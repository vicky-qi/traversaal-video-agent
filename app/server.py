"""Traversaal Video Studio: a local web app around the make-video pipeline.

Start it with ./start.sh (or: render/env.sh python app/server.py), then open http://127.0.0.1:8765.
It only listens on this computer (127.0.0.1). Standard library only.

  - New video: writes runs/<slug>/request.json, then runs Claude Code headless
    (claude -p, permission mode dontAsk, allowlist in .claude/settings.json) to follow
    .claude/skills/make-video/SKILL.md. Output streams to runs/<slug>/agent_log.jsonl.
  - Progress: read from the files each stage writes (01_brief.md ... final.mp4).
  - Setup check: Claude Code, the video environment, disk space.
"""
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "runs"
STATIC = Path(__file__).resolve().parent / "static"
PORT = int(os.environ.get("STUDIO_PORT", "8765"))
SERVE_TYPES = {".md": "text/markdown; charset=utf-8", ".json": "application/json", ".srt": "text/plain; charset=utf-8",
               ".txt": "text/plain; charset=utf-8", ".mp4": "video/mp4", ".png": "image/png"}

STAGES = [
    ("intake", "Brief"), ("research", "Research"), ("factcheck", "Fact-check"), ("script", "Script"),
    ("voice", "Voiceover"), ("storyboard", "Storyboard"), ("check", "Final check"), ("scenes", "Scenes"),
    ("render", "Render"),
]


# ---------- Claude Code ----------

def find_claude():
    """The Claude Code command-line program: $CLAUDE_BIN, PATH, the usual install places, or the desktop app's copy."""
    cands = [os.environ.get("CLAUDE_BIN", ""), shutil.which("claude") or "",
             str(Path.home() / ".claude/local/claude"), str(Path.home() / ".local/bin/claude")]
    bundled = glob.glob(str(Path.home() / "Library/Application Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude"))
    bundled.sort(key=lambda p: [int(x) if x.isdigit() else 0 for x in re.split(r"[./]", p.split("claude-code/")[1].split("/")[0])])
    cands += list(reversed(bundled))
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def claude_version(binary):
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=20)
        return out.stdout.strip().splitlines()[0] if out.stdout.strip() else None
    except Exception:
        return None


def doctor():
    checks = []
    binary = find_claude()
    ver = claude_version(binary) if binary else None
    checks.append({"name": "Claude Code", "ok": bool(ver), "detail": ver or "Not found",
                   "fix": None if ver else "Install Claude Code (https://claude.com/claude-code). A Claude Pro or Max plan is needed."})
    first_run = f'In a terminal: cd "{REPO}" && "{binary or "claude"}"  then type /login, sign in, and accept the "trust this folder" prompt. Close it with /exit.'
    if ver:
        logged_in = False
        try:
            st = json.loads(subprocess.run([binary, "auth", "status", "--json"], capture_output=True, text=True, timeout=30).stdout or "{}")
            logged_in = bool(st.get("loggedIn"))
            how = st.get("authMethod") or ""
        except Exception:
            how = ""
        checks.append({"name": "Claude sign-in", "ok": logged_in, "detail": f"signed in ({how})" if logged_in else "Not signed in",
                       "fix": None if logged_in else first_run})
        trusted = False
        try:
            cfg = json.loads((Path.home() / ".claude.json").read_text())
            trusted = bool(((cfg.get("projects") or {}).get(str(REPO)) or {}).get("hasTrustDialogAccepted"))
        except Exception:
            pass
        checks.append({"name": "Project folder trusted", "ok": trusted, "detail": "yes" if trusted else "Not yet",
                       "fix": None if trusted else first_run})
    env_ok, env_detail = False, ""
    try:
        out = subprocess.run([str(REPO / "render/env.sh"), "ffmpeg", "-version"], capture_output=True, text=True, timeout=60)
        env_ok = out.returncode == 0
        env_detail = out.stdout.splitlines()[0][:60] if env_ok else (out.stderr.strip().splitlines() or ["error"])[-1][:160]
    except Exception as e:
        env_detail = str(e)[:160]
    checks.append({"name": "Video tools (conda env 'video')", "ok": env_ok, "detail": env_detail,
                   "fix": None if env_ok else "Run ./setup.sh in the project folder (it creates the environment with FFmpeg, Node and the voice)."})
    free_gb = shutil.disk_usage(REPO).free / 1e9
    checks.append({"name": "Free disk space", "ok": free_gb > 5, "detail": f"{free_gb:.0f} GB free",
                   "fix": None if free_gb > 5 else "Free up at least 5 GB."})
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


