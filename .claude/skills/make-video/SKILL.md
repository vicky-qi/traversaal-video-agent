---
name: make-video
description: Turn a one-line prompt into a narrated, fact-checked ~7-minute cinematic explainer MP4 (a short documentary-style film, not slides) by running the intake, researcher, fact-checker, scriptwriter, storyboard and scene-builder subagents in order, then the voiceover, render and sound scripts. Use when the user asks to make a video from a prompt, or runs /make-video.
argument-hint: '"<prompt>" [--minutes 7] [--slug name]'
---

# make-video: prompt → cinematic explainer MP4

A cinematic explainer is one question followed to its answer, told through moving full-frame pictures, camera work, music and sound, with every fact verified.

You are the orchestrator. Run the stages below in order, give each subagent its inputs, check that its output file exists and looks right, and log every stage. **Do not do the subagents' work yourself**: no researching, writing narration or writing scene files in the main conversation. If a stage fails, retry or repair it as described below, never by skipping it.

Run every command from the repo root. Video tools run through `render/env.sh` (see `render/README.md`).

**Command rules** (runs started from the web app use `--permission-mode dontAsk` with the allowlist in `.claude/settings.json`, so anything else is refused):
- Run **one command per Bash call**, from the repo root, with **relative paths** exactly as written in this file. No `cd`, `&&`, `;`, pipes or inline scripts.
- Write and update `run_log.md` and every other file with the Write and Edit tools, never with `printf`, `echo >` or `cat <<`.
- Tell every subagent you launch to follow the same rules.

## 0. Start

1. The prompt is the text after `/make-video`. If there is none, ask for it and stop.
   - `--minutes N` (default 7): the film's target length. Pass it to the intake agent ("Target length: N minutes") and to every `check_script.py` call (`--minutes N`). A 2-minute film is the quick demo the web app offers.
   - `--slug name`: the web app creates `runs/<name>/` with a `request.json` before starting you; pass the slug to the intake agent so every file lands in that folder.
   - When run from the web app (headless, `claude -p`), never stop to ask the user anything: make the sensible choice, note it in `run_log.md`, and go on.
2. Check the video tools once: `render/env.sh ffmpeg -version`. If it fails, stop and point the user to the setup in `render/README.md`.
3. Note the start time (`date "+%Y-%m-%d %H:%M:%S"`). After each stage, append one line to `runs/<slug>/run_log.md`: `| <stage> | <start> | <end> | ok/failed | <short note> |` (create the file with a header row after the intake stage, once the slug is known).

## 1. Intake

Use the **intake** subagent with the prompt. Read the slug from its reply. Check that `runs/<slug>/01_brief.md` exists, has 5–7 key questions and a scene outline of 10–15 rows adding up to 400–450 seconds. If not, ask the intake agent once to fix it. Log `intake`.

## 2. Research (parallel, one researcher per question)

Launch one **researcher** subagent per key question, **all in the same message** so they run at the same time: "Topic slug: <slug>. Question number: <N>." Each writes `runs/<slug>/research/q<N>.md`. (One researcher doing every question in turn takes over 30 minutes.)

When all have finished, merge them:

```bash
python3 .claude/skills/make-video/merge_parts.py runs/<slug> research
```

It writes `02_research.md` and exits with code 1 if a question's file is missing: re-launch the researcher for that question once, then merge again. Check that every question has at least 2 facts; if one has none, note it and do not research it yourself. Log `research` with the fact count.

## 3. Fact-check the research (parallel, one checker per question)

Launch one **fact-checker** subagent per key question, all in the same message: "Topic slug: <slug>. Mode 1. Question number: <N>." Each writes `runs/<slug>/checked/q<N>.md`. Then merge:

```bash
python3 .claude/skills/make-video/merge_parts.py runs/<slug> checked
```

It writes `03_checked.md` with the verdict counts added up. Log `fact-check` with those counts, and list any question left with no verified facts: the script writer will write those scenes in general terms.

## 4. Script

Use the **scriptwriter** subagent: "Topic slug: <slug>." Then run:

```bash
python3 .claude/skills/make-video/check_script.py runs/<slug>/04_script.json --minutes <N>
```

If it prints any `FAIL` line, send those lines back for a revision (see **Revisions** below), at most 2 times. Log `script`.

## 5. Length fit (at most 2 rounds)

Word counts are only an estimate; the real voice decides. Run:

```bash
render/env.sh python render/voiceover.py runs/<slug>
```

- Exit 0 (`LENGTH OK`): go on.
- Exit 2 (`LENGTH LONG` or `LENGTH SHORT`): send the scriptwriter a revision with the measured total, the target, and each scene's measured seconds (from the output). Then run `check_script.py` and `voiceover.py` again; only changed sentences are re-voiced.
- After 2 rounds, go on anyway and note the length in the log.

