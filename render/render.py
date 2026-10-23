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


def join(clips, run):
    concat = run / "build" / "concat.txt"
    concat.write_text("".join(f"file '{c.name}'\n" for c in clips))
    out = run / "build" / "joined.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--scene", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--no-check", action="store_true")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    run = Path(args.run_dir).resolve()
    timing = json.loads((run / "audio" / "timing.json").read_text())["scenes"]
    topic = json.loads((run / "04_script.json").read_text()).get("topic", "")
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
    mix(run, joined, final, board, timing)
    print(f"final.mp4: {duration(final):.1f}s, {len(clips)} scenes -> {final.relative_to(REPO)}")


if __name__ == "__main__":
    main()
