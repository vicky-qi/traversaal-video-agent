"""Check a 04_script.json against docs/scene-format.md.

Usage: python3 .claude/skills/make-video/check_script.py runs/<topic-slug>/04_script.json
       python3 .claude/skills/make-video/check_script.py --example docs/example-script.json
--example skips the scene-count and total-word checks, for short format examples.
Prints every problem found and exits with code 1 if there are any.
"""
import json
import sys

WORDS_PER_SEC = 2.4  # 145 words per minute
TOLERANCE = 0.15
SCENE_FIELDS = ("id", "title", "narration", "duration_sec", "visual_type", "visual_content", "sources")
BAD_IN_NARRATION = ("http", "*", "#", "[", "]", "%", "$")

VISUAL_FIELDS = {
    # visual_type: {field: (required, max_words or None)}
    "title": {"headline": (True, 8), "subheadline": (False, 12), "background_description": (False, 25)},
    "bullets": {"heading": (False, 8), "bullets": (True, None)},
    "image": {"image_description": (True, 25), "caption": (False, 12), "image_path": (False, None)},
    "chart": {"chart_type": (True, None), "chart_title": (True, 10), "labels": (True, None),
              "values": (True, None), "unit": (True, None), "source_note": (True, None)},
    "quote": {"quote_text": (True, 30), "attribution": (True, None)},
}


def words(text):
    return len(text.split())


def check_visual(n, vtype, vc, problems):
    spec = VISUAL_FIELDS[vtype]
    for field, (required, max_words) in spec.items():
        if field not in vc:
            if required:
                problems.append(f"Scene {n}: {vtype} needs visual_content.{field}")
            continue
        if max_words and words(str(vc[field])) > max_words:
            problems.append(f"Scene {n}: visual_content.{field} is over {max_words} words")
    for field in vc:
        if field not in spec:
            problems.append(f"Scene {n}: field visual_content.{field} is not allowed for {vtype}")
    for field, value in vc.items():
        if field != "image_path" and isinstance(value, str) and "http" in value:
            problems.append(f"Scene {n}: visual_content.{field} must not contain a URL")

    if vtype == "bullets" and "bullets" in vc:
        items = vc["bullets"]
        if not isinstance(items, list) or not 2 <= len(items) <= 5:
            problems.append(f"Scene {n}: bullets needs 2-5 items")
        else:
            for item in items:
                if words(item) > 12:
                    problems.append(f"Scene {n}: bullet over 12 words: {item!r}")
    if vtype == "image" and vc.get("image_path") is not None:
        problems.append(f"Scene {n}: image_path must be null in the script")
    if vtype == "chart":
        if vc.get("chart_type") not in ("bar", "line", "pie"):
            problems.append(f"Scene {n}: chart_type must be 'bar', 'line' or 'pie'")
        labels, values = vc.get("labels", []), vc.get("values", [])
        if not 2 <= len(labels) <= 8:
            problems.append(f"Scene {n}: chart needs 2-8 labels")
        if not all(isinstance(label, str) for label in labels):
            problems.append(f"Scene {n}: chart labels must be strings (write years as \"2015\")")
        if len(labels) != len(values):
            problems.append(f"Scene {n}: chart labels and values differ in length")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            problems.append(f"Scene {n}: chart values must be numbers")


def check(path, example=False):
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
    if not example and not 10 <= len(scenes) <= 15:
        problems.append(f"Has {len(scenes)} scenes; needs 10-15")

    total = 0
    for i, scene in enumerate(scenes, 1):
        n = scene.get("id", f"#{i}")
        if scene.get("id") != i:
            problems.append(f"Scene {i}: id is {scene.get('id')!r}; ids must be integers 1, 2, 3...")
        for field in SCENE_FIELDS:
            if field not in scene:
                problems.append(f"Scene {n}: missing {field}")
        for field in scene:
            if field not in SCENE_FIELDS:
                problems.append(f"Scene {n}: field {field} is not allowed")

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

        vtype = scene.get("visual_type")
        if vtype not in VISUAL_FIELDS:
            problems.append(f"Scene {n}: visual_type {vtype!r} is not one of {', '.join(VISUAL_FIELDS)}")
        elif isinstance(scene.get("visual_content"), dict):
            check_visual(n, vtype, scene["visual_content"], problems)
        else:
            problems.append(f"Scene {n}: visual_content must be an object")

        sources = scene.get("sources", [])
        if not isinstance(sources, list) or not all(isinstance(s, str) and s.startswith("http") for s in sources):
            problems.append(f"Scene {n}: sources must be a list of full URLs")

    if script.get("total_words") != total:
        problems.append(f"total_words says {script.get('total_words')}, real count is {total}")
    if not example and not 950 <= total <= 1100:
        problems.append(f"Total narration is {total} words; needs 950-1,100")
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    example = "--example" in args
    args = [a for a in args if a != "--example"]
    if len(args) != 1:
        sys.exit(__doc__)
    problems = check(args[0], example)
    for p in problems:
        print("FAIL:", p)
    print("OK: script matches docs/scene-format.md" if not problems else f"{len(problems)} problem(s) found")
    sys.exit(1 if problems else 0)
