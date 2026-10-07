"""Update built scenes to the latest measured voiceover timing, without rebuilding them.

Usage: python tools/sync_timing.py <run_dir> [--only s02]

Scenes follow the reference pattern (templates/key_points.html): every time comes from one
`const TIMING = {...};` block, and the root, full-length clips and <audio> carry the scene and
voice durations in data-* attributes. After tools/voiceover.py re-measures a scene, this script
rewrites those values from scenes.json. If a scene has other absolute times it cannot safely
update, it reports the scene so a scene-builder can rebuild it (exit code 1).
"""
import json
import re
import sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1]).resolve()
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
spec = json.loads((run / "scenes.json").read_text())
TIMING_RE = re.compile(r"const TIMING = \{.*?\n\s*\};", re.S)

needs_rebuild = []
for scene in spec["scenes"]:
    sid = scene["scene_id"]
    if only and sid != only:
        continue
    html_path = run / "scenes" / sid / "index.html"
    if not html_path.exists():
        continue
    html = html_path.read_text()
    timing = scene["timing"]

    block = TIMING_RE.search(html)
    old_dur = re.search(r"duration:\s*([\d.]+)", block.group(0)) if block else None
    old_audio = re.search(r'<audio[^>]*data-duration="([\d.]+)"', html)
    if not (block and old_dur and old_audio):
        needs_rebuild.append(f"{sid}: no TIMING block or <audio> duration found")
        continue
    old_dur, old_audio = old_dur.group(1), old_audio.group(1)

    lines = ",\n".join(f'          {{ id: "{l["id"]}", start: {l["start"]}, end: {l["end"]} }}'
                       for l in timing["lines"])
    new_block = ("const TIMING = {\n"
                 f"        offset: {timing['vo_offset_s']},\n"
                 f"        duration: {timing['scene_duration_s']},\n"
                 f"        lines: [\n{lines},\n        ],\n      }};")
    html = TIMING_RE.sub(lambda _: new_block, html, count=1)
    html = re.sub(r'(<audio[^>]*data-duration=")[\d.]+(")', rf"\g<1>{timing['audio_duration_s']}\g<2>", html)
    html = re.sub(r'(<audio[^>]*data-start=")[\d.]+(")', rf"\g<1>{timing['vo_offset_s']}\g<2>", html)
    # Full-length clips (root, content, captions) carry the old scene duration.
    html = html.replace(f'data-duration="{old_dur}"', f'data-duration="{timing["scene_duration_s"]}"')

    # Any other timed element with a non-zero start is an absolute time we cannot re-derive.
    stray = [m.group(0) for m in re.finditer(r'data-start="([\d.]+)"', html)
             if float(m.group(1)) not in (0.0, float(timing["vo_offset_s"]))]
    if stray:
        needs_rebuild.append(f"{sid}: hand-set clip times {stray}; rebuild with scene-builder")
        continue
    html_path.write_text(html)
    print(f"{sid}: synced (scene {old_dur}s -> {timing['scene_duration_s']}s, "
          f"voice {old_audio}s -> {timing['audio_duration_s']}s)")

for n in needs_rebuild:
    print("REBUILD", n)
sys.exit(1 if needs_rebuild else 0)
