# Scene Style Guide

All scenes in a video share this look so the stitched video reads as one piece. The scene-builder agent follows it exactly; change it here to restyle every future video.

## Canvas and layout

- 1920×1080, 30 fps. Background `#0b1020`.
- **Content zone:** top 880px, padding `120px 160px 0`. All headings, cards, numbers, and charts go here.
- **Caption band:** bottom 200px (y = 880–1080). Only the current narration sentence, centered, max width 1480px.
- Nothing may overlap across the two zones. `hyperframes check` must pass with 0 errors.

## Type (Inter, loaded automatically by HyperFrames)

| Role | Size | Weight | Color |
|---|---|---|---|
| Eyebrow (small label above headline) | 30px, uppercase, letter-spacing .14em | 600 | `#38bdf8` |
| Headline | 84–96px, letter-spacing -.03em, line-height 1.05 | 700 | `#f4f4f5` |
| Dimmed headline words | same | 700 | `#64748b` |
| Card label | 44–48px | 700 | `#f4f4f5` |
| Body / supporting text | 34–40px | 400 | `#cbd5e1` |
| Big stat number | 220–280px, letter-spacing -.04em | 800 | `#38bdf8` |
| Caption | 38px, line-height 1.35 | 400 | `#e2e8f0` |
| Source line (small, bottom of content zone) | 24px | 400 | `#94a3b8` |

## Colors

- Accent `#38bdf8` (active state, numbers, eyebrow). Second accent `#f59e0b` only for a contrasting value in comparisons.
- Surfaces: card `#111a2e`, border `#1e293b` (inactive) → `#38bdf8` (active). Radius 24px.

## Visual types

| `visual_type` | Layout |
|---|---|
| `title` | Eyebrow + large headline (2 lines max) + one-line subtitle. Used for the opening scene. |
| `key_points` | Eyebrow + headline, then 2–4 cards in a row. Cards appear dim (opacity .35) and light up (border accent, opacity 1) when their sentence starts. See `key_points.html`. |
| `stat` | One big number counting up to its value when its sentence starts, a label under it, the source line below. |
| `quote` | Large quote text (≤ 25 words) with a left accent bar, attribution beneath. |
| `chart` | Horizontal bar chart with 2–6 bars, drawn in pure HTML/CSS (no chart libraries); bars grow when their sentence starts; value labels at bar ends. |
| `comparison` | Two columns, left accent `#38bdf8` vs right `#f59e0b`, each with a header and 2–3 lines. |
| `timeline` | Horizontal line with 3–5 dated markers that appear in sequence. |

## Motion

- Entrances: fade + 24–40px rise, 0.5–0.8s, `power3.out`. Stagger groups by 0.1s.
- Every on-screen change is keyed to a narration line start: `vo_offset_s + line.start`.
- Scene exit: fade the content zone to 0 over 0.4s ending at `scene_duration_s`. Scenes cut directly, with no cross-scene transitions.
- Captions switch on exactly at each line start and off 0.3s after its end.

## Sources on screen

When a scene's narration cites facts, show a small source line at the bottom of the content zone (y ≈ 820px): `Source: <publisher>, <year>`. Several sources are separated by ` · `.
