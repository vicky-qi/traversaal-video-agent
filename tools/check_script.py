"""Validate runs/<slug>/scenes.json before voiceover: structure, claim links, and estimated timing.

Usage: python tools/check_script.py <run_dir>
Also fills each scene's "sources" from the facts its lines cite.
Exits 1 if there are errors (warnings alone pass).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from speech_text import load_lexicon, to_speech  # noqa: E402


# Kokoro rate in spoken words, counted on the text the voice actually reads (tools/speech_text.py:
# "2025" -> "twenty twenty-five", "ROI" -> "R-O-I"). Measured: ~152 wpm at speed 0.9 for
# fact-heavy narration, ~179 for plain prose. This is only an estimate; the measured
# voiceover (tools/voiceover.py) decides final length.
WPM_AT_SPEED_1 = 172
MAX_WORDS_PER_LINE = 40
VISUAL_TYPES = {"title", "key_points", "stat", "quote", "chart", "comparison", "timeline"}

if len(sys.argv) < 2:
    sys.exit(__doc__)
run = Path(sys.argv[1])
spec = json.loads((run / "scenes.json").read_text())
brief = json.loads((run / "brief.json").read_text())

facts = {}
for f in sorted((run / "research").glob("*.json")):
    for fact in json.loads(f.read_text()).get("facts", []):
        facts[fact["id"]] = fact



LEXICON = load_lexicon(run)


def spoken_words(text):
    spoken, _ = to_speech(text, LEXICON)
    return len([w for w in re.split(r"[\s\-]+", spoken) if re.search(r"\w", w)])


errors, warnings = [], []
voice = spec.get("voice", {})
speed = voice.get("speed", 1.0)
pause = voice.get("pause_between_sentences_s", 0.35)
wpm = WPM_AT_SPEED_1 * speed

scenes = spec.get("scenes", [])
if not scenes:
    errors.append("no scenes")
if len(scenes) != brief.get("scene_count", len(scenes)):
    warnings.append(f"{len(scenes)} scenes, brief asked for {brief['scene_count']}")

total_est = 0.0
for i, scene in enumerate(scenes, 1):
    sid = scene.get("scene_id", f"#{i}")
    if sid != f"s{i:02d}":
        errors.append(f"{sid}: scene_id should be s{i:02d}")
    for key in ("title", "visual_type", "target_duration_s", "narration"):
        if key not in scene:
            errors.append(f"{sid}: missing {key}")
    if scene.get("visual_type") not in VISUAL_TYPES:
        errors.append(f"{sid}: visual_type {scene.get('visual_type')!r} not in {sorted(VISUAL_TYPES)}")

    words, sources = 0, []
    for line in scene.get("narration", []):
        lid = f"{sid}/{line.get('id')}"
        n = len(line.get("text", "").split())
        words += spoken_words(line.get("text", ""))
        if n == 0:
            errors.append(f"{lid}: empty text")
        elif n > MAX_WORDS_PER_LINE:
            warnings.append(f"{lid}: {n} words; split long sentences for natural TTS")
        if "claims" not in line:
            errors.append(f"{lid}: missing claims (use [] for lines with no factual claim)")
        for fid in line.get("claims", []):
            if fid not in facts:
                errors.append(f"{lid}: cites unknown fact {fid}")
            elif facts[fid]["source_url"] not in sources:
                sources.append(facts[fid]["source_url"])
    scene["sources"] = sources

    lines = len(scene.get("narration", []))
    est = words / wpm * 60 + pause * lines + 1.3  # 1.3s = scene lead-in + tail
    total_est += est
    target = scene.get("target_duration_s") or est
    off = (est - target) / target
    msg = f"{sid}: {words} spoken words, est {est:.1f}s vs target {target}s ({off:+.0%})"
    if abs(off) > 0.35:
        errors.append(msg)
    elif abs(off) > 0.2:
        warnings.append(msg)
    print(msg)

target_total = brief.get("target_duration_s")
if target_total:
    off = (total_est - target_total) / target_total
    msg = f"total est {total_est:.1f}s vs brief target {target_total}s ({off:+.0%})"
    print(msg)
    if abs(off) > 0.15:
        errors.append(msg)

(run / "scenes.json").write_text(json.dumps(spec, indent=2) + "\n")
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("PASS" if not errors else "FAIL")
sys.exit(1 if errors else 0)
