| Stage | Start | End | Result | Note |
|---|---|---|---|---|
| intake | 17:26:22 | 17:27:14 | ok | 6 questions; 4 scenes x 30 s = 120 s. Headless choice: outline scaled to the 2-minute target instead of 10-15 scenes / 400-450 s |
| research | 17:27:14 | 17:37:33 | ok | 6 researchers in parallel, 53 facts (q1 10, q2 8, q3 8, q4 9, q5 10, q6 8); edition followed: 1857 |
| fact-check | 17:37:33 | 17:40:03 | ok | 6 checkers in parallel: Verified 50, Overstated 3 (Q1-F2, Q5-F1, Q6-F5), Unsupported 0, Unreachable 0; every question has verified facts |
| script | 17:40:03 | 17:42:43 | ok | 312 words, 4 scenes; check_script.py OK on first pass (scriptwriter's own Bash was blocked, orchestrator ran the check) |
| length-fit | 17:42:43 | 17:44:11 | ok | measured 117.7 s vs 120 s target (-2%), LENGTH OK in round 1 |
| storyboard | 17:44:11 | 17:46:27 | ok | shots: 28 (14.3 per minute), average 4.2s, camera movement 96%, on-screen text 14%; OK first pass |
| final-check | 17:46:27 | 17:48:00 | ok | PASS in round 1: 4/4 scenes verified, 34 sentences and 28 shots checked; nothing removed. Checker's note about 312 words vs ~1,000 ignored: this run's target is 2 minutes |
| resume | 13:05:19 | 13:05:40 | ok | continuing at scenes (stages 1-7 finished; storyboard re-checked OK, 06_final_check.md ends with PASS) |
| scenes | 13:05:40 | 13:22:15 | ok | 4 builders in parallel; all 4 scene.html pass render.py --check-only on first launch (only shell-layout lint warnings) |
| render | 13:22:15 | 13:25:06 | ok | final.mp4 117.8 s vs 120 s target; 4 scenes all checked and rendered; music bed (tense) + 18 sound effects. Two blank-frame suspects in scene 1 (frames 833-834) re-captured automatically |
