# Scene templates

Owner: Jiaxin (with Cynthia). They follow `docs/visual-style.md`, which is based on Jiaxin's style guide.

- `base.html`: the shared scene page: canvas, styles, captions, source line, timing and the scene's exit. `render/render.py` fills its three tokens (`__DURATION__`, `__SCENE_JSON__`, `__TYPE_SCRIPT__`).
- One script per `visual_type` in `docs/scene-format.md`: `title.js`, `bullets.js`, `image.js`, `chart.js` (bar, line and pie), `quote.js`. Each builds its layout from the scene's `visual_content` and adds its animations to the shared timeline.
- `hyperframes.json`: HyperFrames project settings copied into each scene's build folder.

To change the look, edit `docs/visual-style.md` and the matching template together, then re-render `runs/template-test` to check every type:

```bash
render/env.sh python render/render.py runs/template-test --draft
```

Rule from HyperFrames' check: animate with transforms and opacity (`scale`, `x`, `y`), never `left`, `top` or `width`.
