# Visual style

Owner: Jiaxin. Based on the style guide on Jiaxin's pipeline branch, adapted to the five `visual_type`s in `docs/scene-format.md`. The templates in `templates/` implement this file; change both together.

Every scene shares one look so the joined video reads as one piece.

## Canvas

- 1920×1080, 30 fps, background `#0b1020`.
- **Content zone:** the top 880px, padding `120px 160px 0`. Headings, rows, charts, quotes and panels go here.
- **Caption band:** the bottom 200px. Only the sentence being spoken, centred, at most 1480px wide.
- **Source line:** top right of the content zone, 24px, `#94a3b8`: `Source: iea.org` or, for charts, the chart's `source_note`.
- `hyperframes check` must pass with 0 errors before a scene is rendered (`render/render.py` runs it).

## Type (Inter, loaded by HyperFrames)

| Role | Size | Weight | Colour |
|---|---|---|---|
| Eyebrow (label above the headline) | 30px, uppercase, letter-spacing .14em | 600 | `#38bdf8` |
| Headline | 108px (title), 84px (default), 72px (bullets), 64px (chart) | 700 | `#f4f4f5` |
| Subheadline / body | 40px | 400 | `#cbd5e1` |
| Bullet row text | 40px | 600 | `#f4f4f5` |
| Quote | 64px | 600 | `#f4f4f5` |
| Caption | 38px, line-height 1.35 | 400 | `#e2e8f0` |
| Source line, units | 24–26px | 400 | `#94a3b8` |

## Colour

- Accent `#38bdf8` for active items, eyebrows and the first data series. Second accent `#f59e0b` for a contrasting value.
- Cards and rows: fill `#111a2e`, border `#1e293b` (inactive) and `#38bdf8` (active), radius 20–28px.
- Extra chart colours, in order: `#a78bfa`, `#34d399`, `#f472b6`, `#94a3b8`.

## Layout by visual type

| `visual_type` | Layout |
|---|---|
| `title` | Topic as eyebrow, large headline (2 lines max), subheadline, short accent bar. |
| `bullets` | Scene title as eyebrow, heading, then 2–5 numbered rows. Rows start dim and light up one by one, spread across the narration. |
| `image` | Scene title as eyebrow and a wide panel with the caption. Version 1 has no image source, so the panel is a soft gradient placeholder; `image_description` is kept for later and not shown. |
| `chart` | Chart title as headline with the unit under it. `bar`: horizontal bars that grow in turn. `line`: a line that draws itself with value labels. `pie`: a donut with a legend. Values are shown exactly as given. |
| `quote` | Large quote with a left accent bar; the attribution fades in after the first sentence. |

## On-screen text limits

These match `docs/scene-format.md`; the scene builder flags anything longer.

| Field | Limit |
|---|---|
| `headline`, `heading` | 8 words |
| `subheadline`, `caption`, each bullet | 12 words |
| `chart_title` | 10 words |
| `quote_text` | 30 words |
| bullets per scene | 2–5 |
| chart labels | 2–8 |

## Motion

- Entrances: fade with a 24–40px rise, 0.5–0.8s, `power3.out`; groups stagger by about 0.1s.
- On-screen changes follow the voice: each reveal starts with a narration sentence.
- Use transforms (`scale`, `x`, `y`, opacity) for motion, never `left`, `top` or `width`; HyperFrames' check rejects layout motion.
- Each scene fades its content out over its last 0.4s. Scenes cut directly, with no transitions between them.
- Captions switch on at each sentence's start and off 0.3s after its end, or when the next sentence starts.
