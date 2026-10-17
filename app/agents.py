"""Run one pipeline agent (a file in .claude/agents/) through the Claude Agent SDK.

The agent files stay the single source of truth: the frontmatter gives the tools, the body
is the system prompt. Each run uses an Anthropic API key (ANTHROPIC_API_KEY), so nobody
needs a Claude Pro or Max account, and Claude Code itself never has to be opened.

Guardrails are enforced in code, not in the prompt (see guard()): agents may only write
inside runs/, may not read secrets or system files, and the two agents with Bash may not
run network or environment-dumping commands. This matters because the researcher and the
fact-checker read arbitrary web pages.
"""
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / ".claude" / "agents"
RUNS = REPO / "runs"
DEFAULT_MODEL = "claude-opus-5-5"

RUN_CONTEXT = """

---

Run context: you are one stage of an automated pipeline (app/pipeline.py), not a chat.
Nobody can answer questions while you work, so make the sensible choice, note it where your
instructions say to, and finish. The working directory is the repo root ({repo}). All paths
in your instructions are relative to it. Today's date is {today}."""

READABLE_OUTSIDE_REPO = [Path(tempfile.gettempdir()), Path.home() / ".claude"]
BLOCKED_COMMAND = re.compile(
    r"(^|[\s;|&(`])(env|printenv|export|set|curl|wget|nc|ncat|ssh|scp|pip|npm|apt|apt-get)(\s|$)"
    r"|/proc/|ANTHROPIC|API_KEY|\.env\b|base64|environ|getenv|declare|compgen"
)


class AgentError(RuntimeError):
    def __init__(self, message, cost=0.0):
        super().__init__(message)
        self.cost = cost


@dataclass
class Agent:
    name: str
    tools: list[str]
    prompt: str


@dataclass
class AgentRun:
    text: str
    cost: float
    session_id: str
    turns: int


def load_agent(name):
    text = (AGENTS / f"{name}.md").read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise AgentError(f"{name}.md has no frontmatter")
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    tools = [t.strip() for t in meta.get("tools", "").split(",") if t.strip()]
    return Agent(name=name, tools=tools, prompt=m.group(2).strip())


def model_for(name):
    """VIDEO_MODEL sets every agent's model; VIDEO_MODEL_RESEARCHER (etc.) overrides one agent."""
    return os.environ.get(f"VIDEO_MODEL_{name.upper().replace('-', '_')}") or os.environ.get("VIDEO_MODEL") or DEFAULT_MODEL


def _inside(path, roots):
    return any(path == r or r in path.parents for r in roots)


def check_tool_call(tool, tool_input):
    """Return a reason to block this tool call, or None to let it through."""
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        path = (REPO / raw).resolve()
        if not _inside(path, [RUNS.resolve()]):
            return f"Write only inside runs/ (got {raw})"
    elif tool == "Read":
        raw = tool_input.get("file_path") or ""
        path = (REPO / raw).resolve()
        if path.name == ".env" or path.name.startswith(".env."):
            return "secrets files are off limits"
        if not _inside(path, [REPO.resolve()] + [p.resolve() for p in READABLE_OUTSIDE_REPO]):
            return f"Read only inside the project folder (got {raw})"
    elif tool == "Bash":
        if BLOCKED_COMMAND.search(tool_input.get("command", "")):
            return "that command is not allowed in this pipeline"
    return None


async def guard(hook_input, tool_use_id, context):
    reason = check_tool_call(hook_input.get("tool_name", ""), hook_input.get("tool_input") or {})
    if reason is None:
        return {}
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def _short(path):
    p = (REPO / path).resolve() if path else REPO
    return str(p.relative_to(REPO)) if REPO in p.parents else path


def describe(block):
    """One short line for the progress feed."""
    i = block.input or {}
    if block.name == "WebSearch":
        return f"searching: {i.get('query', '')}"
    if block.name == "WebFetch":
        u = urlparse(i.get("url", ""))
        return f"opening {u.netloc}{u.path[:60]}"
    if block.name in ("Read", "Write", "Edit"):
        return f"{block.name.lower()} {_short(i.get('file_path', ''))}"
    if block.name == "Bash":
        return f"running: {i.get('command', '')[:90]}"
    return block.name


async def run_agent(name, prompt, *, on_event=None, resume=None, budget_usd=None):
    agent = load_agent(name)
    options = ClaudeAgentOptions(
        system_prompt=agent.prompt + RUN_CONTEXT.format(repo=REPO, today=date.today().isoformat()),
        tools=agent.tools,
        allowed_tools=agent.tools,
        permission_mode="dontAsk",
        hooks={"PreToolUse": [HookMatcher(hooks=[guard])]},
        setting_sources=["project"],  # loads CLAUDE.md, as a subagent in Claude Code would see it
        skills=[],
        cwd=str(REPO),
        model=model_for(name),
        resume=resume,
        max_budget_usd=budget_usd,
        env={"CLAUDE_AGENT_SDK_CLIENT_APP": "traversaal-video-agent/1.0"},
    )
    texts, result = [], None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    texts.append(block.text)
                elif isinstance(block, ToolUseBlock) and on_event:
                    on_event(describe(block))
        elif isinstance(message, ResultMessage):
            result = message
    if result is None:
        raise AgentError(f"{name}: the agent stopped without a result")
    cost = result.total_cost_usd or 0.0
    if result.is_error:
        detail = "; ".join(result.errors or []) or result.result or result.subtype
        if result.api_error_status:
            detail = f"API error {result.api_error_status}: {detail}"
        raise AgentError(f"{name}: {detail}", cost)
    return AgentRun(text=result.result or "\n".join(texts), cost=cost, session_id=result.session_id, turns=result.num_turns)
