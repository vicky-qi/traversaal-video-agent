# Traversaal Video Agent: the app

Owner: Vicky. The same pipeline as `/make-video`, packaged as a web app that anyone can use in a browser. Nobody needs Claude Code, a Claude Pro or Max plan, conda or a terminal: the person who hosts it sets one **Anthropic API key**, and everyone else just opens a link.

| | In Claude Code (`/make-video`) | As the app |
|---|---|---|
| Who can use it | People with Claude Code and a Claude Pro/Max plan | Anyone with the link (and the access code, if set) |
| How it is paid | The user's Claude subscription | The host's Anthropic API key, pay per use |
| What you install | Claude Code, conda env, the repo | Nothing (to use it); Docker (to host it) |
| Agents and workflow | `.claude/agents/`, `SKILL.md` | The same agent files; `SKILL.md` as Python in `app/pipeline.py` |

## Using it

1. Open the link and enter the access code.
2. Type what the video should explain (or click an example) and press **Make the video**.
3. Watch the stages tick off, or close the page and come back: the video keeps going on the server. A video takes about an hour.
4. When it is ready, play it in the page or press **Download MP4**. The **Report** shows the length, the fact-check results, the assumptions the brief made, and the time and API cost of each stage. The brief, research, checked facts, script and run log are linked below it.

Videos are made one at a time; later requests wait in line (at most 3 by default).

## Put it online (Hugging Face Spaces, free)

A Space is a free server that runs our Docker image and gives it a public link (2 CPUs, 16 GB of memory).

1. Get an API key: [console.anthropic.com](https://console.anthropic.com) → **API keys** → **Create key**, and add credit under **Billing**.
2. Create a Hugging Face account, then **New Space** → name it (for example `traversaal-video-agent`) → **Docker** → **Blank** → hardware **CPU basic (free)** → **Create Space**.
3. In the Space, **Settings** → **Variables and secrets** → **New secret**:
   - `ANTHROPIC_API_KEY`: the key from step 1
   - `APP_ACCESS_CODE`: any code you choose; give it to the people who should use the app
   - `VIDEO_MAX_COST_USD`: a spending cap per video, for example `40` (see Cost)
4. Create a Hugging Face access token with **write** access (**Settings** → **Access Tokens**), then from the repo root:

   ```bash
   HF_TOKEN=hf_... app/deploy_hf.sh <your-hf-username>/traversaal-video-agent
   ```

   This pushes the committed repo to the Space (it adds the header the Space needs to a copy of `README.md`; the GitHub README is not changed). The Space builds for 10–15 minutes, then the app is at `https://huggingface.co/spaces/<your-hf-username>/traversaal-video-agent`. Run the same command again after changing the code.

On the free hardware, rendering is slower than on a laptop, and the Space sleeps after 48 hours without visitors; finished videos are lost when it restarts, so download the ones you want to keep. Any other host that runs a Docker image works the same way (a cloud VM, Railway, Render): build the image and set the three variables. Avoid hosts that stop the container between web requests (such as Cloud Run), because a video runs for an hour in the background.

## Run it on your own computer (Docker)

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), then from the repo root:

```bash
docker build -t traversaal-video-agent .
docker run -p 7860:7860 -e ANTHROPIC_API_KEY=sk-ant-... -v "$PWD/runs:/home/user/app/runs" traversaal-video-agent
```

Open <http://localhost:7860>. The `-v` part keeps the finished videos in your `runs/` folder.

## Run it without Docker (team members)

Inside the `video` conda env from `render/README.md`:

```bash
render/env.sh pip install -r app/requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env          # .env is never committed
render/env.sh python -m uvicorn app.server:app --port 7860       # web app at http://localhost:7860
render/env.sh python -m app "How does compound interest work?"   # or: one video from the terminal
```

## Settings

All are environment variables (Space secrets, `docker run -e`, or lines in `.env`).

| Variable | Default | What it does |
|---|---|---|
| `ANTHROPIC_API_KEY` | (required) | The key every agent runs on |
| `APP_ACCESS_CODE` | none | Code the web page asks for. Set it whenever the app is online |
| `VIDEO_MAX_COST_USD` | no limit | Stops a video once its agents have cost this much |
| `VIDEO_MODEL` | `claude-opus-5-5` | Model for every agent |
| `VIDEO_MODEL_RESEARCHER` (or `_INTAKE`, `_FACT_CHECKER`, `_SCRIPTWRITER`, `_SCENE_BUILDER`) | `VIDEO_MODEL` | Model for one agent only |
| `VIDEO_MAX_PARALLEL` | `7` | How many researchers or fact-checkers run at once. Lower it (for example to `3`) if a new API account hits rate limits (429 errors) |
| `VIDEO_MAX_QUEUE` | `3` | How many requests may wait in line |
| `PORT` | `7860` | Web port inside the container |

## Cost

Each run's exact API cost is in its report and on the page, per stage. We have not measured a real run on an API key yet, so treat this as a rough estimate: with about 20 agent runs per video (7 researchers, 7 fact-checkers, the script writer and its revisions, up to 3 script checks, the scene builder), expect somewhere around **$10–30 per video** on Claude Opus 5.5 ($4 per million input tokens, $20 per million output tokens; web searches cost $10 per 1,000). Set `VIDEO_MAX_COST_USD` before sharing the link, check the first report, and adjust. The voiceover (Kokoro) and the render (HyperFrames) run on the server and cost nothing.

## How it works

| File | What it does |
|---|---|
| `app/server.py` | The web app (FastAPI): queue, access code, progress, downloads |
| `app/static/index.html` | The page |
| `app/pipeline.py` | `.claude/skills/make-video/SKILL.md` as code: the same stages, order, checks and repair loops (brief check, parallel research and fact-check with one retry, script format check, length fit, up to 3 final script checks then deleting failing sentences, scene files, render with one content fix). Writes `run_log.md`, `report.md` and `status.json` into `runs/<slug>/` |
| `app/agents.py` | Runs one agent from `.claude/agents/<name>.md` through the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk): the file's `tools:` line sets its tools and its body is the system prompt, plus `CLAUDE.md` as context |
| `app/__main__.py` | The same pipeline from the terminal |
| `Dockerfile` | One image with the `video` env from `environment.yml`, the render browser, the voice model and the app |

**Keeping the two versions in sync.** The agent files, the templates, `docs/` and the scripts in `render/` and `.claude/skills/make-video/` are shared: change them once and both `/make-video` and the app use the change. Only the orchestration is duplicated: if `SKILL.md` changes a stage, a limit or a prompt it sends to an agent, `app/pipeline.py` must change the same way.

**Guardrails.** The researcher and the fact-checker read arbitrary web pages, so `app/agents.py` enforces in code (not in the prompt) that agents write only inside `runs/`, never read `.env` or files outside the project, and never run network or environment-printing shell commands. Each agent gets only the tools its file lists. Videos still need the same human look as before: the report lists the review flags, thin questions and the intake agent's unconfirmed assumptions.
