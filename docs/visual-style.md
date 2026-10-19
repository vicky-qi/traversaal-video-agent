# Visual style

Owner: Jiaxin. **Updated Oct 16 for the cinematic definition** (Video Definition v2): the film is told through moving, full-frame pictures, not cards of text. Each film's own look comes from the brief's **Art direction**; this file sets the rules every film follows. The shot library in `templates/film/` implements them. (The first definition's slide layouts are described in git history before Oct 16.)

## Canvas

- 1920×1080, 30 fps. The picture fills the whole frame in every shot.
- **Subtitles:** small (30px), centred near the bottom on a soft dark pill; the shell shows them automatically. Keep the bottom 170px free of important picture detail.
- **Source credits:** small (22px), top right, only on shots that show a number (`credit(...)`). Every source also goes in the film's sources list.
- `hyperframes check` must pass with 0 errors before a scene renders.

## Default art direction

Used when the brief does not set one.

| | Default |
|---|---|
| Style | Flat vector illustration with soft gradients and glow, like an animated science documentary |
| Palette | Background `#0b1020`, accent `#38bdf8`, second accent `#f59e0b`, light `#e2e8f0` |
| Type | Inter (loaded by HyperFrames). Labels 34px semibold; big numbers 200px extra-bold in the accent colour |
| Mood | Curious and calm, building to a confident payoff; music mood `calm` |

## Shots and camera

| Rule | Target |
|---|---|
| Shot length | 2.5–9 seconds, mostly 4–6; 4–8 shots per scene |
| Camera | Movement in at least 70% of shots: `push_in`, `pull_out`, `pan_*`, `orbit`, `parallax`; `static` only for a beat of stillness |
| Motion inside the frame | Something meaningful moves in every shot: objects acting out the narration, particles, light |
| Timing | Actions start on the sentence that names them (`lineStart(i)`) |
| Scene transitions | `fade` (first scene), `zoom_through` (into something), `wipe` (change of place or time), `match_cut` (shape carries over), `cut` |
| Hero visual | Returns at least three times, including the last scene |

## On-screen text

- At most 10 words at a time, in at most 30% of shots: labels, a short title card, or one number with its unit.
- Numbers on screen are exact verified values (`data` in the storyboard), with a source credit.
- Never repeat the narration on screen; the subtitles already carry it.

| Element | Limit |
|---|---|
| Label or title card | 10 words |
| Big number | the value plus its unit |
| Source credit | publisher and year |

## Pictures in version 1

Built in code only: inline SVG, CSS shapes, gradients, particles and animated diagrams. No photographs, footage, logos, real people or specific products until Traversaal.ai confirms what images are allowed. Pictures must not imply anything the verified facts do not support.

## Motion rules HyperFrames enforces

- Animate transforms and opacity only (`x`, `y`, `scale`, `rotate`, `opacity`, SVG `attr`), never `left`, `top`, `width` or `height`.
- Text stays inside the frame and does not overlap other text.
- Deterministic animation only: no randomness or clocks.

## Sound

- Voice, plus a music bed under the whole film (synthesised by `render/sound.py` in the storyboard's `music.mood`, lowered automatically while the voice speaks), plus short effects (`whoosh`, `hit`, `rise`, `chime`) on the shots the storyboard marks.
