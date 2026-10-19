# Traversaal Video Agent

UCLA Anderson MSBA capstone (MGMTMSA 412) for Traversaal.ai. We are building a tool inside Claude Code, made of skills and subagents, that turns **one prompt** into a **finished, narrated cinematic explainer of about 7 minutes (MP4)** with little human involvement.

**What "cinematic explainer" means** (Video Definition v2, Oct 16): a short documentary-style film that follows one question the viewer cares about to its answer, told through moving full-frame pictures, camera work, music and sound, not narrated slides. A new shot every 3–8 seconds, camera movement in at least 70% of shots, on-screen text in at most 30% of shots, and every spoken fact verified. Version 1 builds every picture in code (no photos, footage or logos) until Traversaal.ai says what images are allowed.

## Pipeline

Stages run in this order. Each stage reads the previous stage's file and writes its own, all inside `runs/<topic-slug>/`.

| # | Stage | Reads | Writes | Owner |
|---|---|---|---|---|
| 1 | Intake agent | the user's prompt | `01_brief.md` (with story spine and art direction) | Vicky |
| 2 | Research agents, one per question in parallel | `01_brief.md` | `research/q<N>.md` → `02_research.md` | Vicky |
| 3 | Fact-check agents, one per question in parallel | `02_research.md` | `checked/q<N>.md` → `03_checked.md` | Jiaxin |
| 4 | Script agent | `01_brief.md`, `03_checked.md` | `04_script.json` (narration, acts) | Julia |
| 5 | Voiceover (`render/voiceover.py`) | `04_script.json` | `audio/scene_NN.wav`, `audio/timing.json`, `audio/subtitles.srt` | Cynthia |
| 6 | Storyboard agent | brief, script, `audio/timing.json`, `03_checked.md` | `05_storyboard.json` (shots) | Jiaxin |
| 7 | Fact-check agent, final (script and storyboard) | `04_script.json`, `05_storyboard.json`, `03_checked.md` | `06_final_check.md` | Jiaxin |
| 8 | Scene builder agents, one per scene in parallel | `05_storyboard.json`, `audio/timing.json`, `templates/film/` | `scenes/scene_NN/scene.html` | Maggie |
| 9 | Render and sound (`render/render.py`, `render/sound.py`, HyperFrames) | scenes, audio, storyboard | `final.mp4` | Cynthia |

The `/make-video` skill (owner: Julia) runs all stages in order, loops back to the script agent when the length or the final fact-check fails, and stops at any stage it cannot repair. Video tools run through `render/env.sh`; see `render/README.md`.

## Key numbers

- About 1,000 words of narration (140–150 words per minute).
- 10–15 scenes of 30–45 seconds each (about 75–110 words per scene).
- The script format is defined in `docs/scene-format.md` and the shot list in `docs/storyboard-format.md`. Follow them exactly.
- About 60–100 shots per film, 4–8 per scene, each 2.5–9 seconds (`check_storyboard.py` checks this).

## Folder layout

- `.claude/agents/`: one subagent file per stage
- `.claude/skills/make-video/`: the workflow that runs everything
- `docs/`: scene format, visual style, rubric, meeting notes
- `render/`: voiceover and render scripts (HyperFrames), and `render/README.md` with the exact steps
- `templates/film/`: the film shot library (scene shell, helpers, reference scene); `templates/*.js` and `base.html` are the first definition's slide layouts, kept so old runs re-render
- `environment.yml`: the `video` conda environment (Node, FFmpeg, Python, local text-to-speech)
- `tests/prompts.md`: the shared test prompts; `tests/log.md`: one row per test run
- `runs/<topic-slug>/`: every output of one run

## Rules

- `<topic-slug>` is the topic in lowercase words joined by hyphens, for example `how-ev-batteries-work`.
- Only use facts that passed the fact-check stage. Never invent a source.
- Each person edits only the files they own. Announce changes to the scene format or this file in the group chat first.
- API keys go in `.env` only, never in the repo.
- After every test run, add a row to `tests/log.md`.
