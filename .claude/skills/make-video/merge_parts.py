"""Merge the per-question files from parallel researchers or fact-checkers into one file.

Usage (from the repo root):
    python3 .claude/skills/make-video/merge_parts.py runs/<slug> research   # research/q*.md -> 02_research.md
    python3 .claude/skills/make-video/merge_parts.py runs/<slug> checked    # checked/q*.md  -> 03_checked.md

Each part file uses the normal template with one question. Questions are kept in order,
Gaps are combined, sources are de-duplicated by URL, and verdict counts are added up.
Exits with code 1 if a key question from 01_brief.md has no part file.
"""
import re
import sys
from datetime import date
from pathlib import Path

FACT = re.compile(r"^- \*\*Q\d+-F\d+\*\*", re.M)
URL = re.compile(r"\((https?://[^)\s]+)\)|(https?://\S+)")


def sections(text):
    """Return (header_text, [(heading, body), ...]) split on '## ' lines."""
    parts = re.split(r"^## ", text, flags=re.M)
    out = []
    for p in parts[1:]:
        heading, _, body = p.partition("\n")
        out.append((heading.strip(), body.strip("\n")))
    return parts[0], out


def first_url(line):
    m = URL.search(line)
    return (m.group(1) or m.group(2)).rstrip("|").strip() if m else line.strip()


def table_rows(body):
    rows = [l for l in body.splitlines() if l.startswith("|")]
    return rows[2:] if len(rows) >= 2 and set(rows[1].replace("|", "").strip()) <= set("-: ") else rows


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("research", "checked"):
        sys.exit(__doc__)
    run, kind = Path(sys.argv[1]), sys.argv[2]
    slug = run.name
    brief = (run / "01_brief.md").read_text()
    kq = re.search(r"## Key questions for research\n(.*?)\n## ", brief, re.S)
    expected = len(re.findall(r"^\d+\. ", kq.group(1), re.M)) if kq else 0
    files = sorted((run / kind).glob("q*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
    found = {int(re.sub(r"\D", "", p.stem)) for p in files}
    missing = [n for n in range(1, expected + 1) if n not in found]
    if missing:
        print(f"MISSING part files for questions: {missing}")

    topic = re.search(r"^# Video Brief: (.+)$", brief, re.M)
    topic = topic.group(1).strip() if topic else slug
    q_sections, gaps, src_lines, rejected, src_rows, notes = [], [], [], [], [], []
    counts = {"Verified": 0, "Overstated": 0, "Unsupported": 0, "Unreachable": 0}
    for f in files:
        header, secs = sections(f.read_text())
        for line in header.splitlines():
            if line.startswith("Note for the fact-checker") and line not in notes:
                notes.append(line)
            for k in counts:
                m = re.search(rf"{k}: (\d+)", line)
                if m:
                    counts[k] += int(m.group(1))
        for heading, body in secs:
            h = heading.lower()
            if re.match(r"q\d+\.", h):
                q_sections.append(f"## {heading}\n\n{body}")
            elif h.startswith("gaps"):
                gaps += [l for l in body.splitlines() if l.strip()]
            elif h.startswith("sources cited") or (kind == "research" and h.startswith("sources")):
                src_lines += [re.sub(r"^\d+\.\s*", "", l).strip() for l in body.splitlines() if re.match(r"^\d+\.", l.strip())]
            elif h.startswith("rejected"):
                rejected += table_rows(body)
            elif h.startswith("sources"):
                src_rows += table_rows(body)

    body = "\n\n".join(q_sections)
    n_facts = len(FACT.findall(body))
    today = date.today().isoformat()
    if kind == "research":
        seen, sources = set(), []
        for s in src_lines:
            u = first_url(s)
            if u not in seen:
                seen.add(u); sources.append(s)
        out = [f"# Research: {topic}", "",
               f"Brief: `runs/{slug}/01_brief.md` · Researched: {today} · Facts: {n_facts}", ""]
        out += notes + ([""] if notes else [])
        out += [f"Merged from {len(files)} parallel research files in `research/` (one researcher per question).", "", body, "",
                "## Gaps", ""] + (gaps or ["- None reported."]) + ["", "## Sources cited", ""]
        out += [f"{i}. {s}" for i, s in enumerate(sources, 1)]
        target = run / "02_research.md"
    else:
        seen, rows = set(), []
        for r in src_rows:
            u = first_url(r)
            if u not in seen:
                seen.add(u); rows.append(r)
        verified_lines = len(re.findall(r"Check: VERIFIED", body))
        out = [f"# Checked facts: {topic}", "",
               f"Research: `runs/{slug}/02_research.md` · Checked: {today} · merged from {len(files)} files in `checked/`",
               " · ".join(f"{k}: {v}" for k, v in counts.items()), "",
               "Only the facts below may be used in the script.", "", body, "",
               "## Rejected facts (do not use)", "",
               "| ID | Verdict | Reason | Narrower wording the source does support |", "|---|---|---|---|"] + rejected
        out += ["", "## Sources", "", "| URL | Status |", "|---|---|"] + rows
        target = run / "03_checked.md"
        if verified_lines != counts["Verified"]:
            print(f"note: headers say {counts['Verified']} verified, but {verified_lines} facts carry 'Check: VERIFIED'")
    target.write_text("\n".join(out).rstrip() + "\n")
    print(f"wrote {target} from {len(files)} files: {n_facts} facts"
          + ("" if kind == "research" else f"; " + ", ".join(f"{k} {v}" for k, v in counts.items())))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
