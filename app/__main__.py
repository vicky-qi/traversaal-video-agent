"""Make one video from the terminal, without the web page or Claude Code:

    render/env.sh python -m app "How do electric vehicle batteries work?"

Needs ANTHROPIC_API_KEY (in the environment or in .env). Prints progress as it goes and
exits with code 0 when runs/<slug>/final.mp4 is ready, 1 if a stage could not be repaired.
"""
import argparse
import asyncio
import sys
import uuid
from datetime import datetime

from .pipeline import Job, Pipeline, clock


def main():
    ap = argparse.ArgumentParser(description="One prompt in, a narrated ~7-minute explainer MP4 out.")
    ap.add_argument("prompt", help='the video prompt, e.g. "How does compound interest work?"')
    args = ap.parse_args()

    job = Job(id=uuid.uuid4().hex[:12], prompt=args.prompt, created=datetime.now().isoformat(timespec="seconds"))
    record = job.log

    def log(text, stage=None):
        record(text, stage)
        print(f"{clock()} [{stage or '-'}] {text}", flush=True)

    job.log = log
    asyncio.run(Pipeline(job).run())
    if job.status != "done":
        print(f"\nFAILED: {job.error}", file=sys.stderr)
        sys.exit(1)
    print(f"\nVideo: runs/{job.slug}/final.mp4 · report: runs/{job.slug}/report.md · cost ${job.cost_usd:.2f}")


if __name__ == "__main__":
    main()
