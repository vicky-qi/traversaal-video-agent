# Step 2 Results: Agent Pipeline, First 60-Second Run

## Outcome
The first end-to-end run (`runs/smb-genai-test/`) produced a **56.0 s, 2-scene, 1080p narrated video** from a one-line prompt. All 8 narration lines were fact-checked as supported against 5 sources, and both scenes passed `hyperframes check` on the first render.

Prompt: *"How are small businesses actually using generative AI, and is it paying off? Make it useful for a small-business owner deciding whether to invest."*

| Stage | Result | Time |
|---|---|---|
| Intake | Brief with 2 research questions and 4 recorded assumptions | 21 s |
| Research (2 agents, parallel) | 11 facts from 5 sources; 1 conflict flagged (Chamber 58% vs Census ~18%) | 116 s |
| Script | 2 scenes, 10 lines | 49 s |
| Fact-check round 1 | 8 supported, **2 overstated** (generalized one survey to all owners) | 86 s |
| Revision + round 2 | 10/10 supported | 90 s |
| Voiceover (measured) | **83.8 s vs 60 s target, +40%** | 37 s |
| Trim pass | Deleted 2 lines, shortened 7 → 56.0 s | ~45 s* |
| Fact-check round 3 (final wording) | 8/8 supported | ~43 s* |
| Scene builders (2 agents, parallel) | Both check-clean; agents inspected their own snapshots | 110 s |
| Render + stitch | 2 × 13 s render, final 56.03 s | 61 s |

\*The run log shows longer times for these because the pipeline was being changed mid-run (see below). End-to-end agent time was about **10 minutes**.

## What the run changed in the design
1. **TTS reads numbers in full, so word counts underestimate length by ~25%.** "2025" becomes "twenty twenty-five". Number- and acronym-heavy lines ran at 115–135 wpm vs 180–190 for plain prose. Fixes:
   - `check_script.py` now counts *spoken* words (numbers expanded) at 145 wpm. Re-estimating the over-long script gave 83.9 s vs 83.8 s measured.
   - New **length-fit stage**: generate the voiceover (local, ~30 s), and if the total is > 15% off target, the scriptwriter trims using measured per-line seconds. Unchanged lines are cached, not re-voiced.
   - **Fact-check now runs after the length fit**, so it checks the final wording. Trimming had changed 7 lines that round 2 had already approved.
2. **Intake was deciding the answer before research.** The brief's angle asserted "the clearest payoff is time saved"; research found no measured time-savings data. The intake rule now makes the angle a working question, and the scriptwriter follows the evidence. In this run it correctly declined to claim measured savings.
3. **The fact-check loop catches real problems.** Both round-1 flags were genuine overgeneralizations (one program's alumni presented as "most owners"), the kind of error a single agent would ship.

## Known limitations to address in Steps 3–4
- **Source access.** Several primary sources (Goldman Sachs, Gusto, Bank of America) blocked automated fetching (HTTP 403), so researchers cited reprints (Business Wire, CPA Practice Advisor, Stock Titan). These are faithful but secondary. Options: the Traversaal Ares API, or a source-quality score in Step 4.
- **Self-reported data.** All payoff figures are owner surveys; the script says so, but a 7-minute video will need harder evidence.
- **Visual variety.** Scene builders produce clean but similar layouts (cards, bars). Add 2–3 more reference scenes (stat, chart, quote) before scaling to 10–15 scenes.
- **Run-log timing** measures time between log calls, so it is only accurate when the orchestrator logs immediately after each stage (it does when run via `/make-video`).
- **Not yet tested as native subagents.** In this run, each agent's instructions were executed through a general-purpose subagent, because the `.claude/agents/` folder was created mid-session. The next run should be `/make-video` in a fresh Claude Code session.

## Next: scale toward 7 minutes
1. Run `/make-video ... --minutes 2 --scenes 4` in a fresh session to confirm native agent loading and parallel scaling.
2. Add reference scenes for `stat`, `chart`, `quote`.
3. Then `--minutes 7 --scenes 12`; expect research and scene building to dominate time (both are parallel).
