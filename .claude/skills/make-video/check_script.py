"""Check a 04_script.json against docs/scene-format.md.

Each scene has exactly: id, title, act, narration, duration_sec, sources.

Usage: python3 .claude/skills/make-video/check_script.py runs/<topic-slug>/04_script.json [--minutes 7]
       python3 .claude/skills/make-video/check_script.py --example examples/snow-white/04_script.json
--example skips the scene-count and total-word checks, for short format examples.
--minutes sets the target film length (default 7): it decides the allowed scene count and total words.
Prints every problem found and exits with code 1 if there are any.
"""
import json
import sys

WORDS_PER_SEC = 2.4  # 145 words per minute
TOLERANCE = 0.15
FIELDS = ("id", "title", "act", "narration", "duration_sec", "sources")
BAD_IN_NARRATION = ("http", "*", "#", "[", "]", "%", "$")

def words(text):
    return len(text.split())


def targets(minutes):
    """Allowed scene count and total words for a film of `minutes` minutes."""
    seconds = minutes * 60
    if minutes >= 6:
        scenes = (10, 15)
    else:
        scenes = (max(2, int(seconds // 45)), max(3, -(-int(seconds) // 30)))
    words = seconds * WORDS_PER_SEC
    return scenes, (round(words * 0.9), round(words * 1.1))


def check(path, example=False, minutes=7):
    try:
        with open(path) as f:
            script = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"Cannot read {path}: {e}"]

    problems = []
    for field in ("topic", "total_words", "scenes"):
        if field not in script:
            problems.append(f"Missing top-level field: {field}")
    scenes = script.get("scenes", [])
    (lo, hi), (wlo, whi) = targets(minutes)
    if not example and not lo <= len(scenes) <= hi:
        problems.append(f"Has {len(scenes)} scenes; needs {lo}-{hi} for a {minutes}-minute film")

    total = 0
    for i, scene in enumerate(scenes, 1):
        n = scene.get("id", f"#{i}")
        if scene.get("id") != i:
            problems.append(f"Scene {i}: id is {scene.get('id')!r}; ids must be integers 1, 2, 3...")
        for field in FIELDS:
            if field not in scene:
                problems.append(f"Scene {n}: missing {field}")
        for field in scene:
            if field not in FIELDS:
                problems.append(f"Scene {n}: field {field} is not allowed")
        if scene.get("act") not in (1, 2, 3):
            problems.append(f"Scene {n}: act must be 1, 2 or 3")

        narration = scene.get("narration", "")
        total += words(narration)
        for bad in BAD_IN_NARRATION:
            if bad in narration:
                problems.append(f"Scene {n}: narration contains {bad!r}, which the voice would misread")

        duration = scene.get("duration_sec")
        if not isinstance(duration, int) or not 30 <= duration <= 45:
            problems.append(f"Scene {n}: duration_sec must be a whole number from 30 to 45")
        else:
            target = duration * WORDS_PER_SEC
            if abs(words(narration) / target - 1) > TOLERANCE:
                problems.append(f"Scene {n}: {words(narration)} words; target is about {target:.0f} for {duration}s")

        sources = scene.get("sources", [])
        if not isinstance(sources, list) or not all(isinstance(s, str) and s.startswith("http") for s in sources):
            problems.append(f"Scene {n}: sources must be a list of full URLs")

    if script.get("total_words") != total:
        problems.append(f"total_words says {script.get('total_words')}, real count is {total}")
    if not example and not wlo <= total <= whi:
        problems.append(f"Total narration is {total} words; needs {wlo}-{whi} for a {minutes}-minute film")
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    example = "--example" in args
    args = [a for a in args if a != "--example"]
    minutes = 7.0
    if "--minutes" in args:
        i = args.index("--minutes")
        minutes = float(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    problems = check(args[0], example, minutes)
    for p in problems:
        print("FAIL:", p)
    print("OK: script matches docs/scene-format.md" if not problems else f"{len(problems)} problem(s) found")
    sys.exit(1 if problems else 0)
