"""Check the generated voiceover of a run for problems you would otherwise only hear.

Usage: python tools/check_voice.py <run_dir>

Per scene: vo.wav exists and matches the timing in scenes.json, loudness is near -16 LUFS,
and there are no long silences inside the narration (a sign TTS dropped words).
Per line: speaking rate is plausible (a far too fast or slow line usually means
a garbled or truncated sentence). Exits 1 on any ERROR.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from speech_text import load_lexicon, to_speech  # noqa: E402

TARGET_LUFS = -16.0
MAX_GAP_S = 1.0          # pauses between sentences are 0.35s
WPM_RANGE = (100, 240)   # normal narration is ~150-180 spoken wpm

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1])
spec = json.loads((run / "scenes.json").read_text())
lexicon = load_lexicon(run)
errors, warnings = [], []


def ffmpeg_stderr(*args):
    return subprocess.run(["ffmpeg", "-hide_banner", *args, "-f", "null", "-"],
                          capture_output=True, text=True).stderr


for scene in spec["scenes"]:
    sid = scene["scene_id"]
    wav = run / "scenes" / sid / "vo.wav"
    timing = scene.get("timing")
    if not wav.exists() or not timing:
        errors.append(f"{sid}: no voiceover; run tools/voiceover.py")
        continue

    out = ffmpeg_stderr("-i", str(wav), "-af", "loudnorm=print_format=json")
    lufs = float(json.loads(out[out.rindex("{"):out.rindex("}") + 1])["input_i"])
    if abs(lufs - TARGET_LUFS) > 1.0:
        errors.append(f"{sid}: loudness {lufs:.1f} LUFS, expected {TARGET_LUFS}")

    out = ffmpeg_stderr("-i", str(wav), "-af", f"silencedetect=n=-45dB:d={MAX_GAP_S}")
    for start, dur in re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_duration: ([\d.]+)", out):
        errors.append(f"{sid}: {float(dur):.1f}s silence at {float(start):.1f}s; a sentence may be missing words")

    by_id = {l["id"]: l for l in scene["narration"]}
    for t in timing["lines"]:
        spoken, _ = to_speech(by_id[t["id"]]["text"], lexicon)
        words = len([w for w in re.split(r"[\s\-]+", spoken) if re.search(r"\w", w)])
        secs = t["end"] - t["start"]
        wpm = words / secs * 60 if secs > 0 else 0
        msg = f"{sid}/{t['id']}: {wpm:.0f} spoken wpm ({words} words in {secs:.1f}s)"
        if not WPM_RANGE[0] <= wpm <= WPM_RANGE[1]:
            errors.append(msg + "; regenerate or reword this line")
    print(f"{sid}: {lufs:.1f} LUFS, {len(timing['lines'])} lines, {timing['audio_duration_s']}s")

for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
