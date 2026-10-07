---
name: make-video
description: Turn a prompt into a narrated, fact-checked MP4 explainer video by running the intake, researcher, scriptwriter, fact-checker and scene-builder subagents in order, then voicing, rendering and stitching the scenes. Use when the user asks to make or generate a video from a prompt, or runs /make-video.
argument-hint: '"<prompt>" [--minutes 1] [--scenes 2] [--slug name]'
---

# make-video: prompt → narrated MP4

You are the orchestrator. You run the stages below in order, hand each subagent its inputs, check its output file exists and is valid, and log every stage. **Do not do the subagents' work yourself** (no researching, writing narration, or writing scene HTML in the main conversation). If a stage fails, retry or repair it as described, never by skipping it.

Run every command from the repo root. Run tools through `tools/env.sh`, which activates the `video` conda env.

## 0. Parse the request
- `prompt`: the user's text. Required.
- `--minutes`: default **1**. `target_duration_s` = minutes × 60.
- `--scenes`: default 2 for 1 minute; otherwise round(target_duration_s / 35), kept within 10-15 for 6-8 minutes.
- `--slug`: default = 3-5 kebab-case words from the prompt. If `runs/<slug>` exists, append `-2`, `-3`, ….

```bash
tools/env.sh python tools/new_run.py <slug> "<prompt>"
```
Below, `RUN=runs/<slug>`. After each stage run `tools/env.sh python tools/log_stage.py $RUN <stage> ok|failed "<note>"`.

## 1. Intake
Use the **intake** subagent: "Run folder: $RUN. Target length: <target_duration_s> seconds. Scene count: <n>."
Check that `$RUN/brief.json` exists and has `key_questions`. Log `intake`.

## 2. Research (parallel)
Launch one **researcher** subagent per key question, **all in the same message** so they run in parallel: "Run folder: $RUN. Question id: <qid>."
Check that each `$RUN/research/<qid>.json` exists with at least 2 facts. Re-run a researcher once if its file is missing or empty. Log `research` with the total fact count.

## 3. Script
Use the **scriptwriter** subagent: "Run folder: $RUN. Write scenes.json."
Then run `tools/env.sh python tools/check_script.py $RUN` yourself. If it fails, send the scriptwriter the error lines and ask it to fix them (at most 2 times). Log `script`.

## 4. Length fit (at most 2 trim rounds)
The word-count estimate is rough (numbers and acronyms slow the voice), so measure the real audio:
```bash
tools/env.sh python tools/voiceover.py $RUN
```
- Exit 0 (`LENGTH OK`): go to step 5.
- Exit 2 (`LENGTH LONG` or `SHORT`): send the **scriptwriter** "Run folder: $RUN. Trim pass: measured total is <X>s vs target <T>s. Per-line seconds: <paste the list>. Cut to fit." Then run `check_script.py` and `voiceover.py` again. Only changed lines are re-voiced, so this is fast.
- After 2 trim rounds, continue even if still off, and note the length in the log.
Log `length-fit` with the measured total.

## 5. Fact-check loop (at most 2 revision rounds)
This runs after the length fit, so it checks the final wording.
1. Use a **fresh fact-checker** subagent each round: "Run folder: $RUN." Log `factcheck-<round>` with its summary.
2. If `factcheck.json` has `"pass": true`, go to step 6.
3. Otherwise use the **scriptwriter**: "Run folder: $RUN. Revision pass: fix the lines flagged in factcheck.json." Run `check_script.py`, then go back to 1.
4. After 2 revision rounds, if lines still fail, have the scriptwriter **delete** every line that is not `supported`, run `check_script.py` again, and record the deletions in the log note. Unverified claims never go to voiceover.

## 6. Voiceover
Use the **voiceover** subagent: "Run folder: $RUN." It reviews how every sentence will be pronounced (fixing names and terms in `$RUN/pronunciations.json`), generates the audio with `tools/voiceover.py`, and verifies it with `tools/check_voice.py` (loudness, dropped words, pacing). It never changes the narration wording; the voice reads a speech version (years, money, acronyms rewritten), and captions keep the original.
Check that its reply says the voice check passed. If it reports a line that cannot be made to sound right, send that line to the **scriptwriter** to reword, then run a **fresh fact-checker** on the result and repeat this step. Log `voiceover` with the respellings it added and the measured total; a `LENGTH` warning here is logged, not looped on.

If the voiceover is ever regenerated **after** scenes are built (e.g. a late wording fix), run `tools/env.sh python tools/sync_timing.py $RUN` to move the scenes onto the new timing; it lists any scene that must be rebuilt by a scene-builder instead.

## 7. Scene building (parallel)
Launch one **scene-builder** subagent per scene, **all in the same message**: "Run folder: $RUN. Scene id: <id>."
Check that each `$RUN/scenes/<id>/index.html` exists. Log `scenes`.

## 8. Render and stitch
```bash
tools/env.sh python tools/assemble.py $RUN
```
It checks each scene, renders it to `$RUN/renders/<id>.mp4`, and stitches them into `$RUN/<slug>.mp4`.
If a scene fails, send its error output to a **scene-builder** for that scene ("Fix this check/render failure: …"), then run `tools/env.sh python tools/assemble.py $RUN --only <id>`; this re-renders that scene and stitches again. One repair attempt per scene; if it still fails, log `render failed` and report it. Log `render`.

## 9. Report
Tell the user, briefly:
- the video path and its duration vs target
- the fact-check outcome (rounds, lines revised or deleted) and length-fit rounds
- the assumptions intake made (from `brief.json`), since the user never confirmed them
- time per stage (from `run_log.json`)
- anything that failed or needs a human look

Then send the MP4 to the user if a file-sending tool is available.
