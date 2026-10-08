---
name: make-video
description: Turn a one-line prompt into a narrated, fact-checked ~7-minute explainer MP4 by running the intake, researcher, fact-checker, scriptwriter and scene-builder subagents in order, then the voiceover and render scripts. Use when the user asks to make a video from a prompt, or runs /make-video.
argument-hint: '"<prompt>"'
---

# make-video: prompt → narrated MP4

Owner: Julia. Adapted from the orchestrator on Jiaxin's pipeline branch to the file names on main (`CLAUDE.md`, `docs/scene-format.md`).

You are the orchestrator. Run the stages below in order, give each subagent its inputs, check that its output file exists and looks right, and log every stage. **Do not do the subagents' work yourself**: no researching, writing narration or writing scene files in the main conversation. If a stage fails, retry or repair it as described below, never by skipping it.

Run every command from the repo root. Video tools run through `render/env.sh` (see `render/README.md`).

## 0. Start

1. The prompt is the text after `/make-video`. If there is none, ask for it and stop.
2. Check the video tools once: `render/env.sh ffmpeg -version`. If it fails, stop and point the user to the setup in `render/README.md`.
3. Note the start time (`date "+%Y-%m-%d %H:%M:%S"`). After each stage, append one line to `runs/<slug>/run_log.md`: `| <stage> | <start> | <end> | ok/failed | <short note> |` (create the file with a header row after the intake stage, once the slug is known).

## 1. Intake

Use the **intake** subagent with the prompt. Read the slug from its reply. Check that `runs/<slug>/01_brief.md` exists, has 5–7 key questions and a scene outline of 10–15 rows adding up to 400–450 seconds. If not, ask the intake agent once to fix it. Log `intake`.

## 2. Research

Use the **researcher** subagent: "Topic slug: <slug>." Check that `runs/<slug>/02_research.md` exists and that every key question has at least 2 facts. If a question has none, note it; do not research it yourself. Log `research` with the fact count. (This stage takes about 30 minutes; running one researcher per question in parallel is the planned speed-up.)

## 3. Fact-check the research

Use the **fact-checker** subagent (Mode 1): "Topic slug: <slug>." Check that `runs/<slug>/03_checked.md` exists. Log `fact-check` with its verdict counts, and list any question left with no verified facts: the script writer will write those scenes in general terms.

## 4. Script

Use the **scriptwriter** subagent: "Topic slug: <slug>." Then run:

```bash
python3 .claude/skills/make-video/check_script.py runs/<slug>/04_script.json
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

## 6. Fact-check the final script (at most 2 rounds)

This runs after the length fit so it checks the final wording. Jiaxin's test found the script writer stretching facts that were correct in the research.

1. Use a **fresh fact-checker** subagent in Mode 2: "Topic slug: <slug>. Check the script (Mode 2)." It writes `runs/<slug>/05_script_check.md`.
2. `PASS`: go to step 7.
3. `FAIL`: send the scriptwriter a revision with the failing sentences and reasons, run `check_script.py`, then go back to 1.
4. After 2 rounds, if sentences still fail, send a revision telling the scriptwriter to **delete** every failing sentence. Unverified claims never reach the final video.
5. If the wording changed, run `voiceover.py` again (a length warning here is logged, not looped on).

Log `script-check`.

## 7. Scene files

Use the **scene-builder** subagent: "Topic slug: <slug>." Check that `runs/<slug>/scenes/index.json` has `"status": "complete"`. If it is incomplete, read its `problems`: missing or ambiguous audio means rerun `voiceover.py`; incomplete `visual_content` means a script revision. Log `scenes`, including any `review_flags`.

## 8. Render

```bash
render/env.sh python render/render.py runs/<slug>
```

It checks each scene with `hyperframes check`, renders it and joins everything into `runs/<slug>/final.mp4`. If a scene fails its check, the error names the scene: if the cause is content (text too long), send a script revision for that scene, rerun steps 5–7 as needed, then `render.py runs/<slug> --scene <N>`; if it is a template problem, stop and report it. Log `render` with the final length.

## 9. Report

Add one row to `tests/log.md`, then tell the user briefly:

- the video path and its length vs the 7-minute target
- the fact-check results (verified, rejected, script-check rounds, sentences deleted)
- the assumptions the intake agent made (from `01_brief.md`), since the user never confirmed them
- time per stage (from `run_log.md`) and the total
- anything that failed or needs a human look (`review_flags`, thin scenes)

## Revisions

The scriptwriter never overwrites an existing script. Before every revision:

1. Rename `runs/<slug>/04_script.json` to `04_script.v<N>.json` (N = 1, 2, 3…).
2. Use the **scriptwriter**: "Topic slug: <slug>. Revision pass. Start from `04_script.v<N>.json` and keep everything that is not mentioned below exactly the same. Fix: <the problems, scene by scene>."
3. Run `check_script.py` on the new file.
