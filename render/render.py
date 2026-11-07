"""Render stage: turn a run into runs/<slug>/final.mp4.

Usage (from the repo root):
    render/env.sh python render/render.py runs/<slug> [--scene 3] [--draft] [--no-check] [--check-only]

For each scene it puts the scene builder's runs/<slug>/scenes/scene_NN/scene.html into
templates/film/shell.html with the storyboard's shot timing, runs `hyperframes check`, renders
it, joins all scenes, then mixes in a music bed and sound effects (render/sound.py).

  --scene N     build/check/render only scene N, then join again if every scene is rendered
  --check-only  build and check only (with --scene: one scene); no rendering. Scene builders use this.
  --draft       faster, lower-quality render for previews
  --no-check    skip `hyperframes check` (not recommended)
  --no-music    voice and sound effects only, no music bed
  --min-seconds N  the finished film must be at least N seconds (420 for a 7-minute film); a shorter
                film is kept as final.too-short.mp4 and the script exits with code 3

It refuses to start if audio/timing.json no longer matches the script's sentences (re-run voiceover.py).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"
HF = ["npx", "--yes", "hyperframes@0.8.140"]


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def check(out_dir, name):
    res = subprocess.run(HF + ["check", str(out_dir), "--json"], capture_output=True, text=True)
    try:
        report = json.loads(res.stdout[res.stdout.find("{"):])
    except ValueError:
        report = None
    findings = []
    if isinstance(report, dict):
        for part in ("lint", "runtime", "layout", "motion", "contrast"):
            for f in (report.get(part) or {}).get("findings") or (report.get(part) or {}).get("issues") or []:
                if isinstance(f, dict) and f.get("severity") == "error":
                    findings.append(f"{part}: {f.get('code', '')}: {f.get('message', '')[:300]}")
    ok = res.returncode == 0 and (not isinstance(report, dict) or report.get("ok", True))
    if not ok:
        print(f"  {name}: hyperframes check found errors")
        for f in findings or [(res.stdout or res.stderr)[-2000:]]:
            print("    " + f)
        return False
    print(f"  {name}: check passed")
    return True


def film_shots(board_scene, t):
    """Absolute start/end (seconds within the scene) of every storyboard shot."""
    lines, dur = t["lines"], t["duration"]
    shots = board_scene["shots"]
    starts = [0.0 if k == 0 else lines[sh["sentence"]]["start"] + float(sh.get("offset") or 0)
              for k, sh in enumerate(shots)]
    ends = starts[1:] + [dur]
    return [{"n": sh["n"], "start": round(a, 3), "end": round(b, 3), "camera": sh.get("camera", "static"),
             "text": sh.get("text"), "data": sh.get("data"), "sound": sh.get("sound", "none")}
            for sh, a, b in zip(shots, starts, ends)]


def build_film_scene(run, board, board_scene, t, topic, out_dir):
    name = f"scene_{int(board_scene['id']):02d}"
    fragment = run / "scenes" / name / "scene.html"
    if not fragment.exists():
        sys.exit(f"{name}: missing {fragment.relative_to(REPO)}; run the scene builder for scene {board_scene['id']}")
    data = {
        "topic": topic, "scene_id": board_scene["id"], "duration": t["duration"],
        "transition_in": board_scene.get("transition_in", "cut"),
        "palette": (board.get("art_direction") or {}).get("palette") or [],
        "lines": t["lines"], "shots": film_shots(board_scene, t),
    }
    html = (TEMPLATES / "film" / "shell.html").read_text()
    html = html.replace("__DURATION__", f"{t['duration']:.3f}")
    html = html.replace("__SCENE_JSON__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("__SCENE_FRAGMENT__", fragment.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html)
    shutil.copy(TEMPLATES / "hyperframes.json", out_dir / "hyperframes.json")
    shutil.copy(run / "audio" / f"{name}.wav", out_dir / "vo.wav")
    return t["duration"]


def data_sheet(run, board, timing, final):
    """One frame from every shot that shows a number, tiled into build/data_shots.png, so the
    finished video itself can be checked: is each number complete, readable and uncovered?"""
    offset, picks = 0.0, []
    for bs in board["scenes"]:
        t = timing[f"scene_{int(bs['id']):02d}"]
        for sh in film_shots(bs, t):
            if sh.get("data"):
                # Near the end of the shot, when a counting number has reached its value.
                at = offset + max(sh["start"], sh["end"] - 0.6)
                picks.append((at, f"scene {bs['id']} shot {sh['n']}: {sh['data'].get('value')} {sh['data'].get('unit', '')}"))
        offset += t["duration"]
    if not picks:
        return
    work = run / "build" / "data_shots"
    work.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, (at, _) in enumerate(picks):
        f = work / f"{i + 1:02d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(final), "-frames:v", "1",
                        "-vf", "scale=640:-1", str(f)], check=True)
        frames.append(f)
    cols = 3 if len(frames) > 4 else 2
    rows = -(-len(frames) // cols)
    out = run / "build" / "data_shots.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(work / "%02d.png"),
                    "-vf", f"tile={cols}x{rows}", "-frames:v", "1", str(out)], check=True)
    print(f"data_shots.png: {len(frames)} number shots, left to right, top to bottom:")
    for i, (_, label) in enumerate(picks, 1):
        print(f"  {i}. {label}")


def join(clips, run):
    concat = run / "build" / "concat.txt"
    concat.write_text("".join(f"file '{c.name}'\n" for c in clips))
    out = run / "build" / "joined.mp4"
    # The scene clips share one encoding, so the picture is copied as rendered (no second compression);
    # only the audio is re-encoded, which keeps the joins between scenes click-free.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--scene", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--no-check", action="store_true")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--min-seconds", type=float, default=0)
    args = ap.parse_args()

    run = Path(args.run_dir).resolve()
    timing = json.loads((run / "audio" / "timing.json").read_text())["scenes"]
    script = json.loads((run / "04_script.json").read_text())
    topic = script.get("topic", "")
    # The audio must be the voice of the current script: a sentence edited or deleted after the
    # voiceover would put old words and old timing into the film.
    from voiceover import sentences
    stale = [sc["id"] for sc in script["scenes"]
             if [ln["text"] for ln in (timing.get(f"scene_{int(sc['id']):02d}") or {}).get("lines", [])] != sentences(sc["narration"])]
    if stale:
        sys.exit(f"Audio out of date for scenes {stale}: the script changed after the voiceover. "
                 f"Run render/env.sh python render/voiceover.py {args.run_dir}, update those scenes' shots, then render again.")
    build = run / "build"
    board = json.loads((run / "05_storyboard.json").read_text())
    quality = "draft" if args.draft else "standard"

    jobs = []  # (order, name, builder)
    for bs in board["scenes"]:
        name = f"scene_{int(bs['id']):02d}"
        jobs.append((int(bs["id"]), name, lambda bs=bs, name=name: build_film_scene(run, board, bs, timing[name], topic, build / name)))

    clips, failed = [], []
    for order, name, builder in jobs:
        clip = build / f"{name}.mp4"
        clips.append(clip)
        if args.scene and order != args.scene:
            continue
        dur = builder()
        print(f"{name} ({dur:.1f}s)")
        if not args.no_check and not check(build / name, name):
            failed.append(order)
            if not args.check_only:
                sys.exit(f"Fix scene {order} (see the errors above), then run again with --scene {order}.")
            continue
        if args.check_only:
            continue
        # One scene at a time: HyperFrames already spreads each render over several Chrome workers,
        # and renders running side by side corrupt each other's output.
        subprocess.run(HF + ["render", str(build / name), "-o", str(clip), "--quality", quality, "--quiet"], check=True)
        print(f"  rendered {clip.name}: {duration(clip):.2f}s")

    if args.check_only:
        sys.exit(f"check failed for scenes {failed}" if failed else 0)
    missing = [c.name for c in clips if not c.exists()]
    if missing:
        sys.exit(f"Not joined yet; still to render: {missing}")
    joined = join(clips, run)
    final = run / "final.mp4"
    from sound import mix
    mix(run, joined, final, board, timing, music_on=not args.no_music)
    length = duration(final)
    if length < args.min_seconds:
        short = final.with_name("final.too-short.mp4")
        final.replace(short)
        sys.exit(f"LENGTH SHORT: the film is {length:.1f}s, below the {args.min_seconds:.0f}s minimum. "
                 f"Kept as {short.relative_to(REPO)}; it is not delivered as final.mp4.")
    print(f"final.mp4: {length:.1f}s, {len(clips)} scenes -> {final.relative_to(REPO)}")
    data_sheet(run, board, timing, final)


if __name__ == "__main__":
    main()