# ---------- runs ----------

def slugify(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    stop = {"the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "how", "what", "why", "do", "does", "is", "are"}
    words = [w for w in words if w not in stop][:5] or ["video"]
    return datetime.now().strftime("%m%d-%H%M") + "-" + "-".join(words)


def pid_alive(pid):
    try:
        if os.waitpid(pid, os.WNOHANG)[0]:  # a run started by this server has finished: reap it
            return False
    except (ChildProcessError, OSError, TypeError):
        pass  # not our child (started before a server restart)
    try:
        os.kill(pid, 0)
        return True
    except (OSError, TypeError):
        return False


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def log_summary(run):
    """Activity feed and result from Claude Code's stream-json log."""
    path = run / "agent_log.jsonl"
    feed, result = [], None
    if not path.exists():
        return feed, result
    for line in path.read_text(errors="replace").splitlines()[-600:]:
        try:
            ev = json.loads(line)
        except ValueError:
            if line.strip():  # Claude Code's own messages (stderr), e.g. a stop or a limit
                feed.append({"kind": "warn", "text": line.strip()[:600]})
            continue
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for part in (ev.get("message") or {}).get("content") or []:
                if part.get("type") == "text" and part.get("text", "").strip():
                    feed.append({"kind": "say", "text": part["text"].strip()[:600]})
                elif part.get("type") == "tool_use":
                    inp = part.get("input") or {}
                    name = part.get("name", "")
                    what = inp.get("description") or inp.get("command") or inp.get("file_path") or inp.get("skill") or ""
                    feed.append({"kind": "tool", "text": f"{name}: {str(what)[:160]}"})
        elif ev.get("type") == "result":
            result = {"ok": not ev.get("is_error") and ev.get("subtype") == "success",
                      "text": str(ev.get("result") or "")[:2000], "cost_usd": ev.get("total_cost_usd"),
                      "duration_s": round((ev.get("duration_ms") or 0) / 1000)}
    return feed[-40:], result


def run_created(run):
    """When the run started: request.json for app runs, else the earliest file of the run."""
    req = read_json(run / "request.json", {}) or {}
    if req.get("created"):
        return req["created"]
    times = [p.stat().st_mtime for p in run.rglob("*") if p.is_file()]
    return min(times) if times else run.stat().st_mtime


def stage_status(run):
    script = read_json(run / "04_script.json", {}) or {}
    n_scenes = len(script.get("scenes") or [])
    built = len(glob.glob(str(run / "scenes" / "scene_*" / "scene.html")))
    check_txt = (run / "06_final_check.md").read_text(errors="replace") if (run / "06_final_check.md").exists() else ""
    done = {
        "intake": (run / "01_brief.md").exists(),
        "research": (run / "02_research.md").exists(),
        "factcheck": (run / "03_checked.md").exists(),
        "script": (run / "04_script.json").exists(),
        "voice": (run / "audio" / "timing.json").exists(),
        "storyboard": (run / "05_storyboard.json").exists(),
        "check": bool(re.search(r"\bPASS\b", check_txt[-400:])),
        "scenes": n_scenes > 0 and built >= n_scenes,
        "render": (run / "final.mp4").exists(),
    }
    files = {"intake": "01_brief.md", "research": "02_research.md", "factcheck": "03_checked.md", "script": "04_script.json",
             "voice": "audio/subtitles.srt", "storyboard": "05_storyboard.json", "check": "06_final_check.md", "render": "final.mp4"}
    detail = {
        "research": f"{len(glob.glob(str(run / 'research' / 'q*.md')))} questions" if (run / "research").exists() else "",
        "factcheck": f"{len(glob.glob(str(run / 'checked' / 'q*.md')))} questions" if (run / "checked").exists() else "",
        "script": f"{n_scenes} scenes" if n_scenes else "",
        "scenes": f"{built} of {n_scenes}" if n_scenes else "",
        "check": "PASS" if done["check"] else ("FAIL, revising" if check_txt else ""),
    }
    created = run_created(run)
    out = []
    for key, label in STAGES:
        f = files.get(key)
        t = None
        if done[key] and f and (run / f).exists():
            t = max(0, round((run / f).stat().st_mtime - created))
        out.append({"key": key, "label": label, "done": done[key], "detail": detail.get(key, ""),
                    "file": f if f and (run / f).exists() else None, "at_s": t})
    return out


def run_info(slug, full=False):
    run = RUNS / slug
    req = read_json(run / "request.json", {}) or {}
    job = read_json(run / "job.json", {}) or {}
    stages = stage_status(run)
    feed, result = log_summary(run) if full or job else ([], None)
    running = bool(job.get("pid")) and pid_alive(job.get("pid"))
    if running:
        result = None  # helper agents emit their own result events; only the finished process has a final result
    finished = (run / "final.mp4").exists()
    if running:
        state = "running"
    elif finished:
        state = "done"
    elif job.get("cancelled"):
        state = "cancelled"
    elif job:
        state = "failed"
    else:
        state = "earlier run"
    title = req.get("prompt")
    if not title and (run / "01_brief.md").exists():
        m = re.search(r"^# Video Brief: (.+)$", (run / "01_brief.md").read_text(errors="replace"), re.M)
        title = m.group(1) if m else slug
    info = {"slug": slug, "title": title or slug, "minutes": req.get("minutes"), "state": state,
            "created": run_created(run), "stages": stages,
            "video": f"/files/{slug}/final.mp4" if finished else None}
    if full:
        info.update({"feed": feed, "result": result, "elapsed_s": round(time.time() - info["created"]) if running else None})
    return info


def list_runs():
    out = []
    if RUNS.exists():
        for d in RUNS.iterdir():
            if d.is_dir() and ((d / "request.json").exists() or (d / "01_brief.md").exists() or (d / "final.mp4").exists()):
                try:
                    out.append(run_info(d.name))
                except Exception:
                    pass
    return sorted(out, key=lambda r: r["created"], reverse=True)


def start_run(prompt, minutes):
    binary = find_claude()
    if not binary:
        raise RuntimeError("Claude Code was not found. See the setup check.")
    slug = slugify(prompt)
    run = RUNS / slug
    run.mkdir(parents=True, exist_ok=False)
    (run / "request.json").write_text(json.dumps({"prompt": prompt, "minutes": minutes, "created": time.time()}, indent=2))
    instruction = (
        "Run the make-video workflow: read .claude/skills/make-video/SKILL.md and follow it exactly, from step 0 to the report. "
        f"Arguments: --slug {slug} --minutes {minutes}. This run is headless (started from the Traversaal Video Studio web app): "
        "never ask the user a question; make sensible choices and note them in run_log.md. "
        f"The user's prompt is: \"{prompt}\""
    )
    launch(binary, run, instruction, "w")
    return slug


def resume_run(slug):
    """Continue a stopped run from its first unfinished stage; finished stages are kept."""
    binary = find_claude()
    if not binary:
        raise RuntimeError("Claude Code was not found. See the setup check.")
    run = RUNS / slug
    req = read_json(run / "request.json", {}) or {}
    job = read_json(run / "job.json", {}) or {}
    if not req.get("prompt"):
        raise RuntimeError("Only runs started from this app can be continued.")
    if job.get("pid") and pid_alive(job["pid"]):
        raise RuntimeError("This run is still running.")
    if (run / "final.mp4").exists():
        raise RuntimeError("This run already has its video.")
    instruction = (
        "Resume the make-video workflow: read .claude/skills/make-video/SKILL.md and follow its Resume section, then continue "
        "from the first unfinished stage to the report. "
        f"Arguments: --slug {slug} --minutes {req.get('minutes', 2)}. This run is headless (started from the Traversaal Video "
        "Studio web app): never ask the user a question; make sensible choices and note them in run_log.md. "
        f"The user's original prompt was: \"{req['prompt']}\""
    )
    launch(binary, run, instruction, "a")


def launch(binary, run, instruction, log_mode):
    log = open(run / "agent_log.jsonl", log_mode)
    # In -p mode Claude Code stops background subagents 10 minutes after the main agent's last turn;
    # scene builders often need longer, so wait for them.
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    proc = subprocess.Popen([binary, "-p", instruction, "--output-format", "stream-json", "--verbose",
                             "--permission-mode", "dontAsk"],
                            cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            start_new_session=True)
    (run / "job.json").write_text(json.dumps({"pid": proc.pid, "started": time.time(), "claude": binary}))


def cancel_run(slug):
    job_path = RUNS / slug / "job.json"
    job = read_json(job_path, {}) or {}
    if job.get("pid") and pid_alive(job["pid"]):
        try:
            os.killpg(job["pid"], signal.SIGTERM)
        except OSError:
            pass
    job["cancelled"] = True
    job_path.write_text(json.dumps(job))


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, ctype):
        size = path.stat().st_size
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if a and b else size - 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        try:
            if path in ("/", "/index.html"):
                return self.send_file(STATIC / "index.html", "text/html; charset=utf-8")
            if path == "/api/doctor":
                return self.send_json(doctor())
            if path == "/api/runs":
                return self.send_json(list_runs())
            m = re.fullmatch(r"/api/runs/([A-Za-z0-9._-]+)", path)
            if m and (RUNS / m.group(1)).is_dir():
                return self.send_json(run_info(m.group(1), full=True))
            m = re.fullmatch(r"/files/([A-Za-z0-9._-]+)/([A-Za-z0-9._/-]+)", path)
            if m:
                target = (RUNS / m.group(1) / m.group(2)).resolve()
                if str(target).startswith(str((RUNS / m.group(1)).resolve())) and target.is_file() and target.suffix in SERVE_TYPES:
                    return self.send_file(target, SERVE_TYPES[target.suffix])
            self.send_json({"error": "not found"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self.send_json({"error": "bad JSON"}, 400)
        try:
            if path == "/api/runs":
                prompt = str(body.get("prompt", "")).strip()
                minutes = body.get("minutes", 2)
                if not 8 <= len(prompt) <= 400:
                    return self.send_json({"error": "Write a topic of 8 to 400 characters."}, 400)
                if minutes not in (2, 7):
                    return self.send_json({"error": "Length must be 2 or 7 minutes."}, 400)
                return self.send_json({"slug": start_run(prompt, minutes)})
            m = re.fullmatch(r"/api/runs/([A-Za-z0-9._-]+)/cancel", path)
            if m and (RUNS / m.group(1)).is_dir():
                cancel_run(m.group(1))
                return self.send_json({"ok": True})
            m = re.fullmatch(r"/api/runs/([A-Za-z0-9._-]+)/resume", path)
            if m and (RUNS / m.group(1)).is_dir():
                resume_run(m.group(1))
                return self.send_json({"ok": True})
            self.send_json({"error": "not found"}, 404)
        except RuntimeError as e:
            self.send_json({"error": str(e)}, 400)


def main():
    RUNS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Traversaal Video Studio: http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(main())
