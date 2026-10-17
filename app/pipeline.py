"""The /make-video workflow as plain Python: one prompt in, runs/<slug>/final.mp4 out.

This is .claude/skills/make-video/SKILL.md (Julia's) turned into code, so the pipeline runs
without anyone opening Claude Code: the same stages in the same order, the same agents
(.claude/agents/*.md), the same helper scripts (check_script.py, merge_parts.py,
render/voiceover.py, render/render.py) and the same repair limits. The agents' own
files are read fresh on every run, so changing an agent changes the app too. If SKILL.md
changes its stages or limits, change this file to match.
"""
import asyncio
import json
import os
import re
import shutil
import signal
import sys
import time
import traceback
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from .agents import REPO, RUNS, AgentError, run_agent

SKILL = REPO / ".claude" / "skills" / "make-video"
TOOLS = "render/env.sh"  # runs FFmpeg, Node and the voice model inside the `video` conda env
TARGET_SEC = 420

STAGES = [
    ("intake", "Brief"),
    ("research", "Research"),
    ("fact-check", "Fact-check"),
    ("script", "Script"),
    ("length-fit", "Voiceover"),
    ("script-check", "Script fact-check"),
    ("scenes", "Scene files"),
    ("render", "Render"),
]
# Files of a run the web app may serve.
FILES = ["final.mp4", "report.md", "01_brief.md", "02_research.md", "03_checked.md",
         "04_script.json", "05_script_check.md", "run_log.md"]


class StageError(RuntimeError):
    """A stage failed and the workflow could not repair it."""


def clock():
    return datetime.now().strftime("%H:%M:%S")


def tail(text, n=12):
    return "\n".join(text.strip().splitlines()[-n:])


