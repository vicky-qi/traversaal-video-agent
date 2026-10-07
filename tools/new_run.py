"""Create a run folder for one video: runs/<slug>/ with the prompt and an empty run log.

Usage: python tools/new_run.py <slug> "<user prompt>"
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

if len(sys.argv) < 3:
    sys.exit(__doc__)

slug, prompt = sys.argv[1], sys.argv[2]
run = REPO / "runs" / slug
if run.exists():
    sys.exit(f"{run} already exists; pick another slug or delete it")

for sub in ("research", "scenes", "renders"):
    (run / sub).mkdir(parents=True)
(run / "prompt.txt").write_text(prompt + "\n")
(run / "run_log.json").write_text(json.dumps({
    "slug": slug,
    "prompt": prompt,
    "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "stages": [],
}, indent=2) + "\n")
print(run.relative_to(REPO))
