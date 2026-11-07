"""Print everything one scene builder needs about its scene, and nothing else.

Usage: python3 .claude/skills/make-video/scene_brief.py runs/<topic-slug> <scene id>

Prints the film's art direction and music mood, the scene's narration with each sentence's
start and end time, its transition and its storyboard shots, plus the last shot of the scene
before and the first shot of the scene after (so the scene can lead in and out). Reading this
instead of the whole storyboard and script keeps each builder's context small.
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    run, sid = Path(sys.argv[1]), int(sys.argv[2])
    board = json.loads((run / "05_storyboard.json").read_text())
    script = json.loads((run / "04_script.json").read_text())
    timing = json.loads((run / "audio" / "timing.json").read_text())["scenes"]
    scenes = board["scenes"]
    idx = next((i for i, s in enumerate(scenes) if int(s["id"]) == sid), None)
    if idx is None:
        sys.exit(f"No scene {sid} in {run / '05_storyboard.json'}")
    scene = scenes[idx]
    text = next((s for s in script["scenes"] if int(s["id"]) == sid), {})
    t = timing[f"scene_{sid:02d}"]

    out = {
        "topic": board.get("topic") or script.get("topic"),
        "art_direction": board.get("art_direction"),
        "music": board.get("music"),
        "scene": {"id": sid, "title": text.get("title"), "act": text.get("act"),
                  "duration_seconds": t["duration"], "transition_in": scene.get("transition_in")},
        "sentences": [{"i": i, "start": ln["start"], "end": ln["end"], "text": ln["text"]} for i, ln in enumerate(t["lines"])],
        "shots": scene["shots"],
        "previous_scene_last_shot": scenes[idx - 1]["shots"][-1] if idx > 0 else None,
        "next_scene_first_shot": scenes[idx + 1]["shots"][0] if idx + 1 < len(scenes) else None,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