Log `length-fit` with the measured total.

## 6. Storyboard

Use the **storyboard** subagent: "Topic slug: <slug>." It reads the brief's story spine and art direction, the script and `audio/timing.json`, and writes `runs/<slug>/05_storyboard.json`. Then run:

```bash
python3 .claude/skills/make-video/check_storyboard.py runs/<slug>
```

If it prints any `FAIL`, send the failures back to the storyboard agent (at most 2 times). Log `storyboard` with the numbers line (shots, per minute, camera movement, on-screen text).

## 7. Final fact-check of script and storyboard (at most 2 rounds)

This runs after the length fit and the storyboard, so it checks the final words and pictures. Scripts can stretch facts that were correct in the research.

1. Use a **fresh fact-checker** subagent in Mode 2: "Topic slug: <slug>. Final check (Mode 2): script and storyboard." It writes `runs/<slug>/06_final_check.md`.
2. `PASS`: go to step 8.
3. `FAIL` on narration: send the scriptwriter a revision (see **Revisions**), run `check_script.py` and `voiceover.py` again (only changed sentences are re-voiced), then ask the storyboard agent to update the shots of the changed scenes, and go back to 1. In round 2, ask the fact-checker to re-check only the changed scenes.
4. `FAIL` on a shot: send the storyboard agent the failing shots and reasons, run `check_storyboard.py`, then go back to 1.
5. After 2 rounds, tell the scriptwriter to **delete** every sentence that still fails, and the storyboard agent to remove every shot that still fails. Unverified claims never reach the final film.

Log `final-check`.

## 8. Scene building (parallel, one builder per scene)

Launch one **scene-builder** subagent per scene, **all in the same message**: "Topic slug: <slug>. Scene id: <N>." Each writes `runs/<slug>/scenes/scene_NN/scene.html` and checks it with `render.py --check-only`; a builder usually takes 10–20 minutes. When all have finished, check that every scene has a `scene.html`; re-launch a builder once for any scene that is missing or whose check failed. Log `scenes`.

## 9. Render and sound

```bash
render/env.sh python render/render.py runs/<slug>
```

It checks and renders each scene, joins them, then mixes a music bed (the storyboard's `music.mood`) and the shots' sound effects under the voice (`render/sound.py`), writing `runs/<slug>/final.mp4`. If a scene fails its check, send the error to a scene builder for that scene ("Fix this check failure: …"), then run `render.py runs/<slug> --scene <N>`. One repair attempt per scene; if it still fails, log `render failed` and report it. Log `render` with the final length.

## 10. Report

Tell the user briefly:

- the video path and its length vs the 7-minute target
- the film's numbers from `check_storyboard.py` (shots per minute, camera movement, on-screen text)
- the fact-check results (verified, rejected, final-check rounds, sentences or shots removed)
- the assumptions the intake agent made (from `01_brief.md`), since the user never confirmed them
- time per stage (from `run_log.md`) and the total
- anything that failed or needs a human look

## Resume

When told to resume a run (the web app's "Continue this run", after a stop, a crash or a usage limit), keep every finished stage and start at the first one whose output is missing or incomplete:

| Stage | Finished when |
|---|---|
| 1 Intake | `01_brief.md` exists |
| 2 Research | `02_research.md` exists (if only some `research/q<N>.md` exist, launch researchers for the missing questions, then merge) |
| 3 Fact-check | `03_checked.md` exists (same rule for `checked/q<N>.md`) |
| 4–5 Script and length fit | `04_script.json` and `audio/timing.json` exist and `run_log.md` has a `length-fit` row |
| 6 Storyboard | `05_storyboard.json` exists and `check_storyboard.py` prints no `FAIL` |
| 7 Final check | `06_final_check.md` ends with `PASS` |
| 8 Scenes | every script scene has `scenes/scene_NN/scene.html` and `render.py --scene <N> --check-only` passes; launch builders only for the scenes that do not |
| 9 Render | `final.mp4` exists |

Read `run_log.md` first, add a row `| resume | <time> | <time> | ok | continuing at <stage> |`, and never redo a finished stage.

## Revisions

The scriptwriter never overwrites an existing script. Before every revision:

1. Rename `runs/<slug>/04_script.json` to `04_script.v<N>.json` (N = 1, 2, 3…).
2. Use the **scriptwriter**: "Topic slug: <slug>. Revision pass. Start from `04_script.v<N>.json` and keep everything that is not mentioned below exactly the same. Fix: <the problems, scene by scene>."
3. Run `check_script.py` on the new file.
