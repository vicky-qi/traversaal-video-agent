# Traversaal Video Agent

UCLA Anderson MSBA capstone (MGMTMSA 412) for Traversaal.ai. We are building a tool inside Claude Code, made of skills and subagents, that turns **one prompt** into a **finished, narrated explainer video of about 7 minutes (MP4)** with little human involvement.

## Pipeline

Stages run in this order. Each stage reads the previous stage's file and writes its own, all inside `runs/<topic-slug>/`.

| # | Stage | Reads | Writes | Owner |
|---|---|---|---|---|
| 1 | Intake agent | the user's prompt | `01_brief.md` | Vicky |
| 2 | Research agents | `01_brief.md` | `02_research.md` | Vicky |
| 3 | Fact-check agent | `02_research.md` | `03_checked.md` | Jiaxin |
| 4 | Script agent | `01_brief.md`, `03_checked.md` | `04_script.json` | Julia |
| 5 | Voiceover | `04_script.json` | `audio/` (one file per scene) | Cynthia |
| 6 | Scene builder | `04_script.json`, `audio/`, `templates/` | `scenes/` | Jiaxin + Cynthia |
| 7 | Assembly | `scenes/`, `audio/` | `final.mp4` | Cynthia |

The `/make-video` skill (owner: Julia) runs all stages in order and stops at the first stage that fails.

## Key numbers

- About 1,000 words of narration (140–150 words per minute).
- 10–15 scenes of 30–45 seconds each (about 75–110 words per scene).
- The scene format is defined in `docs/scene-format.md`. Follow it exactly.

## Folder layout

- `.claude/agents/`: one subagent file per stage
- `.claude/skills/make-video/`: the workflow that runs everything
- `docs/`: scene format, visual style, rubric, meeting notes
- `render/`: rendering setup (HyperFrames or Remotion) and `render/README.md` with the exact render steps
- `templates/`: reusable scene templates
- `tests/prompts.md`: the shared test prompts; `tests/log.md`: one row per test run
- `runs/<topic-slug>/`: every output of one run

## Rules

- `<topic-slug>` is the topic in lowercase words joined by hyphens, for example `how-ev-batteries-work`.
- Only use facts that passed the fact-check stage. Never invent a source.
- Each person edits only the files they own. Announce changes to the scene format or this file in the group chat first.
- API keys go in `.env` only, never in the repo.
- After every test run, add a row to `tests/log.md`.
