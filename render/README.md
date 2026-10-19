# Rendering: from `04_script.json` to `final.mp4`

Owner: Cynthia. Uses HyperFrames (see `render/comparison.md`). The `/make-video` workflow follows these steps.

## One-time setup (about 10 minutes)

Run this **inside the project folder** (the one that contains `environment.yml`):

```bash
conda env create -f environment.yml
```

- `EnvironmentFileNotFound`: you are in the wrong folder. `cd` into the project folder first.
- `prefix already exists`: the environment is already installed. Nothing to do.
- `conda: command not found`: install Miniconda or Anaconda first.

This creates a conda environment called `video` with Node 22+, FFmpeg and Python. Every command below runs inside it through `render/env.sh`, which works even when conda is not activated (for example in the Claude desktop app). The first voiceover downloads the voice model (about 27 MB); the first render downloads HyperFrames' browser and fonts.

## Film mode (cinematic definition, Oct 16)

Replace `<slug>` with the run folder name. The `/make-video` workflow runs these in order.

**1. Voiceover** (needs `runs/<slug>/04_script.json`):

```bash
render/env.sh python render/voiceover.py runs/<slug>
```

Writes `audio/scene_NN.wav`, `audio/timing.json` (when each sentence starts and ends) and `audio/subtitles.srt`. Each sentence is voiced separately, so subtitles and shots match the voice exactly; unchanged sentences are reused on the next run. Options: `--voice af_heart` (default), `--speed 0.85` (default). Exit code 2 means the total is more than 15% away from the script's target.

**2. Storyboard** (the `storyboard` agent) writes `05_storyboard.json`; check it with `python3 .claude/skills/make-video/check_storyboard.py runs/<slug>`.

**3. Scenes** (one `scene-builder` agent per scene) write `scenes/scene_NN/scene.html`. Check one scene without rendering:

```bash
render/env.sh python render/render.py runs/<slug> --scene 3 --check-only
```

**4. Render and sound**:

```bash
render/env.sh python render/render.py runs/<slug>
```

For each scene it places the scene's fragment into `templates/film/shell.html` with the storyboard's shot timing and palette, runs `hyperframes check`, renders it, joins all scenes, then `render/sound.py` adds a synthesised music bed (the storyboard's `music.mood`, lowered under the voice) and the shots' sound effects. Output: **`runs/<slug>/final.mp4`** (1920×1080, H.264 + AAC).

- `--scene 3`: re-render only scene 3, then join and mix again if every scene is rendered.
- `--draft`: faster, lower-quality render for previews.
- It stops at the first scene that fails `hyperframes check` and prints why.

## Slide mode (first definition)

Runs made before Oct 16 have no `05_storyboard.json`; `render.py` renders them the old way, from `scenes/index.json` and the slide templates in `templates/`.

## Where things go

| Path | What | In GitHub? |
|---|---|---|
| `runs/<slug>/audio/` | Voiceover files and `timing.json` | No (`.gitignore`) |
| `runs/<slug>/scenes/` | Scene fragments from the scene builders (the film's source) | Yes |
| `runs/<slug>/build/` | One HyperFrames project and MP4 per scene, plus the sound files | No |
| `runs/<slug>/final.mp4` | The finished video | No: share it through the team Google Drive |

## Examples

- `runs/sample/`: Julia's 2-scene example script (`docs/example-script.json`) run through all three steps; 65.7 s.
- `runs/template-test/`: one scene of each chart type, a quote and an image, with placeholder numbers, used to test the templates.
