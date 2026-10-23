# Scene format (`04_script.json`)

The script holds only the narration and its story position; the pictures are planned in `05_storyboard.json` (`docs/storyboard-format.md`).

The script agent writes one JSON file per run, `runs/<topic-slug>/04_script.json`. The voiceover, storyboard and fact-check stages read it.

Example: `examples/snow-white/04_script.json` (a 2-minute film with 4 scenes; a 7-minute film has 10–15).

## File

```json
{
  "topic": "How Electric Car Batteries Work",
  "total_words": 1019,
  "scenes": [ { "...": "one object per scene, see below" } ]
}
```

| Field | Type | Rule |
|---|---|---|
| `topic` | string | The video title, from the brief's `# Video Brief:` heading |
| `total_words` | integer | Sum of narration words across all scenes; 950–1,100 |
| `scenes` | array of scene objects | 10–15 scenes, in the order they play |

## Scene

```json
{
  "id": 1,
  "title": "Inside a single cell",
  "act": 2,
  "narration": "Start with a single cell, the basic building block...",
  "duration_sec": 40,
  "sources": ["https://example.com/source-page"]
}
```

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | integer | yes | Scene order: 1, 2, 3… with no gaps |
| `title` | string | yes | Short scene name, same as the brief's scene outline |
| `narration` | string | yes | Exactly what the voiceover says. Plain spoken text: no Markdown, URLs, brackets or symbols such as `%` and `$` |
| `duration_sec` | integer | yes | Target length in seconds, 30–45, from the brief. A target only; see Timing |
| `act` | integer | yes | 1, 2 or 3, from the brief's scene outline (set-up, journey, payoff) |
| `sources` | array of strings | yes | Full URLs of the facts the scene uses, copied from `03_checked.md`. `[]` only if the scene states no facts |

No other fields. Every later stage copies these fields as they are.

## Timing

- `duration_sec` is the script agent's **target**: it sets the narration length at about `duration_sec × 2.4` words (145 words per minute).
- **The voiceover's real length always overrides `duration_sec`.** The renderer uses only each scene's measured audio length. Nobody edits the script to make the numbers match.
- Audio file names: the voiceover for scene `id` 1 is `runs/<topic-slug>/audio/scene_01.<ext>`, id 12 is `scene_12.<ext>` (two digits; `.wav`, `.mp3` or `.m4a`). Scene folders use the same names: `scenes/scene_01/`.

## Checks before a script is accepted

`python3 .claude/skills/make-video/check_script.py runs/<topic-slug>/04_script.json --minutes <N>` checks everything below except the last item. The scene and word counts are for a 7-minute film; `--minutes` scales them (a 2-minute film: 2–4 scenes, about 260–320 words).

- Valid JSON with exactly the fields above.
- 10–15 scenes; `id`s run 1, 2, 3… with no gaps; `duration_sec` 30–45.
- `total_words` equals the real word count, between 950 and 1,100.
- Each scene's narration is within ±15% of `duration_sec × 2.4` words.
- No URLs, Markdown, brackets, `%` or `$` in narration.
- Every number, name and quote in `narration` appears in `03_checked.md`, and its source URL is in that scene's `sources` (checked by the final fact-check).
