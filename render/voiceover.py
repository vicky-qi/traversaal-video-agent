"""Voiceover stage: turn runs/<slug>/04_script.json into one audio file per scene.

Usage (from the repo root):
    render/env.sh python render/voiceover.py runs/<slug> [--voice af_heart] [--speed 0.85]

For each scene it speaks the narration one sentence at a time with HyperFrames' local
text-to-speech (Kokoro, free, runs on the Mac), measures each sentence, and joins them
with short pauses into runs/<slug>/audio/scene_NN.wav. Sentence start and end times go
to runs/<slug>/audio/timing.json so captions match the voice exactly. Sentences whose
text has not changed are not spoken again.

The measured audio length is the scene length. Exit code 2 means the total is more than
15% away from the script's target (the sum of duration_sec), so the script needs trimming
or padding. Approach based on Jiaxin's tools/voiceover.py.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HF = ["npx", "--yes", "hyperframes@0.8.140"]
LEAD_IN_S = 0.4   # silence before the voice starts
PAUSE_S = 0.3     # silence between sentences
TAIL_S = 0.6      # silence after the voice ends
RATE = 48000
TOLERANCE = 0.15


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def silence(path, seconds):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=mono",
                    "-t", f"{seconds:.3f}", str(path)], check=True)


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=0.85)
    args = ap.parse_args()

    run = Path(args.run_dir).resolve()
    script = json.loads((run / "04_script.json").read_text())
    audio_dir = run / "audio"
    parts_dir = audio_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    lead, pause, tail = parts_dir / "lead.wav", parts_dir / "pause.wav", parts_dir / "tail.wav"
    silence(lead, LEAD_IN_S); silence(pause, PAUSE_S); silence(tail, TAIL_S)

    timing = {"voice": args.voice, "speed": args.speed, "scenes": {}}
    target_total = 0.0
    for scene in script["scenes"]:
        name = f"scene_{int(scene['id']):02d}"
        target_total += float(scene.get("duration_sec", 0))
        files, lines, t = [lead], [], LEAD_IN_S
        for i, text in enumerate(sentences(scene["narration"])):
            key = hashlib.sha1(f"{args.voice}|{args.speed}|{text}".encode()).hexdigest()[:10]
            raw, wav = parts_dir / f"{name}-{i:02d}-{key}.raw.wav", parts_dir / f"{name}-{i:02d}-{key}.wav"
            if not wav.exists():
                subprocess.run(HF + ["tts", text, "-o", str(raw), "-v", args.voice, "-s", str(args.speed)],
                               check=True, capture_output=True)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ar", str(RATE), "-ac", "1", str(wav)], check=True)
                raw.unlink()
            d = duration(wav)
            lines.append({"text": text, "start": round(t, 3), "end": round(t + d, 3)})
            files += [wav, pause]
            t += d + PAUSE_S
        files[-1] = tail
        concat = parts_dir / f"{name}.txt"
        concat.write_text("".join(f"file '{f.name}'\n" for f in files))
        out = audio_dir / f"{name}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                        "-c:a", "pcm_s16le", str(out)], check=True)
        d = round(duration(out), 3)
        timing["scenes"][name] = {"audio_file": str(out.relative_to(run.parent.parent)), "duration": d, "lines": lines}
        print(f"{name}: {d:.1f}s (target {scene.get('duration_sec')}s), {len(lines)} sentences")

    (audio_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")
    total = sum(s["duration"] for s in timing["scenes"].values())
    off = (total - target_total) / target_total if target_total else 0
    print(f"total: {total:.1f}s vs script target {target_total:.0f}s ({off:+.0%})")
    if abs(off) > TOLERANCE:
        print(f"LENGTH {'LONG' if off > 0 else 'SHORT'}: ask the script writer to adjust; per-scene lengths are above.")
        sys.exit(2)
    print("LENGTH OK")


if __name__ == "__main__":
    main()
