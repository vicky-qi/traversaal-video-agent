# Evaluation

How to measure the agent: the same four 7-minute topics, the same settings, every attempt recorded, and every finished video scored with [`rubric.md`](rubric.md) by two people who did not build it. The goal is numbers anyone can check: how often a run delivers, how good the films are, how many facts are wrong, and what a film costs in time.

## The four topics

Run each as a **7-minute film** from the web app with default settings (general audience, auto look, music on, no draft). Do not change the prompts once scoring has started.

| # | Prompt | Why it is in the set |
|---|---|---|
| E1 | What caused the 2008 financial crisis? | Economics: many numbers, dates and places to verify |
| E2 | How does a vaccine teach the immune system to fight a virus? | Science: a process the pictures must actually show |
| E3 | How did the printing press change Europe? | History: a story across centuries, few clean statistics |
| E4 | How do large language models like ChatGPT learn? | Technology: abstract ideas that are easy to overstate |

## Running

- One computer for every run; note its model and memory (RAM).
- Count **every attempt**, including failed ones. A run stopped by Claude's usage limit and finished with **Continue this run** counts as one attempt, with the wait noted.
- After each run, copy the stage times from the run's `run_log.md` into the sheet below.

## Sheet 1: runs

| Topic | Attempt | Date | Delivered? | Length | Working time | Usage-limit stops | Continues | Human help | Notes |
|---|---|---|---|---|---|---|---|---|---|
| E1 | 1 | | | | | | | | |

- **Delivered**: `final.mp4` exists, plays, and is at least 7:00 (the workflow keeps shorter films as `final.too-short.mp4`).
- **Working time**: from the run's start to `final.mp4`, minus time spent waiting for a usage limit to reset.
- **Human help**: anything a person did besides clicking Continue. Ideally none.

## Sheet 2: scores

Two scorers who did not build the system watch each delivered film once, then score it alone with [`rubric.md`](rubric.md). If their scores on a criterion differ by more than 1 point, they discuss and record both the original scores and the agreed one.

| Topic | Scorer | Clarity | Visual | Narration | Coherence | Accuracy | Cinematic | Average | Notes |
|---|---|---|---|---|---|---|---|---|---|
| E1 | | | | | | | | | |

A film with Accuracy 2 or lower fails, whatever its other scores.

## Sheet 3: fact spot-check

For each film, pick **10 factual sentences or on-screen numbers** at random (for example every fourth sentence in `audio/subtitles.srt` that states a fact). For each one, open its source page and record:

| Topic | Claim (as said in the film) | Fact ID | Source supports it? | Problem |
|---|---|---|---|---|
| E1 | | | yes / partly / no / page gone | |

Also count, from `03_checked.md` and `06_final_check.md`: facts researched, verified, rejected, and sentences or shots removed by the final check. Report **wrong facts found by people** separately from what the checker rejected: the checker's numbers show what it caught, the spot-check shows what it missed.

## Sheet 4: picture and sound problems

From watching the film and its `build/data_shots.png` (one frame from every shot that shows a number):

| Topic | Time | Problem | Kind |
|---|---|---|---|
| E1 | 5:49 | Empty box at the top for about a second | layout |

Kinds: number wrong or cut off, text covered, empty frame, picture contradicts narration, sound.

## What to report

- **Delivery**: delivered films / all attempts, per topic and overall.
- **Quality**: average score per criterion and overall; films that failed on accuracy.
- **Facts**: spot-checked claims, how many the source fully supports, and every error with its cause.
- **Time and cost**: working time per film, usage-limit stops, and the Claude plan used. Voice, music and rendering run locally at no extra cost.

## First results

| Topic | Attempt | Delivered | Length | Notes |
|---|---|---|---|---|
| E1 | 1 | yes | 7:28 | Oct 29: stopped once by the usage limit at scene building, finished with Continue; 70 facts researched, 62 verified, 2 shots removed by the final check. Not yet scored. |
