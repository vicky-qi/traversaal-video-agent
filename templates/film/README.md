# Film shot library

Owner: Jiaxin (with Cynthia and Maggie). The building blocks for cinematic scenes (Video Definition v2, Oct 16). They replace the five slide layouts in `templates/*.js`, which stay only for runs made before Oct 16.

- `shell.html`: the scene page. `render/render.py` fills it with the scene's timing, storyboard shots and palette, and drops the scene builder's fragment (`runs/<slug>/scenes/scene_NN/scene.html`) into `#world`. The shell also plays the scene's `transition_in` and shows small subtitles.
- `example-scene.html`: a finished 6-shot reference scene ("Inside a single cell"), every picture built in SVG.

## Helpers available to a fragment

| Helper | What it does |
|---|---|
| `shot(n, el, {hold, camera, strength, fade})` | Shows `el` during shot `n` (cross-fading in and out) and applies the shot's camera move to the `.cam` inside it. `hold: true` keeps it on screen for the following shots. |
| `camera(el, move, start, dur, strength)` | One camera move: `push_in`, `pull_out`, `pan_left` / `pan_right` / `pan_up` / `pan_down` (the picture slides that way; `pan_left` reveals the right side), `orbit`, `parallax` (moves children with `data-depth`), `static` (slow drift). |
| `reveal(el, at, from, dur)` / `hide(el, at, dur)` | Bring an element in (fade and rise by default) or take it out. |
| `label(text, x, y, at, until)` | A small pill label for storyboard `text`. |
| `bigNumber(value, unit, x, y, at, until, decimals)` | A large number that counts up, with its unit, for storyboard `data`. |
| `credit(text, at, until)` | A small source credit in the top right, for data shots. |
| `shotStart(n)`, `shotEnd(n)`, `shotLen(n)`, `S(n)` | The shot's timing (seconds within the scene) and its storyboard entry. |
| `lineStart(i)` | When narration sentence `i` starts, to time an action to the words. |
| `P` | The art direction's palette: `P[0]` background, then accents. |

## Rules HyperFrames' check enforces

- Animate transforms and opacity only (`x`, `y`, `scale`, `rotate`, `opacity`, SVG `attr`); never `left`, `top`, `width` or `height`.
- Text must stay inside the frame and must not overlap other text.
- No randomness or clocks: the same frame must render the same way every time.

Check a scene without rendering it: `render/env.sh python render/render.py runs/<slug> --scene <id> --check-only`.
