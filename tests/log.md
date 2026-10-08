# Test log

One row per test run, newest first. This log becomes the Nov 15 progress report.

| Date | Who | Prompt # | Stage that failed or looked weakest | What we changed |
|---|---|---|---|---|
| Oct 7 | Vicky (Cynthia's part) | Template test (5 scenes) | Render: bar chart moved labels with `left` and the line chart's top label overflowed; `hyperframes check` caught both | Charts now animate with transforms; line chart has more headroom. All 5 types pass |
| Oct 7 | Vicky (Cynthia's part) | Julia's 2-scene example | Voiceover → scene builder → render worked end to end: 65.7 s video, voice within 6% of target, render about 45 s | First working MP4 on main |
| Oct 7 | Vicky (Jiaxin's part) | Fact-check trap (6 real + 2 false facts) | Fact-checker rejected both planted errors and verified all 6 real facts | Added rules for PDFs, paraphrased wording, warnings and weak quotes |
| Oct 7 | Vicky | 1 | Research: 54 facts from 47 pages, but most numbers SINGLE SOURCE; many official sites blocked (403/404); took about 29 minutes. Brief Q3 and Q6 asked for data that isn't published | Added a time budget, a fallback for blocked pages, a Source 2 line, and definitions of "independent" and "conflict"; year rules now refer to the year of the data |
| Oct 7 | Vicky | Extra: "AI and jobs" (vague) | Intake only. Brief OK: stated its assumptions, 12 scenes, 440 s | Clarified that years are allowed only as research instructions |
| Oct 7 | Vicky | 1 | Intake only. Brief OK: 7 specific questions, 12 scenes, 440 s, no invented facts | Removed the Glob tool (not available); check for an existing brief with Read |
