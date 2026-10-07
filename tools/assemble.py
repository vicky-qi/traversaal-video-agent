"""Check, render and stitch every scene of a run into one MP4.

Usage:
  python tools/assemble.py <run_dir> --check-only      # run `hyperframes check` on each scene
  python tools/assemble.py <run_dir> [--only s02]      # check + render (one scene or all) + stitch

Output: runs/<slug>/renders/<id>.mp4 per scene and runs/<slug>/<slug>.mp4 for the full video.
Exit code 1 if any scene fails its check, fails to render, or comes out the wrong length.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1]).resolve()
check_only = "--check-only" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
spec = json.loads((run / "scenes.json").read_text())
renders = run / "renders"
renders.mkdir(exist_ok=True)


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def hf(*args):
    return subprocess.run(["npx", "hyperframes", *args], capture_output=True, text=True)


failed = []
for scene in spec["scenes"]:
    sid = scene["scene_id"]
    if only and sid != only:
        continue
    scene_dir = run / "scenes" / sid
    if not (scene_dir / "index.html").exists():
        failed.append(f"{sid}: no index.html")
        continue

    res = hf("check", str(scene_dir))
    if res.returncode != 0:
        tail = "\n".join((res.stdout + res.stderr).strip().splitlines()[-25:])
        failed.append(f"{sid}: check failed\n{tail}")
        continue
    print(f"{sid}: check passed")
    if check_only:
        continue

    out = renders / f"{sid}.mp4"
    t0 = time.time()
    res = hf("render", str(scene_dir), "-o", str(out), "-q", "delivery", "--quiet")
    if res.returncode != 0 or not out.exists():
        failed.append(f"{sid}: render failed\n{(res.stdout + res.stderr)[-1500:]}")
        continue
    got, want = duration(out), scene["timing"]["scene_duration_s"]
    print(f"{sid}: rendered {got:.2f}s (expected {want}s) in {time.time() - t0:.0f}s")
    if abs(got - want) > 0.2:
        failed.append(f"{sid}: rendered {got:.2f}s but scene_duration_s is {want}; "
                      "check the root data-duration")

if failed:
    print("\n".join("FAIL " + f for f in failed))
    sys.exit(1)
if check_only:
    print("PASS")
    sys.exit(0)

clips = [renders / f"{s['scene_id']}.mp4" for s in spec["scenes"]]
missing = [c.name for c in clips if not c.exists()]
if missing:
    sys.exit(f"cannot stitch, missing renders: {missing}")

final = run / f"{run.name}.mp4"
inputs = sum((["-i", str(c)] for c in clips), [])
streams = "".join(f"[{i}:v][{i}:a]" for i in range(len(clips)))
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", *inputs,
     "-filter_complex", f"{streams}concat=n={len(clips)}:v=1:a=1[v][a]",
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)],
    check=True,
)
expected = sum(s["timing"]["scene_duration_s"] for s in spec["scenes"])
print(f"final: {final.relative_to(run.parent.parent)} {duration(final):.2f}s (expected {expected:.2f}s)")
print("PASS")
