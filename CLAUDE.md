# Traversaal Video Agent

A tool inside Claude Code, made of skills and subagents, that turns **one prompt** into a **finished, narrated cinematic explainer of about 7 minutes (MP4)**, or a 2-minute demo, with no human involvement. Built for Traversaal.ai.

**What "cinematic explainer" means:** a short documentary-style film that follows one question the viewer cares about to its answer, told through moving full-frame pictures, camera work, music and sound, not narrated slides. A new shot every 3–8 seconds, camera movement in at least 70% of shots, on-screen text in at most 30% of shots, and every spoken fact verified. Every picture is built in code (no photos, footage or logos).

## Pipeline

Stages run in this order. Each stage reads the previous stage's file and writes its own, all inside `runs/<topic-slug>/`.

| # | Stage | Reads | Writes |
|---|---|---|---|
| 1 | Intake agent | the user's prompt | `01_brief.md` (with story spine and art direction) |
| 2 | Research agents, one per question in parallel | `01_brief.md` | `research/q<N>.md` → `02_research.md` |
| 3 | Fact-check agents, one per question in parallel | `02_research.md` | `checked/q<N>.md` → `03_checked.md` |
| 4 | Script agent | `01_brief.md`, `03_checked.md` | `04_script.json` (narration, acts) |
| 5 | Voiceover (`render/voiceover.py`) | `04_script.json` | `audio/scene_NN.wav`, `audio/timing.json`, `audio/subtitles.srt` |
| 6 | Storyboard agent | brief, script, `audio/timing.json`, `03_checked.md` | `05_storyboard.json` (shots) |
| 7 | Fact-check agent, final (script and storyboard) | `04_script.json`, `05_storyboard.json`, `03_checked.md` | `06_final_check.md` |
| 8 | Scene builder agents, one per scene in parallel | `05_storyboard.json`, `audio/timing.json`, `templates/film/` | `scenes/scene_NN/scene.html` |
| 9 | Render and sound (`render/render.py`, `render/sound.py`, HyperFrames) | scenes, audio, storyboard | `final.mp4` |

The `/make-video` skill runs all stages in order, loops back to the script agent when the length or the final fact-check fails, resumes a stopped run from its first unfinished stage, and stops at any stage it cannot repair. Video tools run through `render/env.sh`; see `render/README.md`. The web app (`app/`, started with `./start.sh`) runs the same skill headless.

## Key numbers (7-minute film)

- About 1,000 words of narration (140–150 words per minute).
- 10–15 scenes of 30–45 seconds each (about 75–110 words per scene).
- About 60–100 shots per film, 4–8 per scene, each 2.5–9 seconds (`check_storyboard.py` checks this).
- The script format is defined in `docs/scene-format.md` and the shot list in `docs/storyboard-format.md`. Follow them exactly.

## Folder layout

- `.claude/agents/`: one subagent file per stage
- `.claude/skills/make-video/`: the workflow that runs everything, plus its checking scripts
- `app/`: the local web app (Traversaal Video Studio)
- `docs/`: script format, storyboard format, visual style, scoring rubric
- `render/`: voiceover, render and sound scripts (HyperFrames), and `render/README.md` with the exact steps
- `templates/film/`: the scene shell, helpers and a reference scene
- `examples/snow-white/`: a finished 2-minute run, every stage's output plus the video
- `environment.yml`: the `video` conda environment (Node, FFmpeg, Python, local text-to-speech)
- `runs/<topic-slug>/`: every output of one run (kept on your computer, not in the repository)

## Rules

- `<topic-slug>` is the topic in lowercase words joined by hyphens, for example `how-ev-batteries-work`.
- Only use facts that passed the fact-check stage. Never invent a source.
- API keys go in `.env` only, never in the repo.
