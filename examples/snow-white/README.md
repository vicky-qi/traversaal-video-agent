# Example: Snow White

Prompt: **"Tell the story of Snow White as the Brothers Grimm wrote it, for a general audience"** · 2-minute demo · made from the web app with no human edits.

**Video:** [`snow-white.mp4`](snow-white.mp4) (117.8 s, 1920×1080). Frames: [`contact_sheet.png`](contact_sheet.png).

| Measure | Result |
|---|---|
| Length | 117.8 s (target 120 s) |
| Shots | 28 in 4 scenes (14.3 per minute, average 4.2 s) |
| Camera movement | 96% of shots (target at least 70%) |
| On-screen text | 14% of shots (target at most 30%) |
| Research | 53 facts from opened pages |
| Fact-check | 50 verified, 3 overstated and dropped |
| Final check | Passed in round 1, nothing removed |
| Working time | About 41 minutes |

## Files, in pipeline order

| File | Stage |
|---|---|
| `01_brief.md` | Intake: key questions, story spine, art direction |
| `research/q*.md` → `02_research.md` | Research, one file per question |
| `checked/q*.md` → `03_checked.md` | Fact-check, with the rejected facts and why |
| `04_script.json` | Script |
| `audio/timing.json`, `audio/subtitles.srt` | Voiceover timing and subtitles |
| `05_storyboard.json` | Storyboard: every shot, camera move and sound |
| `06_final_check.md` | Final check of script and storyboard |
| `scenes/scene_NN/scene.html` | The animated scenes, built in code |
| `run_log.md` | Time and result of every stage |

The run was stopped after the final check and continued the next day with **Continue this run**; `run_log.md` shows both parts.
