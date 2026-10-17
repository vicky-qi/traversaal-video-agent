"""Traversaal Video Agent as a standalone app: the same agents and workflow, no Claude Code needed."""
import os
from pathlib import Path

# Read ANTHROPIC_API_KEY and the other settings from .env (never committed) when present.
_env = Path(__file__).resolve().parent.parent / ".env"
if _env.exists():
    for _line in _env.read_text().splitlines():
        _key, _sep, _value = _line.strip().partition("=")
        if _sep and _key and not _key.startswith("#"):
            os.environ.setdefault(_key.strip().removeprefix("export "), _value.strip().strip("\"'"))
