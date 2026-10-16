# Run log: how-ev-batteries-work-2

Prompt: "How do electric vehicle batteries work?" · Run by Vicky (Claude as orchestrator, following .claude/skills/make-video/SKILL.md) · 2026-10-07

| Stage | Start | End | Result | Note |
|---|---|---|---|---|
| intake | 21:03:00 | 21:03:53 | ok | 7 key questions, 12 scenes, 440 s |
| research (old method, stopped) | 21:04:01 | 21:36:52 | stopped | One researcher for all 7 questions; still unfinished after 33 min, so switched to parallel |
| research (parallel, 7 researchers) | 21:38:24 | 21:52:43 | ok | 69 facts (9-10 per question), 42 SINGLE SOURCE flags, 70 sources; 14 min 19 s |
| fact-check (parallel, 7 checkers) | 21:53:06 | ~21:58-22:05 | ok | Verified 61, Overstated 6, Unsupported 2, Unreachable 0 (of 69). Q7 checker hit the account usage limit after saving its file |
| PAUSED | 22:12 | | waiting | Account usage limit reached (resets 1:40 am Pacific). Next: script stage |
| RESUMED | 22:14:49 | | ok | Usage limit had lifted |
| script | 22:15:00 | 22:26:04 | ok | 12 scenes, 1,046 words, check_script OK; types: title 2, image 3, bullets 4, chart 3; gaps in scenes 8-11 noted by scriptwriter |
| voiceover (length fit) | 22:26:09 | 22:29:40 | ok | 457.1 s vs 440 s target (+4%), LENGTH OK, no trim round needed; scene 5 longest (49.6 s, number-heavy) |
| script check, round 1 | 22:29:50 | 22:35:34 | FAIL | 6 of 12 scenes pass: overstated 3 (sc 3, 9, 10), unsupported 2 (sc 11, 12), uncited 1 (sc 1). Sent back for revision 1 |
| script revision 1 | 22:35:54 | 22:40:32 | ok | Fixed 6 failing scenes; narration of scenes 1, 2, 4-9 unchanged; 1,061 words; check_script OK |
| voiceover (after revision) | 22:40:42 | 22:41:07 | ok | Only changed sentences re-voiced (25 s); 464.8 s vs 440 s (+6%), LENGTH OK |
| script check, round 2 | 22:41:00 | 22:46:00 | FAIL | 11 of 12 scenes pass; scene 12 "sets the lifespan" OVERSTATED. Sent back for revision 2 |
| script revision 2 | 22:47:06 | 22:47:30 | ok | Scene 12 "sets the lifespan" -> "affects how fast they wear"; scene 10 adds "per kilowatt-hour"; scene 3 bullet adds "usually"; 1,065 words |
| voiceover (after revision 2) | 22:47:45 | 22:47:55 | ok | Scenes 10 and 12 re-voiced (10 s); 466.4 s (7 min 46 s), +6%, LENGTH OK |
| script check, round 3 | 22:48:00 | 22:50:30 | PASS | 12 of 12 scenes verified (changed scenes 3, 10, 12 checked fresh; others carried from round 2) |
| scenes | 22:51:23 | 22:53:03 | ok | 12 of 12 written, status complete, 466.44 s, no review flags; scenes 1, 2, 4, 6 use placeholder images |
| render | 22:53:09 | 22:56:21 | failed at scene 10 | Scenes 1-9 rendered; scene 10 failed hyperframes check (long bar-chart labels overlapped) |
| template fix + re-render | 22:56:30 | 23:00:35 | ok | Bar-chart label column now sizes to the longest label and rows grow; re-rendered scenes 5, 8, 10, 11, 12; all 12 pass check |

**Result:** `final.mp4`, 466.6 s (7 min 47 s), 12 scenes, 1920x1080, 22.8 MB.

**Active pipeline time: about 65 minutes** (not counting the stopped one-by-one research or the 10-minute pause for the account usage limit):
intake 1 · research 14 · fact-check 5 · script 11 · voiceover 4 · script check + 2 revisions 26 · scene files 2 · render 3 · template fix and re-render 4.

**Where the time goes:** the final-script fact-check loop (3 rounds, about 26 min) is now the biggest stage, then research (14) and script writing (11).
