"""Append one stage result to runs/<slug>/run_log.json (used for Step 4 metrics).

Usage: python tools/log_stage.py <run_dir> <stage> <ok|failed> [note]
Each call records the time since the previous entry (or since the run started).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if len(sys.argv) < 4:
    sys.exit(__doc__)

run, stage, status = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
note = sys.argv[4] if len(sys.argv) > 4 else ""
log_path = run / "run_log.json"
log = json.loads(log_path.read_text())

now = datetime.now(timezone.utc)
prev = log["stages"][-1]["finished_at"] if log["stages"] else log["started_at"]
elapsed = (now - datetime.fromisoformat(prev)).total_seconds()

log["stages"].append({
    "stage": stage,
    "status": status,
    "note": note,
    "finished_at": now.isoformat(timespec="seconds"),
    "elapsed_s": round(elapsed, 1),
})
log_path.write_text(json.dumps(log, indent=2) + "\n")
print(f"{stage}: {status} ({elapsed:.0f}s)")
