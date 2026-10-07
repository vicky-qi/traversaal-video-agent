# capstone-video-agent

Turn a one-line prompt into a narrated, fact-checked explainer video (MP4), using Claude Code subagents and [HyperFrames](https://github.com/heygen-com/hyperframes).

UCLA Anderson MSBA capstone, sponsored by Traversaal.ai.

```
prompt ─▶ intake ─▶ research (one agent per question, parallel) ─▶ script
       ─▶ length fit (measure real voiceover, trim) ─▶ fact-check (revise until every line is supported)
       ─▶ voiceover ─▶ scene builder (one HyperFrames file per scene, parallel) ─▶ render + stitch ─▶ MP4
```

Everything runs locally. Voiceover uses Kokoro-82M, an open TTS model that runs on your laptop for free. The only cost is Claude usage.

---

## 1. One-time setup (about 15 minutes)

You need macOS or Linux, about 3 GB of free disk space, and Google Chrome installed (HyperFrames renders frames with it).

### a. Conda
If `conda --version` fails, install [Miniconda](https://docs.anaconda.com/miniconda/install/). Anaconda also works.

### b. Clone and create the environment
```bash
git clone https://github.com/jiaxinwu1206/capstone-personal-.git capstone-video-agent
cd capstone-video-agent
conda env create -f environment.yml
```
This creates a conda env named **`video`** with Python 3.12, Node.js ≥ 22, FFmpeg, and the Kokoro TTS Python package. It does not touch your other environments. Remove it any time with `conda env remove -n video`.

You never need to `conda activate` it for the pipeline: every command goes through `tools/env.sh`, which finds conda and activates `video` for that one command.

### c. Check HyperFrames and the voice
```bash
tools/env.sh npx hyperframes doctor
tools/env.sh npx hyperframes tts "Setup works." -o /tmp/test.wav
```
`doctor` should show FFmpeg, FFprobe and Chrome as ✓; the whisper, MusicGen and Docker rows are optional and can be ✗. The first `tts` call downloads the voice model and voices (~350 MB) to `~/.cache/hyperframes/tts/`; the weights are never stored in the repo.

Optional, to turn off HyperFrames' anonymous usage telemetry: `tools/env.sh npx hyperframes telemetry disable`.

### d. Install the HyperFrames agent skills
```bash
tools/env.sh npx hyperframes skills update
```
This installs the HyperFrames skills (e.g. `hyperframes-core`) to `~/.claude/skills/`. The scene-builder agent preloads `hyperframes-core`.

### e. Claude Code
Install [Claude Code](https://code.claude.com/docs) (terminal or desktop app) and open this folder as the project. The subagents in `.claude/agents/` and the `/make-video` skill load automatically. **Start a new session after cloning or pulling** so new agent files are picked up.

---

## 2. Make a video

In Claude Code, from the repo root:

```
/make-video "How are small businesses actually using generative AI, and is it paying off?" --minutes 1 --scenes 2
```

| Option | Default | Notes |
|---|---|---|
| `--minutes` | 1 | Target length. 7 for the full video. |
| `--scenes` | 2 for 1 min, otherwise minutes×60/35 | 10–15 scenes for a 7-minute video. |
| `--slug` | from the prompt | Folder name under `runs/`. |

The orchestrator creates `runs/<slug>/`, runs each stage, and reports the video path, fact-check outcome, the assumptions intake made, and time per stage. The finished video is `runs/<slug>/<slug>.mp4`.

### What is in a run folder

```
runs/<slug>/
  prompt.txt          the user prompt
  brief.json          intake: audience, angle, key questions, assumptions
  research/q1.json    researcher: facts with source URL + verbatim excerpt (one file per question)
  scenes.json         script: scenes, narration lines, cited fact ids, on-screen items, measured timing
  factcheck.json      fact-checker: verdict per line + source checks
  scenes/s01/         one HyperFrames project per scene: index.html + vo.wav
  renders/s01.mp4     rendered scenes
  <slug>.mp4          final stitched video
  run_log.json        each stage's status and duration (for evaluation)
```

Audio, renders, and MP4s are git-ignored; the JSON files are small and worth committing for runs you want to keep as examples.

### Fix one thing without rerunning everything

```bash
tools/env.sh python tools/voiceover.py runs/<slug>                 # re-voice (only changed lines are regenerated)
tools/env.sh npx hyperframes preview runs/<slug>/scenes/s02        # open one scene in HyperFrames Studio
tools/env.sh python tools/assemble.py runs/<slug> --only s02       # re-render one scene and re-stitch
```

---

## 3. How it works

### Agents (`.claude/agents/`)

| Agent | Model | Reads → writes | Job |
|---|---|---|---|
| `intake` | Sonnet | `prompt.txt` → `brief.json` | Audience, angle (a hypothesis, not a conclusion), research questions, assumptions. Never asks the user; records guesses. |
| `researcher` | Sonnet | `brief.json` → `research/<qid>.json` | One per question, in parallel. Every fact must come from a page it actually opened, with a ≤ 25-word verbatim excerpt. |
| `scriptwriter` | Opus | brief + research → `scenes.json` | Spoken narration split into scenes. Every factual sentence cites fact ids. Also does trim and revision passes. |
| `fact-checker` | Opus | `scenes.json` + research → `factcheck.json` | Re-opens every source, judges each line `supported` / `overstated` / `unsupported` / `uncited`. Never edits the script. |
| `scene-builder` | Sonnet | `scenes.json` + `templates/` → `scenes/<id>/index.html` | One per scene, in parallel. Times every on-screen change to the measured voiceover, then runs `hyperframes check` and looks at snapshots. |

The orchestrator is the skill `.claude/skills/make-video/SKILL.md`. It only sequences agents, runs tools, and enforces the loops: at most 2 trim rounds, at most 2 fact-check revision rounds (then unsupported lines are deleted), and 1 repair attempt per failed scene.

### Tools (`tools/`)

The deterministic steps are small Python scripts, so agents never improvise them:

| Tool | Does |
|---|---|
| `env.sh` | Runs a command inside the `video` conda env. |
| `new_run.py` | Creates `runs/<slug>/`. |
| `check_script.py` | Validates `scenes.json`: structure, every cited fact exists, estimated length. |
| `voiceover.py` | TTS per sentence → measured timings in `scenes.json`; exits 2 if the total is > 15% off target. |
| `assemble.py` | `hyperframes check` + render per scene, verify durations, stitch with FFmpeg. |
| `log_stage.py` | Appends a stage result to `run_log.json`. |

### Key design rules
- **Audio first.** Visuals are timed to the measured voiceover, never the reverse.
- **Measured length beats estimates.** TTS reads numbers in full ("2025" → "twenty twenty-five"), so a number-heavy script runs ~25% longer than a word count suggests. The pipeline measures real audio and trims before fact-checking.
- **Nothing unverified is voiced.** Fact-check runs on the final wording.
- **One scene = one standalone HyperFrames project**, so a broken scene is fixed and re-rendered alone.
- **One shared style** (`templates/style-guide.md`, reference scene `templates/key_points.html`) so scenes look like one video.

---

## 4. Repo layout

```
.claude/agents/        the five subagents
.claude/skills/        make-video orchestrator
tools/                 deterministic helpers (see above)
templates/             style guide, reference scene, hyperframes.json
docs/                  step results and decisions
prototypes/            Step 1 experiments (HyperFrames vs Remotion, 30s scene); reference only
runs/                  one folder per generated video
environment.yml        conda env spec
```

## 5. Troubleshooting

| Symptom | Fix |
|---|---|
| `conda env 'video' not found` | `conda env create -f environment.yml` |
| `conda not found` from `tools/env.sh` | `export CONDA_EXE=/path/to/conda/bin/conda` |
| TTS: `kokoro-onnx package is not installed` | You ran `npx hyperframes tts` outside `tools/env.sh`; prefix it. |
| `/make-video` or agents not found | Start a new Claude Code session in the repo root. |
| Render fails on Chrome | `tools/env.sh npx hyperframes browser ensure`, or install Google Chrome. |
| Scene check reports `nested_structure_needs_subcomposition` | Expected warning for standalone scenes; ignore. |

## 6. Decisions and results
- [docs/step1-results.md](docs/step1-results.md): why HyperFrames over Remotion (Apache-2.0 license vs Remotion's ≤ 3-person free tier; built-in TTS and checks), first prototype.
- [docs/step2-results.md](docs/step2-results.md): first end-to-end 60-second run and what it changed.
