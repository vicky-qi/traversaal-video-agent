# Storyboard format (`05_storyboard.json`)

Owner: Jiaxin. Part of the cinematic definition (`Video Definition v2: Cinematic Explainer`, Oct 16). The storyboard agent writes it after the voiceover, so every shot can start on a real sentence; the scene builders turn it into HyperFrames scenes. Check it with:

```bash
python3 .claude/skills/make-video/check_storyboard.py runs/<topic-slug>
```

## File

```json
{
  "topic": "How Electric Car Batteries Work",
  "art_direction": {
    "style": "Flat vector illustration with soft gradients and glow, like an animated science documentary",
    "palette": ["#0b1020", "#38bdf8", "#f59e0b", "#e2e8f0"],
    "mood": "Curious and calm, building to a confident payoff",
    "hero_visual": "One glowing battery cell, opened as a cutaway, that the film keeps returning to"
  },
  "music": { "mood": "calm", "key": "A minor" },
  "scenes": [
    {
      "id": 3,
      "transition_in": "zoom_through",
      "shots": [
        {
          "n": 1,
          "sentence": 0,
          "offset": 0,
          "frame": "Low angle under the car: rows of cells glow inside the flat pack in the floor",
          "camera": "push_in",
          "text": null,
          "data": null,
          "sound": "whoosh",
          "facts": ["Q2-F2"]
        }
      ]
    }
  ]
}
```

| Field | Rule |
|---|---|
| `art_direction` | One style for the whole film. `palette`: 3–6 hex colours. `hero_visual`: the recurring image. Copied from the brief's Art direction. |
| `music.mood` | `calm`, `curious`, `tense` or `uplifting`; the render stage makes a matching music bed. |
| `scenes[].id` | The script scene's `id`; every script scene appears once, in order. |
| `transition_in` | How this scene begins: `cut`, `fade`, `zoom_through`, `wipe` or `match_cut`. The first scene uses `fade`. |
| `shots[].n` | 1, 2, 3… within the scene. |
| `shots[].sentence` | Which narration sentence (0 = first, as listed in `audio/timing.json`) the shot starts on. Shots go forward in order. |
| `shots[].offset` | Seconds after that sentence starts (0 or more), to cut inside a long sentence. |
| `shots[].frame` | What is in the frame, concretely enough to build in code: objects, layout, what moves. No photographs in version 1 (see below). |
| `shots[].camera` | `push_in` (move closer), `pull_out` (move back), `pan_left` / `pan_right` / `pan_up` / `pan_down` (the **picture** slides that way, as if the camera turns the other way: `pan_left` reveals what is on the right), `orbit` (slow tilt and drift), `parallax` (layers at different depths slide past each other) or `static` (a slow drift). |
| `shots[].text` | `null`, or on-screen text of 10 words or fewer (a label, a short title, one number with its unit). |
| `shots[].data` | `null`, or a number shown on screen: `{"value": 99, "unit": "dollars per kilowatt-hour", "label": "Battery-electric car packs, 2025, worldwide", "fact": "Q6-F5"}`. The value must match the verified fact exactly. |
| `shots[].sound` | `none`, `whoosh`, `hit`, `rise` or `chime`, played when the shot starts. |
| `shots[].facts` | IDs of the verified facts (from `03_checked.md`) the shot shows or implies; `[]` for pure atmosphere. |

## Targets (checked by `check_storyboard.py`)

- 4–8 shots per scene (3 allowed for scenes under 30 seconds); each shot 2.5–9 seconds long, measured from `audio/timing.json`.
- Camera movement (anything but `static`) in at least 70% of shots.
- On-screen text or data in at most 30% of shots.
- Every `fact` ID is a VERIFIED fact in `03_checked.md`; every data shot names its fact.

## Pictures in version 1

Until Traversaal.ai answers whether AI-generated or stock images are allowed, every picture is **built in code** inside HyperFrames: SVG illustration, CSS shapes, gradients and particles, animated diagrams. A `frame` description must therefore be something the scene builder can draw: "a cutaway cell with graphite layers on the left and round lithium particles on the right", not "a photo of a Tesla factory".
