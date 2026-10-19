"""Check runs/<slug>/05_storyboard.json against docs/storyboard-format.md and the cinematic targets.

Usage: python3 .claude/skills/make-video/check_storyboard.py runs/<topic-slug>

Needs 04_script.json, audio/timing.json (shot lengths come from the real voiceover) and
03_checked.md (fact IDs must be verified). Prints every problem, then the film's numbers
(shots per minute, camera movement, on-screen text), and exits 1 if anything fails.
"""
import json
import re
import sys
from pathlib import Path

CAMERAS = {"push_in", "pull_out", "pan_left", "pan_right", "pan_up", "pan_down", "orbit", "parallax", "static"}
TRANSITIONS = {"cut", "fade", "zoom_through", "wipe", "match_cut"}
SOUNDS = {"none", "whoosh", "hit", "rise", "chime"}
MOODS = {"calm", "curious", "tense", "uplifting"}
SHOT_FIELDS = {"n", "sentence", "offset", "frame", "camera", "text", "data", "sound", "facts"}
MIN_SHOT, MAX_SHOT = 2.5, 9.0
MIN_MOTION, MAX_TEXT = 0.70, 0.30


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = Path(sys.argv[1])
    problems = []
    try:
        board = json.loads((run / "05_storyboard.json").read_text())
        script = json.loads((run / "04_script.json").read_text())
        timing = json.loads((run / "audio" / "timing.json").read_text())["scenes"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        sys.exit(f"FAIL: cannot read inputs: {e}")
    checked = (run / "03_checked.md").read_text() if (run / "03_checked.md").exists() else ""
    verified = set(re.findall(r"^- \*\*(Q\d+-F\d+)\*\*", checked, re.M))

    art = board.get("art_direction") or {}
    for f in ("style", "palette", "mood", "hero_visual"):
        if not art.get(f):
            problems.append(f"art_direction.{f} is missing")
    if art.get("palette") and not (3 <= len(art["palette"]) <= 6 and all(re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in art["palette"])):
        problems.append("art_direction.palette needs 3-6 hex colours like #38bdf8")
    if (board.get("music") or {}).get("mood") not in MOODS:
        problems.append(f"music.mood must be one of {sorted(MOODS)}")

    script_ids = [s["id"] for s in script.get("scenes", [])]
    board_ids = [s.get("id") for s in board.get("scenes", [])]
    if board_ids != script_ids:
        problems.append(f"storyboard scene ids {board_ids} do not match the script's {script_ids}")

    shots_all, lengths = [], []
    for si, scene in enumerate(board.get("scenes", [])):
        sid = scene.get("id")
        name = f"scene_{int(sid):02d}" if isinstance(sid, int) else str(sid)
        t = timing.get(name)
        if not t:
            problems.append(f"Scene {sid}: no voiceover timing for {name}; run render/voiceover.py first")
            continue
        lines, dur = t["lines"], t["duration"]
        if scene.get("transition_in") not in TRANSITIONS:
            problems.append(f"Scene {sid}: transition_in must be one of {sorted(TRANSITIONS)}")
        if si == 0 and scene.get("transition_in") != "fade":
            problems.append(f"Scene {sid}: the first scene should use transition_in 'fade'")
        shots = scene.get("shots") or []
        lo = 3 if dur < 30 else 4
        if not lo <= len(shots) <= 8:
            problems.append(f"Scene {sid}: has {len(shots)} shots; needs {lo}-8")
        starts = []
        for k, shot in enumerate(shots, 1):
            tag = f"Scene {sid} shot {shot.get('n', k)}"
            extra = set(shot) - SHOT_FIELDS
            if extra:
                problems.append(f"{tag}: fields not allowed: {sorted(extra)}")
            if shot.get("n") != k:
                problems.append(f"{tag}: n should be {k}")
            s = shot.get("sentence")
            if not isinstance(s, int) or not 0 <= s < len(lines):
                problems.append(f"{tag}: sentence must be 0-{len(lines) - 1}")
                continue
            off = shot.get("offset", 0) or 0
            if not isinstance(off, (int, float)) or off < 0:
                problems.append(f"{tag}: offset must be 0 or more seconds")
                off = 0
            start = 0.0 if k == 1 else lines[s]["start"] + off
            if starts and start <= starts[-1]:
                problems.append(f"{tag}: starts at {start:.1f}s, not after the previous shot")
            starts.append(start)
            if not str(shot.get("frame", "")).strip():
                problems.append(f"{tag}: frame is empty")
            if re.search(r"\b(photo|photograph|footage|logo)\b", str(shot.get("frame", "")), re.I):
                problems.append(f"{tag}: version 1 builds every picture in code; no photos, footage or logos")
            if shot.get("camera") not in CAMERAS:
                problems.append(f"{tag}: camera must be one of {sorted(CAMERAS)}")
            if shot.get("sound", "none") not in SOUNDS:
                problems.append(f"{tag}: sound must be one of {sorted(SOUNDS)}")
            text = shot.get("text")
            if text is not None and (not isinstance(text, str) or len(text.split()) > 10):
                problems.append(f"{tag}: text must be null or 10 words or fewer")
            data = shot.get("data")
            if data is not None:
                if not isinstance(data, dict) or not {"value", "unit", "label", "fact"} <= set(data):
                    problems.append(f"{tag}: data needs value, unit, label and fact")
                elif data["fact"] not in verified:
                    problems.append(f"{tag}: data fact {data['fact']} is not a VERIFIED fact in 03_checked.md")
            for fid in shot.get("facts") or []:
                if fid not in verified:
                    problems.append(f"{tag}: fact {fid} is not a VERIFIED fact in 03_checked.md")
            shots_all.append(shot)
        ends = starts[1:] + [dur]
        for k, (a, b) in enumerate(zip(starts, ends), 1):
            lengths.append(b - a)
            if not MIN_SHOT <= b - a <= MAX_SHOT:
                problems.append(f"Scene {sid} shot {k}: {b - a:.1f}s long; shots must be {MIN_SHOT}-{MAX_SHOT}s")

    n = len(shots_all)
    if n:
        motion = sum(s.get("camera") != "static" for s in shots_all) / n
        text = sum(bool(s.get("text")) or bool(s.get("data")) for s in shots_all) / n
        total = sum(t["duration"] for t in timing.values())
        if motion < MIN_MOTION:
            problems.append(f"camera movement in {motion:.0%} of shots; target is at least {MIN_MOTION:.0%}")
        if text > MAX_TEXT:
            problems.append(f"on-screen text or data in {text:.0%} of shots; target is at most {MAX_TEXT:.0%}")
        print(f"shots: {n} ({n / (total / 60):.1f} per minute), average {sum(lengths) / len(lengths):.1f}s, "
              f"camera movement {motion:.0%}, on-screen text {text:.0%}")
    for p in problems:
        print("FAIL:", p)
    print("OK: storyboard matches docs/storyboard-format.md" if not problems else f"{len(problems)} problem(s) found")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
