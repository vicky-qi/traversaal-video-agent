# capstone-video-agent

Agent pipeline that turns a prompt into a narrated, fact-checked MP4 explainer (UCLA Anderson MSBA capstone, sponsored by Traversaal.ai).

## Run it
`/make-video "<prompt>" --minutes 1 --scenes 2`. The orchestrator is `.claude/skills/make-video/SKILL.md`, and it calls the subagents in `.claude/agents/`.

## Conventions
- Run everything from the repo root, and run tools through `tools/env.sh` (activates the `video` conda env with Node, FFmpeg, Kokoro TTS). Example: `tools/env.sh npx hyperframes check runs/<slug>/scenes/s01`.
- One video = one folder `runs/<slug>/`. Stages talk only through files there: `prompt.txt` → `brief.json` → `research/<qid>.json` → `scenes.json` → `factcheck.json` → `scenes/<id>/{vo.wav,index.html}` → `renders/<id>.mp4` → `<slug>.mp4`. `run_log.json` records each stage's outcome and time.
- `scenes.json` is the hand-off format. Audio is generated first and visuals are timed to the measured audio (`timing` block), never the reverse.
- Narration is written normally; `tools/speech_text.py` rewrites it for the voice only (years, money, acronyms) and `templates/pronunciations.json` (all videos) and `runs/<slug>/pronunciations.json` (one video) hold respellings. The voiceover agent manages pronunciation; it never edits narration wording. Captions show the original text.
- Every factual narration sentence cites fact ids in `claims`; nothing the fact-checker has not marked `supported` reaches the voiceover.
- Each scene is a standalone HyperFrames composition in its own folder. The style lives in `templates/style-guide.md` and the reference scene is `templates/key_points.html`.
- `prototypes/` holds the Step 1 experiments; do not build on it.