def last_line(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    return lines[-1][:300] if lines else "no output"


@dataclass
class Job:
    id: str
    prompt: str
    created: str
    status: str = "queued"          # queued, running, done, failed, cancelled, interrupted
    slug: str | None = None
    stages: dict = field(default_factory=lambda: {key: {"status": "pending"} for key, _ in STAGES})
    events: list = field(default_factory=list)
    cost_usd: float = 0.0
    error: str | None = None
    summary: dict = field(default_factory=dict)

    @property
    def dir(self):
        return RUNS / self.slug if self.slug else None

    def log(self, text, stage=None):
        self.events.append({"t": clock(), "stage": stage, "text": text})
        del self.events[:-500]

    def save(self):
        if self.dir and self.dir.exists():
            (self.dir / "status.json").write_text(json.dumps(asdict(self), indent=1) + "\n")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def parse_brief(text):
    """(key questions, outline rows, outline seconds), read the way merge_parts.py reads the brief."""
    kq = re.search(r"## Key questions for research\n(.*?)\n## ", text, re.S)
    questions = len(re.findall(r"^\d+\. ", kq.group(1), re.M)) if kq else 0
    outline = re.search(r"## Scene outline\n(.*?)(?=\n## |\Z)", text, re.S)
    rows = [l for l in outline.group(1).splitlines() if re.match(r"^\|\s*\d+\s*\|", l)] if outline else []
    seconds = 0
    for row in rows:
        m = re.search(r"(\d+)\s*\|\s*$", row)
        seconds += int(m.group(1)) if m else 0
    return questions, len(rows), seconds


def brief_problems(questions, rows, seconds):
    problems = []
    if not 5 <= questions <= 7:
        problems.append(f"it has {questions} key questions; it needs 5-7")
    if not 10 <= rows <= 15:
        problems.append(f"the scene outline has {rows} rows; it needs 10-15")
    if not 400 <= seconds <= 450:
        problems.append(f"the outline adds up to {seconds} seconds; it needs 400-450")
    return problems


def parse_script_check(text):
    """(PASS/FAIL/None, rows of scenes that did not pass) from 05_script_check.md."""
    verdicts = re.findall(r"^[\W_]*(?:(?i:overall|result|verdict)[\W_]*)?(PASS|FAIL)\b", text, re.M)
    rows = [l[:800] for l in text.splitlines()
            if re.match(r"^\|\s*\d+\s*\|", l) and not re.match(r"^\|\s*\d+\s*\|\s*\**\s*(VERIFIED|PASS)\b", l)]
    return (verdicts[-1] if verdicts else None), rows


class Pipeline:
    def __init__(self, job):
        self.job = job
        self.max_cost = float(os.environ.get("VIDEO_MAX_COST_USD") or 0) or None
        self.limit = asyncio.Semaphore(int(os.environ.get("VIDEO_MAX_PARALLEL") or 7))
        self.current = None
        self.questions = 0
        self.researched = []
        self.revisions = 0
        self.facts = {}

    # ---- plumbing -------------------------------------------------------------------

    @property
    def slug(self):
        return self.job.slug

    @property
    def dir(self):
        return self.job.dir

    def log(self, text):
        self.job.log(text, self.current)

    def run_log(self, stage, st, result, note):
        path = self.dir / "run_log.md" if self.dir else None
        if path and path.exists():
            note = " ".join(str(note).split()).replace("|", "/")[:300]
            with path.open("a") as f:
                f.write(f"| {stage} | {st.get('start', '')} | {st.get('end', '')} | {result} | {note} |\n")

    def start_run_log(self):
        path = self.dir / "run_log.md"
        if not path.exists():
            path.write_text(
                f"# Run log: {self.slug}\n\n"
                f"Prompt: \"{self.job.prompt}\" · Run by the web app (app/pipeline.py, following "
                f".claude/skills/make-video/SKILL.md) · {datetime.now():%Y-%m-%d}\n\n"
                "| Stage | Start | End | Result | Note |\n|---|---|---|---|---|\n")

    @asynccontextmanager
    async def stage(self, key):
        st = self.job.stages[key]
        st.update(status="running", start=clock())
        self.current = key
        t0, cost0 = time.monotonic(), self.job.cost_usd
        self.job.save()
        try:
            yield st
        except BaseException as e:
            cancelled = isinstance(e, asyncio.CancelledError)
            st.update(status="cancelled" if cancelled else "failed", end=clock(),
                      note="stopped by the user" if cancelled else str(e).splitlines()[0][:300])
            self.run_log(key, st, "stopped" if cancelled else "failed", st["note"])
            raise
        else:
            st.update(status="done", end=clock())
            self.run_log(key, st, "ok", st.get("note", ""))
        finally:
            st.update(seconds=round(time.monotonic() - t0), cost=round(self.job.cost_usd - cost0, 4))
            self.job.save()

    async def agent(self, name, prompt, label=None, resume=None, share=1):
        budget = None
        if self.max_cost:
            left = self.max_cost - self.job.cost_usd
            if left <= 0:
                raise StageError(f"The cost limit (VIDEO_MAX_COST_USD = ${self.max_cost:.2f}) was reached.")
            budget = left / share
        label = label or name
        self.log(f"{label}: started")
        try:
            run = await run_agent(name, prompt, resume=resume, budget_usd=budget,
                                  on_event=lambda text: self.log(f"{label}: {text}"))
        except AgentError as e:
            self.job.cost_usd += e.cost
            raise StageError(str(e)) from e
        except Exception as e:  # the SDK could not start or lost the agent process
            raise StageError(f"{label}: {e}") from e
        self.job.cost_usd += run.cost
        self.log(f"{label}: done ({run.turns} turns, ${run.cost:.2f})")
        return run

    async def parallel(self, name, prompts):
        """Run one agent per question at the same time; return the question numbers that failed."""
        async def one(n, prompt):
            async with self.limit:
                try:
                    await self.agent(name, prompt, label=f"{name} Q{n}", share=len(prompts))
                except StageError as e:
                    self.log(f"{name} Q{n} failed: {e}")
                    return n
        return [n for n in await asyncio.gather(*(one(n, p) for n, p in prompts.items())) if n]

    async def sh(self, *args, show=None):
        """Run a command from the repo root; return (exit code, output).
        Output lines matching the regex `show` go to the progress feed."""
        proc = await asyncio.create_subprocess_exec(
            *args, cwd=REPO, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}, start_new_session=True)
        lines = []
        try:
            async for raw in proc.stdout:
                line = raw.decode(errors="replace").rstrip()
                lines.append(line)
                if show and re.search(show, line):
                    self.log(line[:240])
            code = await proc.wait()
        except asyncio.CancelledError:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            raise
        return code, "\n".join(lines)

    def path(self, name):
        return self.dir / name

    def archive(self, name):
        """Rename runs/<slug>/<name> to <stem>.v<N><suffix> (N = next free number), as SKILL.md does."""
        p = self.path(name)
        if not p.exists():
            return None
        n = 1
        while (old := p.with_name(f"{p.stem}.v{n}{p.suffix}")).exists():
            n += 1
        p.rename(old)
        return old

    # ---- shared steps ---------------------------------------------------------------

    async def merge(self, kind):
        code, out = await self.sh(sys.executable, str(SKILL / "merge_parts.py"), f"runs/{self.slug}", kind)
        m = re.search(r"MISSING part files for questions: \[([\d, ]*)\]", out)
        missing = [int(x) for x in m.group(1).split(",") if x.strip()] if m else []
        if code not in (0, 1) or (code == 1 and not m):
            raise StageError(f"merge_parts.py {kind} failed: {last_line(out)}\n{tail(out)}")
        return missing, out

    async def check_script(self):
        code, out = await self.sh(sys.executable, str(SKILL / "check_script.py"), f"runs/{self.slug}/04_script.json")
        return [l for l in out.splitlines() if l.startswith("FAIL")]

    async def revise(self, problems):
        """SKILL.md's Revisions: archive the script, have the script writer fix it, check the format.
        One extra revision is allowed for format problems the fix itself introduced."""
        for attempt in (1, 2):
            old = self.archive("04_script.json")
            if old is None:
                raise StageError("There is no 04_script.json to revise.")
            self.revisions += 1
            try:
                await self.agent(
                    "scriptwriter",
                    f"Topic slug: {self.slug}. Revision pass. Start from `{old.name}` and keep everything "
                    f"that is not mentioned below exactly the same. Fix: {problems}",
                    label=f"scriptwriter (revision {self.revisions})")
            finally:
                if not self.path("04_script.json").exists():
                    shutil.copy(old, self.path("04_script.json"))
            if self.path("04_script.json").read_bytes() == old.read_bytes():
                raise StageError("The script writer did not write a revised script.")
            fails = await self.check_script()
            if not fails:
                return
            problems = "check_script.py found these problems:\n" + "\n".join(fails)
        raise StageError("The revised script still fails check_script.py:\n" + "\n".join(fails))

    async def voiceover(self):
        """(exit code, output, (total, target, off) or None). Exit 2 means the length is off."""
        code, out = await self.sh(TOOLS, "python", "render/voiceover.py", f"runs/{self.slug}",
                                  show=r"^(scene_\d+:|total:|LENGTH)")
        if code not in (0, 2):
            raise StageError(f"The voiceover failed: {last_line(out)}\n{tail(out)}")
        m = re.search(r"total: ([\d.]+)s vs script target (\d+)s \(([+-]?\d+%)\)", out)
        return code, out, m.groups() if m else None

    async def build_scenes(self):
        for attempt in (1, 2):
            await self.agent("scene-builder", f"Topic slug: {self.slug}.")
            try:
                index = json.loads(self.path("scenes/index.json").read_text())
            except (OSError, ValueError):
                index = {"status": "missing", "problems": [{"reason": "scenes/index.json was not written"}]}
            if index.get("status") == "complete":
                return index
            problems = index.get("problems") or []
            self.log(f"scene files incomplete: {problems}")
            if attempt == 2:
                raise StageError(f"The scene files are still incomplete: {problems}")
            content = [p for p in problems if "audio" not in str(p.get("reason", ""))]
            if content:
                await self.revise("The scene builder could not build these scenes: "
                                  + "; ".join(f"scene {p.get('scene_id')}: {p.get('reason')}" for p in content)
                                  + ". Make each one's visual_type and visual_content follow docs/scene-format.md exactly.")
            await self.voiceover()

    # ---- stages ---------------------------------------------------------------------

    async def check_tools(self):
        code, out = await self.sh(TOOLS, "ffmpeg", "-version")
        if code:
            raise StageError("The video tools are not set up (render/env.sh ffmpeg -version failed). "
                             f"See render/README.md.\n{tail(out, 4)}")

    async def intake(self):
        async with self.stage("intake") as st:
            before = {p.parent.name for p in RUNS.glob("*/01_brief.md")}
            run = await self.agent("intake", f'Video prompt: "{self.job.prompt}"')
            new = sorted({p.parent.name for p in RUNS.glob("*/01_brief.md")} - before)
            if len(new) != 1:
                raise StageError(f"The intake agent did not write exactly one new brief (found: {new or 'none'}).")
            self.job.slug = new[0]
            self.start_run_log()
            counts = parse_brief(self.path("01_brief.md").read_text())
            problems = brief_problems(*counts)
            if problems:
                self.log("brief check: " + "; ".join(problems))
                await self.agent(
                    "intake",
                    f"The brief you just wrote, runs/{self.slug}/01_brief.md, fails these checks: "
                    f"{'; '.join(problems)}. Fix that same file (overwriting your own brief from this run is "
                    "expected here) and reply with the same summary.",
                    label="intake (fix)", resume=run.session_id)
                counts = parse_brief(self.path("01_brief.md").read_text())
                problems = brief_problems(*counts)
            self.questions = counts[0]
            if not self.questions:
                raise StageError("The brief has no key questions to research.")
            st["note"] = f"{counts[0]} key questions, {counts[1]} scenes, {counts[2]} s" + (
                f"; still off: {'; '.join(problems)}" if problems else "")

    async def research(self):
        async with self.stage("research") as st:
            prompts = {n: f"Topic slug: {self.slug}. Question number: {n}." for n in range(1, self.questions + 1)}
            await self.parallel("researcher", prompts)
            missing, out = await self.merge("research")
            if missing:
                self.log(f"no research file for questions {missing}; launching those researchers once more")
                await self.parallel("researcher", {n: prompts[n] for n in missing})
                missing, out = await self.merge("research")
            self.researched = [n for n in prompts if n not in missing]
            if not self.researched:
                raise StageError("No researcher finished; there is nothing to fact-check.")
            for n in self.researched:
                text = self.path(f"research/q{n}.md").read_text()
                self.facts[n] = len(re.findall(rf"^- \*\*Q{n}-F\d+\*\*", text, re.M))
            thin = [f"Q{n}" for n, c in self.facts.items() if c < 2]
            st["note"] = (f"{sum(self.facts.values())} facts from {len(self.researched)} parallel researchers"
                          + (f"; missing {', '.join(f'Q{n}' for n in missing)}" if missing else "")
                          + (f"; under 2 facts: {', '.join(thin)}" if thin else ""))

    async def fact_check(self):
        async with self.stage("fact-check") as st:
            prompts = {n: f"Topic slug: {self.slug}. Mode 1. Question number: {n}." for n in self.researched}
            await self.parallel("fact-checker", prompts)
            missing, out = await self.merge("checked")
            retry = [n for n in missing if n in prompts]
            if retry:
                self.log(f"no fact-check file for questions {retry}; launching those checkers once more")
                await self.parallel("fact-checker", {n: prompts[n] for n in retry})
                missing, out = await self.merge("checked")
            counts = {k: int(v) for k, v in re.findall(r"(Verified|Overstated|Unsupported|Unreachable) (\d+)", out)}
            self.job.summary["fact_check"] = counts
            if not counts.get("Verified"):
                raise StageError("No fact passed the fact-check, so there is nothing true to narrate.")
            empty = [f"Q{n}" for n in self.researched if self.path(f"checked/q{n}.md").exists()
                     and "Check: VERIFIED" not in self.path(f"checked/q{n}.md").read_text()]
            self.job.summary["thin_questions"] = empty
            st["note"] = ", ".join(f"{k} {v}" for k, v in counts.items()) + (
                f"; no verified facts for {', '.join(empty)}" if empty else "")

    async def script(self):
        async with self.stage("script") as st:
            if self.path("04_script.json").exists():
                raise StageError(f"runs/{self.slug}/04_script.json already exists; the script writer never overwrites one.")
            run = await self.agent("scriptwriter", f"Topic slug: {self.slug}.")
            if not self.path("04_script.json").exists():
                raise StageError("The script writer did not write 04_script.json.")
            fails = await self.check_script()
            if fails:
                await self.revise("check_script.py found these problems:\n" + "\n".join(fails))
            script = json.loads(self.path("04_script.json").read_text())
            types = {}
            for s in script["scenes"]:
                types[s["visual_type"]] = types.get(s["visual_type"], 0) + 1
            self.job.summary["scriptwriter_reply"] = run.text[-1500:]
            st["note"] = (f"{len(script['scenes'])} scenes, {script.get('total_words')} words; "
                          + ", ".join(f"{k} {v}" for k, v in types.items()))

    async def length_fit(self):
        async with self.stage("length-fit") as st:
            for rnd in range(3):
                code, out, total = await self.voiceover()
                if code == 0 or rnd == 2:
                    break
                lines = [l for l in out.splitlines() if l.startswith(("scene_", "total:", "LENGTH"))]
                long = "LENGTH LONG" in out
                await self.revise(
                    f"The real voiceover is too {'long' if long else 'short'}. Measured with the voice:\n"
                    + "\n".join(lines)
                    + f"\nBring the total within 15% of the target by {'trimming' if long else 'extending'} the "
                    "narration of the scenes furthest from their target seconds. Keep every fact, number and source.")
            if total:
                self.job.summary["voice_seconds"] = float(total[0])
            st["note"] = (f"{total[0]} s vs {total[1]} s target ({total[2]})" if total else "measured")
            if code == 2:
                st["note"] += "; still off after 2 trim rounds"

    async def script_check(self):
        async with self.stage("script-check") as st:
            rounds, fixes, deleted = 0, 0, 0
            while True:
                rounds += 1
                self.archive("05_script_check.md")
                run = await self.agent("fact-checker", f"Topic slug: {self.slug}. Check the script (Mode 2).",
                                       label=f"fact-checker (script, round {rounds})")
                if not self.path("05_script_check.md").exists():
                    raise StageError("The fact-checker did not write 05_script_check.md.")
                verdict, failing = parse_script_check(self.path("05_script_check.md").read_text())
                verdict = verdict or ("PASS" if run.text.strip().upper().startswith("PASS") else "FAIL")
                self.log(f"script check round {rounds}: {verdict}" + (f", {len(failing)} scenes failing" if failing else ""))
                if verdict == "PASS":
                    break
                rows = "\n".join(failing) or f"See runs/{self.slug}/05_script_check.md."
                if fixes == 2:
                    await self.revise(
                        "Delete every sentence that failed the final fact-check below (narration and on-screen "
                        "text). Do not reword them and do not add anything: unverified claims never reach the "
                        f"video.\n{rows}")
                    deleted = len(failing)
                    break
                fixes += 1
                await self.revise(
                    f"The final fact-check (runs/{self.slug}/05_script_check.md) failed these scenes:\n{rows}\n"
                    "Fix each failing sentence so it says only what its verified fact supports, and add any "
                    "missing source URL to that scene's sources.")
            if fixes or deleted:
                code, out, total = await self.voiceover()
                if total:
                    self.job.summary["voice_seconds"] = float(total[0])
                if code == 2:
                    self.log("length warning after the script fixes (logged, not looped on, as SKILL.md says)")
            self.job.summary.update(script_check_rounds=rounds, scenes_with_deleted_sentences=deleted)
            st["note"] = (f"PASS in round {rounds}" if not deleted
                          else f"still failing after {rounds} rounds; failing sentences deleted in {deleted} scenes")

    async def scenes(self):
        async with self.stage("scenes") as st:
            index = await self.build_scenes()
            flags = []
            for entry in index.get("scenes", []):
                scene = self.path(f"scenes/scene_{int(entry['id']):02d}.json")
                if scene.exists():
                    flags += [f"scene {entry['id']}: {f}" for f in json.loads(scene.read_text()).get("review_flags") or []]
            self.job.summary["review_flags"] = flags
            st["note"] = (f"{len(index.get('scenes', []))} of {index.get('scene_count')} written, "
                          f"{index.get('total_duration_sec')} s" + (f"; {len(flags)} review flags" if flags else ""))

    async def render(self):
        async with self.stage("render") as st:
            for attempt in (1, 2):
                code, out = await self.sh(TOOLS, "python", "render/render.py", f"runs/{self.slug}",
                                          show=r"^\s*(scene_\d+[ :]|rendered |warning|final\.mp4|\w+: )")
                if code == 0:
                    break
                m = re.search(r"scene_(\d+): hyperframes check found errors\n(.*?)(?=\n\S|\Z)", out, re.S)
                if not m:
                    raise StageError(f"The render failed: {last_line(out)}\n{tail(out)}")
                n, findings = int(m.group(1)), m.group(2).strip() or "(no details printed)"
                # SKILL.md: text that does not fit is the script's to fix; anything else (a script error,
                # a missing file, no network) is a template or server problem, so stop and report it.
                if attempt == 2 or "runtime:" in findings or "layout:" not in findings:
                    raise StageError(f"The render check failed on scene {n}: {findings.splitlines()[0].strip()}\n{findings}")
                try:
                    await self.revise(
                        f"Scene {n} failed the render's layout check:\n{findings}\n"
                        "Shorten that scene's on-screen text (visual_content) so it fits the frame. Do not change any narration.")
                except StageError as e:
                    raise StageError(f"The render check failed on scene {n}, and the script fix did not help ({e}):\n{findings}") from e
                await self.voiceover()
                await self.build_scenes()
            code, out = await self.sh(TOOLS, "ffprobe", "-v", "error", "-show_entries", "format=duration",
                                      "-of", "csv=p=0", f"runs/{self.slug}/final.mp4")
            seconds = float(out.strip().splitlines()[-1]) if code == 0 else 0.0
            self.job.summary["video_seconds"] = round(seconds, 1)
            st["note"] = f"final.mp4, {int(seconds // 60)} min {round(seconds % 60)} s"

    def report(self):
        s, job = self.job.summary, self.job
        brief = self.path("01_brief.md").read_text()
        topic = re.search(r"^# Video Brief: (.+)$", brief, re.M)
        assumptions = re.search(r"\*\*Assumptions:\*\*\s*(.+)", brief)
        secs = s.get("video_seconds", 0)
        fc = s.get("fact_check", {})
        lines = [
            f"# Report: {topic.group(1).strip() if topic else self.slug}", "",
            f"- **Prompt:** \"{job.prompt}\"",
            f"- **Video:** `runs/{self.slug}/final.mp4`, {int(secs // 60)} min {round(secs % 60)} s "
            f"({(secs - TARGET_SEC) / TARGET_SEC:+.0%} vs the 7-minute target)",
            f"- **Fact-check:** " + ", ".join(f"{k} {v}" for k, v in fc.items()),
            f"- **Final script check:** {s.get('script_check_rounds')} round(s)"
            + (f"; failing sentences deleted in {s['scenes_with_deleted_sentences']} scenes"
               if s.get("scenes_with_deleted_sentences") else "; passed"),
            f"- **Script revisions:** {self.revisions}",
            f"- **Assumptions the intake agent made** (never confirmed by a person): "
            f"{assumptions.group(1).strip() if assumptions else 'None'}",
            f"- **API cost:** ${job.cost_usd:.2f}", "",
            "## Time per stage", "", "| Stage | Time | Cost | Note |", "|---|---|---|---|"]
        total = 0
        for key, name in STAGES:
            st = job.stages[key]
            total += st.get("seconds", 0)
            lines.append(f"| {name} | {st.get('seconds', 0) // 60} min {st.get('seconds', 0) % 60} s | "
                         f"${st.get('cost', 0):.2f} | {st.get('note', '').replace('|', '/')} |")
        lines += [f"| **Total** | **{total // 60} min {total % 60} s** | **${job.cost_usd:.2f}** | |", "",
                  "## Needs a human look", ""]
        look = [f"- {f}" for f in s.get("review_flags", [])]
        look += [f"- {q} has no verified facts, so its scenes are written in general terms" for q in s.get("thin_questions", [])]
        lines += look or ["- Nothing flagged."]
        if s.get("scriptwriter_reply"):
            lines += ["", "## Script writer's notes (thin scenes and gaps)", "", s["scriptwriter_reply"].strip()]
        self.path("report.md").write_text("\n".join(lines) + "\n")

    async def run(self):
        job = self.job
        job.status = "running"
        job.log("started")
        try:
            await self.check_tools()
            await self.intake()
            await self.research()
            await self.fact_check()
            await self.script()
            await self.length_fit()
            await self.script_check()
            await self.scenes()
            await self.render()
            self.report()
            job.status = "done"
            job.log(f"done: runs/{self.slug}/final.mp4 (${job.cost_usd:.2f})")
        except asyncio.CancelledError:
            job.status, job.error = "cancelled", "Stopped by the user."
            raise
        except StageError as e:
            job.status, job.error = "failed", str(e)
            job.log(f"stopped: {e}", self.current)
        except Exception as e:
            job.status, job.error = "failed", f"Unexpected error: {e!r}"
            job.log(traceback.format_exc()[-1500:], self.current)
        finally:
            job.save()
