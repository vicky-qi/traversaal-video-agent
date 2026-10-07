# Scene format (`04_script.json`)

Owner: Julia. **Locked Oct 7.** Any change is announced in the group chat before it is pushed.

The script agent writes one JSON file per run, `runs/<topic-slug>/04_script.json`. Voiceover, the scene builder and assembly all read it.

- `docs/example-script.json`: a valid 2-scene example (real scripts have 10–15 scenes).
- `docs/example-script-full.json`: a 12-scene example built from `runs/how-ev-batteries-work/01_brief.md` that uses all five visual types.

Both examples show format, length and writing style only. Their chart numbers, quote and source URLs are placeholders, not checked facts.

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
  "narration": "Start with a single cell, the basic building block...",
  "duration_sec": 40,
  "visual_type": "bullets",
  "visual_content": { "heading": "Inside a single cell", "bullets": ["Anode", "Cathode", "Electrolyte", "Separator"] },
  "sources": ["https://example.com/source-page"]
}
```

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | integer | yes | Scene order: 1, 2, 3… with no gaps |
| `title` | string | yes | Short scene name, same as the brief's scene outline |
| `narration` | string | yes | Exactly what the voiceover says. Plain spoken text: no Markdown, URLs, brackets or symbols such as `%` and `$` |
| `duration_sec` | integer | yes | Target length in seconds, 30–45, from the brief. A target only; see Timing |
| `visual_type` | string | yes | Exactly one of `title`, `bullets`, `image`, `chart`, `quote` |
| `visual_content` | object | yes | What appears on screen; its fields depend on `visual_type` (below) |
| `sources` | array of strings | yes | Full URLs of the facts the scene uses, copied from `03_checked.md`. `[]` only if the scene states no facts |

No other fields. Every later stage copies these fields as they are.

## Timing

- `duration_sec` is the script agent's **target**: it sets the narration length at about `duration_sec × 2.4` words (145 words per minute).
- **The voiceover's real length always overrides `duration_sec`.** The scene builder measures each scene's audio file and the renderer uses only that measured length. Nobody edits the script to make the numbers match.
- Audio file names: the voiceover for scene `id` 1 is `runs/<topic-slug>/audio/scene_01.<ext>`, id 12 is `scene_12.<ext>` (two digits; `.wav`, `.mp3` or `.m4a`). Scene files use the same names: `scenes/scene_01.json`.

## `visual_content` by `visual_type`

On-screen text supports the narration; it never repeats it word for word. Fields not listed for a type are not allowed.

### `title`: opening, section break, closing or final takeaway

| Field | Type | Required | Limit |
|---|---|---|---|
| `headline` | string | yes | ≤ 8 words |
| `subheadline` | string | no | ≤ 12 words |
| `background_description` | string | no | What a background image would show, ≤ 25 words. Never a URL |

```json
{ "headline": "What's really powering an electric car?", "subheadline": "One idea explains range, charging, lifespan and price" }
```

### `bullets`: parts, steps or reasons the narration names

| Field | Type | Required | Limit |
|---|---|---|---|
| `heading` | string | no | ≤ 8 words |
| `bullets` | array of strings | yes | 2–5 items, each ≤ 12 words |

```json
{ "heading": "Inside a single cell", "bullets": ["Anode", "Cathode", "Electrolyte", "Separator"] }
```

### `image`: a photo or illustration

The script agent describes the image; it never gives a URL. The scene builder decides where the image comes from.

| Field | Type | Required | Limit |
|---|---|---|---|
| `image_description` | string | yes | Specific enough to search for, ≤ 25 words |
| `caption` | string | no | ≤ 12 words |
| `image_path` | string or `null` | no | Always `null` from the script agent; filled in later stages |

```json
{ "image_description": "Cutaway of an electric car showing a flat battery pack under the floor, made of rows of cells", "caption": "Cells, then modules, then one pack", "image_path": null }
```

### `chart`: comparing numbers or showing a change over time

| Field | Type | Required | Limit |
|---|---|---|---|
| `chart_type` | string | yes | `bar` (compare items), `line` (change over time) or `pie` (parts of a whole) |
| `chart_title` | string | yes | ≤ 10 words |
| `labels` | array of strings | yes | 2–8 items; years are strings, e.g. `"2015"` |
| `values` | array of numbers | yes | Same length and order as `labels`; exact figures from `03_checked.md` |
| `unit` | string | yes | e.g. `"US dollars per kWh"`, `"percent"` |
| `source_note` | string | yes | Short credit shown under the chart, e.g. `"Source name, 2024"` |

```json
{ "chart_type": "line", "chart_title": "Battery pack price per kWh", "labels": ["2015", "2024"], "values": [0, 0], "unit": "US dollars per kWh", "source_note": "Source name, year" }
```

### `quote`: one striking sentence from a real person or report

| Field | Type | Required | Limit |
|---|---|---|---|
| `quote_text` | string | yes | ≤ 30 words, copied exactly from `03_checked.md` |
| `attribution` | string | yes | Person and role, or report name and year |

```json
{ "quote_text": "Exact quote as it appears in the source.", "attribution": "Name, Title, Organization (2024)" }
```

## Checks before a script is accepted

`python3 .claude/skills/make-video/check_script.py runs/<topic-slug>/04_script.json` checks everything below except the last item.

- Valid JSON with exactly the fields above; required `visual_content` fields present and within limits.
- 10–15 scenes; `id`s run 1, 2, 3… with no gaps; `duration_sec` 30–45.
- `total_words` equals the real word count, between 950 and 1,100.
- Each scene's narration is within ±15% of `duration_sec × 2.4` words.
- No URLs, Markdown, brackets, `%` or `$` in narration.
- Every number, name and quote in `narration` or `visual_content` appears in `03_checked.md`, and its source URL is in that scene's `sources` (checked by people for now).
