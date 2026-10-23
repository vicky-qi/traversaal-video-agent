# Traversaal Video Studio: quick start

Type a topic in a web page and get back a fact-checked, narrated **cinematic explainer** video (MP4): a short documentary-style film with animated pictures, camera moves, music, subtitles and a source for every fact. Built by Julia Low, Jiaxin Wu, Cynthia Jiang, Vicky Qi and Maggie Qu (UCLA Anderson MSBA, MGMTMSA 412) for Traversaal.ai.

## What you need

| | |
|---|---|
| Computer | A Mac (Apple silicon recommended) with at least 5 GB of free disk space |
| Claude | [Claude Code](https://claude.com/claude-code) installed, and a **Claude Pro or Max** plan (Max is recommended: one video runs many agents at once, and Pro's usage limit can pause a run) |
| conda | [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda |
| Internet | For research and the first-time downloads |

Nothing else is paid: the voice, music, sound effects and video rendering all run on your computer for free.

To see what the result looks like first, watch the finished example: `examples/snow-white/snow-white.mp4`.

## Set up (once, about 10 minutes)

1. Download the project and open a terminal in it:

   ```bash
   git clone https://github.com/vicky-qi/traversaal-video-agent.git
   cd traversaal-video-agent
   ```

2. Run:

   ```bash
   ./setup.sh
   ```

   It creates the video environment (FFmpeg, Node, Python), downloads HyperFrames and the local voice, and checks Claude Code.
3. Sign in to Claude Code once **in this folder**: run `claude`, type `/login`, sign in, and answer **Yes** when it asks whether you trust this folder. Then type `/exit`.

## Make a video

```bash
./start.sh
```

Your browser opens **Traversaal Video Studio** (http://127.0.0.1:8765). The setup check on the left should show only green ticks.

1. Type what the video should explain, for example "How do electric vehicle batteries work?"
2. Choose **2-minute demo** (about 40 minutes to make) or **7-minute film** (about 1–1.5 hours).
3. Click **Generate video** and watch the nine steps light up: brief, research, fact-check, script, voiceover, storyboard, final check, scenes, render.
4. When it finishes, the video plays in the page. **Download MP4** saves it; **Sources and checked facts** shows where every fact came from.

You can close the browser while it works; the run continues. Stop the app with Ctrl+C in the terminal.

## What happens inside

Claude Code runs a team of specialised agents on your computer (`.claude/agents/`), coordinated by the `make-video` workflow (`.claude/skills/make-video/SKILL.md`):

1. **Intake** turns your topic into a brief with a story and an art direction.
2. **Research** (one agent per question, in parallel) collects facts from opened web pages, each with its source.
3. **Fact-check** (in parallel) verifies every fact against its page and rejects anything overstated.
4. **Script** writes the narration as a three-act story, using only verified facts.
5. **Voiceover** records it with a local voice and measures every sentence.
6. **Storyboard** plans 4–8 shots per scene: what is seen, the camera move, any label.
7. **Final check** confirms that no sentence and no picture says more than the facts.
8. **Scenes** (one agent per scene, in parallel) animate each scene with [HyperFrames](https://hyperframes.heygen.com).
9. **Render** checks and renders every scene, joins them, and mixes music and sound effects under the voice.

Every file a run produces stays in `runs/<run name>/`.

## If something goes wrong

| What you see | What to do |
|---|---|
| A red cross in the setup check | Follow the line under it |
| "Not logged in" in a run | Sign in once in this folder (Set up, step 3) |
| A run stops partway ("Stopped before the video was finished") | The activity list says why (often Claude's usage limit: wait for it to reset). Then click **Continue this run**: it keeps the finished steps and picks up at the first unfinished one |
| A run keeps failing at Scenes or Render | Open the run's folder; `run_log.md` says which scene failed and why |

Runs use only the tools listed in `.claude/settings.json` and never ask questions while they run (`--permission-mode dontAsk`).
