"""Generate the voiceover for every scene and write exact timings back to scenes.json.

Usage: python tools/voiceover.py <run_dir> [--only s02] [--workers 4]

For each scene it:
  1. rewrites each sentence into speakable text (tools/speech_text.py; captions keep the original),
  2. runs TTS one sentence at a time (in parallel across sentences), caching unchanged sentences,
  3. measures each clip, joins them with short pauses, and normalizes loudness to -16 LUFS
     so every scene sounds equally loud,
  4. writes runs/<slug>/scenes/<id>/vo.wav and per-line start/end times into scenes.json.
Visuals are timed to these measured times, never the other way around.
Exit code 2 (LENGTH LONG/SHORT) means the total is more than 15% off the brief's target.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from speech_text import load_lexicon, to_speech  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LEAD_IN_S = 0.5   # silence before the voice starts in each scene
TAIL_S = 0.8      # hold after the voice ends
TOLERANCE = 0.15  # total length may be this far off brief.target_duration_s
LOUDNESS = "I=-16:TP=-1.5:LRA=11"  # integrated loudness target, true-peak ceiling, loudness range

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1]).resolve()
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
spec_path = run / "scenes.json"
spec = json.loads(spec_path.read_text())
voice = spec["voice"]
pause = voice.get("pause_between_sentences_s", 0.35)
lexicon = load_lexicon(run)


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def tts(job):
    text, wav = job
    res = subprocess.run(["npx", "hyperframes", "tts", text, "-o", str(wav),
                          "-v", voice["voice_id"], "-s", str(voice["speed"])],
                         capture_output=True, text=True)
    if res.returncode != 0 or not wav.exists():
        raise RuntimeError(f"TTS failed for {wav.name}: {(res.stdout + res.stderr)[-500:]}")


def normalize_loudness(src, dst):
    """Two-pass EBU R128 loudness normalization (linear, so it never changes timing)."""
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                            f"loudnorm={LOUDNESS}:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, check=True)
    m = json.loads(probe.stderr[probe.stderr.rindex("{"):probe.stderr.rindex("}") + 1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"loudnorm={LOUDNESS}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
                    f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
                    f":offset={m['target_offset']}", "-ar", "48000", str(dst)], check=True)


# 1. Work out every sentence's speakable text and cache file; collect the ones to generate.
scenes = [s for s in spec["scenes"] if not only or s["scene_id"] == only]
plan, jobs = {}, []
for scene in scenes:
    sid = scene["scene_id"]
    parts_dir = run / "scenes" / sid / "vo"
    parts_dir.mkdir(parents=True, exist_ok=True)
    for line in scene["narration"]:
        spoken, warnings = to_speech(line["text"], lexicon)
        for w in warnings:
            print(f"WARN {sid}/{line['id']}: {w}")
        key = f"{voice['voice_id']}|{voice['speed']}|{spoken}"
        wav = parts_dir / f"{line['id']}-{hashlib.sha1(key.encode()).hexdigest()[:8]}.wav"
        plan[(sid, line["id"])] = (spoken, wav)
        if not wav.exists():
            for old in parts_dir.glob(f"{line['id']}-*.wav"):
                old.unlink()
            jobs.append((spoken, wav))

# 2. Generate missing sentences in parallel.
cached = len(plan) - len(jobs)
print(f"TTS: {len(jobs)} sentences to generate, {cached} cached")
with ThreadPoolExecutor(max_workers=workers) as pool:
    list(pool.map(tts, jobs))

# 3. Assemble, normalize and time each scene.
for scene in scenes:
    sid = scene["scene_id"]
    scene_dir = run / "scenes" / sid
    parts_dir = scene_dir / "vo"
    if not (scene_dir / "hyperframes.json").exists():
        shutil.copy(REPO / "templates" / "hyperframes.json", scene_dir / "hyperframes.json")

    silence = parts_dir / "pause.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", str(pause), str(silence)], check=True)

    parts, lines, t = [], [], 0.0
    for line in scene["narration"]:
        spoken, wav = plan[(sid, line["id"])]
        d = duration(wav)
        entry = {"id": line["id"], "start": round(t, 3), "end": round(t + d, 3)}
        if spoken != line["text"]:
            entry["spoken_as"] = spoken
        lines.append(entry)
        parts += [wav, silence]
        t += d + pause

    concat_list = parts_dir / "concat.txt"
    concat_list.write_text("".join(f"file '{p.name}'\n" for p in parts[:-1]))
    raw = parts_dir / "joined.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-ar", "48000", str(raw)], check=True)
    track = scene_dir / "vo.wav"
    normalize_loudness(raw, track)

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

# 4. Length gate: the measured audio, not the word-count estimate, decides if the script fits.
brief_path = run / "brief.json"
target = json.loads(brief_path.read_text()).get("target_duration_s") if brief_path.exists() else None
if not target or only:
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
