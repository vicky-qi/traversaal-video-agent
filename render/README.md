# Rendering: from `04_script.json` to `final.mp4`

Owner: Cynthia. Uses HyperFrames (see `render/comparison.md`). The `/make-video` workflow follows these steps.

## One-time setup (about 10 minutes)

From the repo root:

```bash
conda env create -f environment.yml
```

This creates a conda environment called `video` with Node 22+, FFmpeg and Python. Every command below runs inside it through `render/env.sh`, which works even when conda is not activated (for example in the Claude desktop app). The first voiceover downloads the voice model (about 27 MB); the first render downloads HyperFrames' browser and fonts.

## The three steps

Replace `<slug>` with the run folder name, for example `how-ev-batteries-work`.

**1. Voiceover** (needs `runs/<slug>/04_script.json`):

```bash
render/env.sh python render/voiceover.py runs/<slug>
```

Writes `runs/<slug>/audio/scene_01.wav`, `scene_02.wav`… and `audio/timing.json` (when each sentence starts and ends). Each sentence is voiced separately, so captions match the voice exactly; unchanged sentences are reused on the next run. Options: `--voice af_heart` (default), `--speed 0.85` (default). It prints each scene's real length and exits with code 2 if the total is more than 15% away from the script's target, which means the script writer should trim or extend.

**2. Scene files**: run the `scene-builder` agent (Maggie's) on the same slug. It measures each audio file and writes `runs/<slug>/scenes/scene_NN.json` and `scenes/index.json`. Its `ffprobe` command must run through the wrapper: `render/env.sh ffprobe ...`.

**3. Render**:

```bash
render/env.sh python render/render.py runs/<slug>
```

For each scene it fills `templates/base.html` with `templates/<visual_type>.js` and the scene's content, runs `hyperframes check`, renders the scene, then joins all scenes into **`runs/<slug>/final.mp4`** (1920×1080, H.264 + AAC).

- `--scene 3`: re-render only scene 3 (after a fix), then join again.
- `--draft`: faster, lower-quality render for previews.
- It stops if `scenes/index.json` is not `complete`, or if `hyperframes check` finds an error, and prints which scene and why.

## Where things go

| Path | What | In GitHub? |
|---|---|---|
| `runs/<slug>/audio/` | Voiceover files and `timing.json` | No (`.gitignore`) |
| `runs/<slug>/scenes/` | Scene files from the scene builder | No (rebuilt from the script and audio) |
| `runs/<slug>/build/` | One HyperFrames project and MP4 per scene | No |
| `runs/<slug>/final.mp4` | The finished video | No: share it through the team Google Drive |

## Examples

- `runs/sample/`: Julia's 2-scene example script (`docs/example-script.json`) run through all three steps; 65.7 s.
- `runs/template-test/`: one scene of each chart type, a quote and an image, with placeholder numbers, used to test the templates.
