"""Generate per-sentence TTS for each scene, join it into one track, and write timings back to scene.json."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
spec_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "scene.json")
spec = json.loads(spec_path.read_text())
voice = spec["voice"]
pause = voice["pause_between_sentences_s"]


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


for scene in spec["scenes"]:
    vo_dir = ROOT / "assets" / "vo" / scene["scene_id"]
    vo_dir.mkdir(parents=True, exist_ok=True)
    silence = vo_dir / "pause.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", str(pause), str(silence)], check=True)

    parts, timing, t = [], [], 0.0
    for line in scene["narration"]:
        wav = vo_dir / f"{line['id']}.wav"
        subprocess.run(["npx", "hyperframes", "tts", line["text"], "-o", str(wav),
                        "-v", voice["voice_id"], "-s", str(voice["speed"])],
                       check=True, capture_output=True)
        d = duration(wav)
        timing.append({"id": line["id"], "start": round(t, 3), "end": round(t + d, 3)})
        parts += [wav, silence]
        t += d + pause

    concat_list = vo_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.name}'\n" for p in parts))
    track = ROOT / "assets" / "vo" / f"{scene['scene_id']}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-ar", "48000", str(track)], check=True)

    scene["audio"] = str(track.relative_to(ROOT))
    scene["timing"] = {"lines": timing, "audio_duration_s": round(duration(track), 3)}
    print(f"{scene['scene_id']}: {scene['timing']['audio_duration_s']}s "
          f"(target {scene['target_duration_s']}s)")

spec_path.write_text(json.dumps(spec, indent=2) + "\n")
