"""Render stage: turn the scene files into runs/<slug>/final.mp4.

Usage (from the repo root):
    render/env.sh python render/render.py runs/<slug> [--scene 3] [--draft] [--no-check]

Reads runs/<slug>/scenes/index.json and scene_NN.json (written by the scene-builder agent),
plus runs/<slug>/audio/timing.json (written by render/voiceover.py). For each scene it fills
templates/base.html with templates/<visual_type>.js, runs `hyperframes check`, renders the
scene to MP4, then joins all scenes into final.mp4.

  --scene N    re-render only scene N, then join again
  --draft      faster, lower-quality render for previews
  --no-check   skip `hyperframes check` (not recommended)
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"
HF = ["npx", "--yes", "hyperframes@0.8.140"]


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def source_line(scene):
    vc = scene.get("visual_content") or {}
    if scene.get("visual_type") == "chart" and vc.get("source_note"):
        return "Source: " + vc["source_note"]
    hosts = []
    for s in scene.get("sources") or []:
        host = urlparse(s).netloc.lower().removeprefix("www.") if "://" in s else ""
        if host and host != "example.com" and host not in hosts:
            hosts.append(host)
    if not hosts:
        return ""
    return ("Source: " if len(hosts) == 1 else "Sources: ") + " · ".join(hosts[:3])


def build_scene(run, scene, timing, topic, out_dir):
    vtype = scene["layout"]["template"] if scene.get("layout") else scene["visual_type"]
    type_js = TEMPLATES / f"{vtype}.js"
    if not type_js.exists():
        sys.exit(f"{scene['id']}: no template for visual_type '{vtype}'")
    dur = float(scene["final_duration_sec"])
    if abs(dur - timing["duration"]) > 0.1:
        print(f"  warning: {scene['id']} scene file says {dur}s but the audio measures {timing['duration']}s; using the audio")
        dur = timing["duration"]
    data = {
        "topic": topic,
        "title": scene["title"],
        "visual_type": vtype,
        "visual_content": scene.get("visual_content") or {},
        "lines": timing["lines"],
        "duration": dur,
        "source_line": source_line(scene),
    }
    html = (TEMPLATES / "base.html").read_text()
    html = html.replace("__DURATION__", f"{dur:.3f}")
    html = html.replace("__SCENE_JSON__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("__TYPE_SCRIPT__", type_js.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html)
    shutil.copy(TEMPLATES / "hyperframes.json", out_dir / "hyperframes.json")
    audio = REPO / scene["audio_file"]
    if not audio.exists():
        audio = run / "audio" / Path(scene["audio_file"]).name
    shutil.copy(audio, out_dir / "vo.wav")
    return dur


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--scene", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args()

    run = Path(args.run_dir).resolve()
    index = json.loads((run / "scenes" / "index.json").read_text())
    if index.get("status") != "complete":
        sys.exit(f"scenes/index.json status is '{index.get('status')}', not 'complete'. Problems: {index.get('problems')}")
    timing = json.loads((run / "audio" / "timing.json").read_text())["scenes"]
    topic = json.loads((run / "04_script.json").read_text()).get("topic", "")
    build = run / "build"

    clips = []
    for entry in index["scenes"]:
        scene_file = REPO / entry["scene_file"]
        if not scene_file.exists():
            scene_file = run / "scenes" / Path(entry["scene_file"]).name
        scene = json.loads(scene_file.read_text())
        name = Path(scene["audio_file"]).stem            # scene_01
        order = int(scene.get("order", re.sub(r"\D", "", name) or 0))
        out_dir = build / name
        clip = build / f"{name}.mp4"
        clips.append(clip)
        if args.scene and order != args.scene:
            continue
        dur = build_scene(run, scene, timing[name], topic, out_dir)
        print(f"{name} ({scene['visual_type']}, {dur:.1f}s)")
        if not args.no_check and not check(out_dir, name):
            sys.exit(f"Fix the template or the scene content for {name}, then run again with --scene {order}.")
        quality = "draft" if args.draft else "standard"
        subprocess.run(HF + ["render", str(out_dir), "-o", str(clip), "--quality", quality, "--quiet"], check=True)
        print(f"  rendered {clip.name}: {duration(clip):.2f}s")

    missing = [c.name for c in clips if not c.exists()]
    if missing:
        sys.exit(f"Missing rendered scenes: {missing}. Render them first.")
    concat = build / "concat.txt"
    concat.write_text("".join(f"file '{c.name}'\n" for c in clips))
    final = run / "final.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], check=True)
    print(f"final.mp4: {duration(final):.1f}s, {len(clips)} scenes -> {final.relative_to(REPO)}")


if __name__ == "__main__":
    main()
