"""Web app: type a prompt, get the finished video. No Claude account or Claude Code needed.

Start it from the repo root (see app/README.md):
    render/env.sh python -m uvicorn app.server:app --host 0.0.0.0 --port 7860

Videos are made one at a time (rendering is heavy, and it keeps the API spend predictable);
later requests wait in a queue. Set APP_ACCESS_CODE to keep strangers from spending the
API key on a public server.
"""
import asyncio
import os
import re
import secrets
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agents import REPO, RUNS, model_for
from .pipeline import FILES, STAGES, Job, Pipeline

ACCESS_CODE = os.environ.get("APP_ACCESS_CODE", "")
MAX_WAITING = int(os.environ.get("VIDEO_MAX_QUEUE") or 3)
STATIC = Path(__file__).parent / "static"
MEDIA = {".mp4": "video/mp4", ".md": "text/plain; charset=utf-8", ".json": "application/json"}

jobs: dict[str, Job] = {}
tasks: dict[str, asyncio.Task] = {}
queue: asyncio.Queue = asyncio.Queue()


def load_history():
    for path in RUNS.glob("*/status.json"):
        try:
            job = Job.load(path)
        except (OSError, ValueError, TypeError):
            continue
        if job.status in ("queued", "running"):
            job.status, job.error = "interrupted", "The server restarted while this video was being made."
            job.save()
        jobs[job.id] = job


async def worker():
    while True:
        job = jobs[await queue.get()]
        if job.status != "queued":  # cancelled while waiting
            continue
        tasks[job.id] = asyncio.create_task(Pipeline(job).run())
        await asyncio.wait([tasks[job.id]])
        tasks.pop(job.id, None)


@asynccontextmanager
async def lifespan(app):
    load_history()
    runner = asyncio.create_task(worker())
    yield
    runner.cancel()
    for task in tasks.values():
        task.cancel()


app = FastAPI(title="Traversaal Video Agent", lifespan=lifespan)


def check_code(request: Request):
    if not ACCESS_CODE:
        return
    given = request.headers.get("x-access-code") or request.query_params.get("code") or ""
    if not secrets.compare_digest(given.encode(), ACCESS_CODE.encode()):
        raise HTTPException(401, "Wrong or missing access code.")


def waiting_ids():
    return [j.id for j in sorted(jobs.values(), key=lambda j: j.created) if j.status == "queued"]


def public(job, events=False):
    data = asdict(job)
    if not events:
        data.pop("events")
    waiting = waiting_ids()
    data["queue_position"] = waiting.index(job.id) + 1 if job.id in waiting else None
    data["files"] = [f for f in FILES if job.dir and (job.dir / f).exists()]
    return data


def get_job(job_id):
    if job_id not in jobs:
        raise HTTPException(404, "No such video.")
    return jobs[job_id]


class NewVideo(BaseModel):
    prompt: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    prompts = (REPO / "tests" / "prompts.md").read_text() if (REPO / "tests" / "prompts.md").exists() else ""
    return {
        "access_code_required": bool(ACCESS_CODE),
        "api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model": model_for("researcher"),
        "max_cost_usd": float(os.environ.get("VIDEO_MAX_COST_USD") or 0) or None,
        "stages": [{"key": k, "name": n} for k, n in STAGES],
        "examples": re.findall(r"^\d+\. (.+)$", prompts, re.M)[:6],
    }


@app.get("/api/videos", dependencies=[Depends(check_code)])
def list_videos():
    return [public(j) for j in sorted(jobs.values(), key=lambda j: j.created, reverse=True)]


@app.post("/api/videos", dependencies=[Depends(check_code)])
async def create_video(body: NewVideo):
    prompt = " ".join(body.prompt.split())
    if not 3 <= len(prompt) <= 300:
        raise HTTPException(400, "Write a prompt of 3 to 300 characters.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "The server has no ANTHROPIC_API_KEY, so it cannot make videos yet.")
    if len(waiting_ids()) >= MAX_WAITING:
        raise HTTPException(429, f"{MAX_WAITING} videos are already waiting. Try again later.")
    job = Job(id=uuid.uuid4().hex[:12], prompt=prompt, created=datetime.now().isoformat(timespec="seconds"))
    job.log("waiting for its turn")
    jobs[job.id] = job
    await queue.put(job.id)
    return public(job)


@app.get("/api/videos/{job_id}", dependencies=[Depends(check_code)])
def get_video(job_id: str):
    return public(get_job(job_id), events=True)


@app.post("/api/videos/{job_id}/cancel", dependencies=[Depends(check_code)])
def cancel_video(job_id: str):
    job = get_job(job_id)
    if job.status == "queued":
        job.status, job.error = "cancelled", "Stopped by the user before it started."
    elif job.id in tasks:
        tasks[job.id].cancel()
    return public(job)


@app.get("/api/videos/{job_id}/files/{name}", dependencies=[Depends(check_code)])
def get_file(job_id: str, name: str, download: bool = False):
    job = get_job(job_id)
    if name not in FILES or not job.dir or not (job.dir / name).exists():
        raise HTTPException(404, "No such file.")
    filename = f"{job.slug}.mp4" if name == "final.mp4" else name
    return FileResponse(job.dir / name, media_type=MEDIA[Path(name).suffix],
                        filename=filename if download else None,
                        content_disposition_type="attachment" if download else "inline")
