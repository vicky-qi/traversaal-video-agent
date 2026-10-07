"""Generate the voiceover for every scene and write exact timings back to scenes.json.

Usage: python tools/voiceover.py <run_dir> [--only s02]

For each scene it runs TTS one sentence at a time, measures each clip, joins them with
short pauses into runs/<slug>/scenes/<id>/vo.wav, and records per-line start/end times.
Sentences whose text has not changed are not re-generated.
Visuals are timed to these measured times, never the other way around.
Exit code 2 (LENGTH LONG/SHORT) means the total is more than 15% off the brief's target.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEAD_IN_S = 0.5   # silence before the voice starts in each scene
TAIL_S = 0.8      # hold after the voice ends
TOLERANCE = 0.15  # total length may be this far off brief.target_duration_s

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1]).resolve()
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
spec_path = run / "scenes.json"
spec = json.loads(spec_path.read_text())
voice = spec["voice"]
pause = voice.get("pause_between_sentences_s", 0.35)


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


for scene in spec["scenes"]:
    sid = scene["scene_id"]
    if only and sid != only:
        continue
    scene_dir = run / "scenes" / sid
    parts_dir = scene_dir / "vo"
    parts_dir.mkdir(parents=True, exist_ok=True)
    if not (scene_dir / "hyperframes.json").exists():
        shutil.copy(REPO / "templates" / "hyperframes.json", scene_dir / "hyperframes.json")

    silence = parts_dir / "pause.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", str(pause), str(silence)], check=True)

    parts, lines, t = [], [], 0.0
    for line in scene["narration"]:
        key = f"{voice['voice_id']}|{voice['speed']}|{line['text']}"
        wav = parts_dir / f"{line['id']}-{hashlib.sha1(key.encode()).hexdigest()[:8]}.wav"
        if not wav.exists():
            for old in parts_dir.glob(f"{line['id']}-*.wav"):
                old.unlink()
            subprocess.run(["npx", "hyperframes", "tts", line["text"], "-o", str(wav),
                            "-v", voice["voice_id"], "-s", str(voice["speed"])],
                           check=True, capture_output=True)
        d = duration(wav)
        lines.append({"id": line["id"], "start": round(t, 3), "end": round(t + d, 3)})
        parts += [wav, silence]
        t += d + pause

    concat_list = parts_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.name}'\n" for p in parts[:-1]))
    track = scene_dir / "vo.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-ar", "48000", str(track)], check=True)

    audio_s = round(duration(track), 3)
    scene["audio"] = str(track.relative_to(run))
    scene["timing"] = {
        "vo_offset_s": LEAD_IN_S,
        "audio_duration_s": audio_s,
        "scene_duration_s": round(LEAD_IN_S + audio_s + TAIL_S, 2),
        "lines": lines,
    }
    print(f"{sid}: voice {audio_s}s, scene {scene['timing']['scene_duration_s']}s "
          f"(target {scene['target_duration_s']}s)")

spec_path.write_text(json.dumps(spec, indent=2) + "\n")
total = sum(s["timing"]["scene_duration_s"] for s in spec["scenes"] if s.get("timing"))

# Length gate: the measured audio, not the word-count estimate, decides if the script fits.
brief_path = run / "brief.json"
target = json.loads(brief_path.read_text()).get("target_duration_s") if brief_path.exists() else None
if not target:
    print(f"total: {total:.1f}s")
    sys.exit(0)
off = (total - target) / target
print(f"total: {total:.1f}s vs target {target}s ({off:+.0%})")
if abs(off) <= TOLERANCE:
    print("LENGTH OK")
    sys.exit(0)
print(f"LENGTH {'LONG' if off > 0 else 'SHORT'}: per-line seconds for the scriptwriter:")
for scene in spec["scenes"]:
    for t in scene["timing"]["lines"]:
        print(f"  {scene['scene_id']}/{t['id']}: {t['end'] - t['start']:.1f}s")
sys.exit(2)
