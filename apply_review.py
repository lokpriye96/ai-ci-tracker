"""Apply the analyst's decisions in data/review_queue.csv.

How the analyst reviews (no code needed):
  1. Open data/review_queue.csv on GitHub and click the pencil (Edit) icon.
  2. Open each row's source_url and check company, date, counterparty and any value.
  3. Type a decision in the first column of the row:
        Approve  -> the event is published to data/ci_events.csv
        Reject   -> the event is dropped and logged in data/retired_ids.csv
     Leave it blank to decide later. Optionally write a reason in analyst_note
     (wrap it in double quotes if it contains a comma).
  4. Click "Commit changes". GitHub Actions ("Apply analyst review") then runs this
     script, re-runs the tests, rebuilds the Excel workbook and dashboard, and commits.

Safety rules: an approved row is only published if it fits the taxonomy and does not
reuse an event ID or a source article already in the database. Otherwise it stays in
the queue with the reason written in analyst_note, so nothing breaks silently.

Run locally:  python apply_review.py
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from ci_tracker.config import COMPANIES, EVENT_TYPES, STRATEGIC_THEMES  # noqa: E402

DB = ROOT / "data" / "ci_events.csv"
REVIEW = ROOT / "data" / "review_queue.csv"
RETIRED = ROOT / "data" / "retired_ids.csv"
RUN_LOG = ROOT / "outputs" / "run_log.md"
DECISION_FIELDS = ["decision", "analyst_note"]


def read(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def problems(row: dict, db: list[dict]) -> list[str]:
    out = []
    if row.get("company") not in COMPANIES:
        out.append(f"company '{row.get('company')}' is not one of the 8 tracked firms")
    if row.get("event_type") not in EVENT_TYPES:
        out.append(f"event_type '{row.get('event_type')}' is not in the taxonomy")
    if row.get("strategic_theme") not in STRATEGIC_THEMES:
        out.append(f"strategic_theme '{row.get('strategic_theme')}' is not in the taxonomy")
    if not row.get("source_url", "").startswith("https://"):
        out.append("source_url must start with https://")
    for d in db:
        if d["event_id"] == row.get("event_id"):
            out.append(f"event ID already used by {d['event_id']}")
        if d["source_url"] == row.get("source_url"):
            out.append(f"same article as {d['event_id']}: cite the original announcement instead")
    return out


def main() -> int:
    db_fields, db = read(DB)
    q_fields, queue = read(REVIEW)
    if not queue:
        print("Review queue is empty.")
        return 0
    for f in DECISION_FIELDS[::-1]:
        if f not in q_fields:
            q_fields.insert(0, f)
    ret_fields, _ = read(RETIRED)

    approved, rejected, held, keep = [], [], [], []
    for row in queue:
        decision = (row.get("decision") or "").strip().lower()
        if decision in ("approve", "approved", "yes"):
            issues = problems(row, db + approved)
            if issues:
                row["decision"] = ""
                row["analyst_note"] = "Not applied: " + "; ".join(issues)
                held.append(row)
                keep.append(row)
                continue
            row["validation_status"] = "Verified"
            approved.append(row)
        elif decision in ("reject", "rejected", "no"):
            rejected.append(row)
        else:
            keep.append(row)

    if approved:
        with DB.open("a", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=db_fields, extrasaction="ignore").writerows(approved)
    if rejected:
        with RETIRED.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            for r in rejected:
                w.writerow([r["event_id"], "Rejected at review",
                            r.get("analyst_note") or "Rejected by analyst"])
    with REVIEW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=q_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(keep)

    summary = (f"approved {len(approved)}, rejected {len(rejected)}, "
               f"could not apply {len(held)}, still waiting {len(keep) - len(held)}")
    print("Analyst review:", summary)
    if approved or rejected or held:
        lines = [f"\n## Analyst review {date.today().isoformat()}", f"- {summary}"]
        lines += [f"  - [Approved] {r['event_id']} {r['company']}: {r['headline']}" for r in approved]
        lines += [f"  - [Rejected] {r['event_id']} {r['company']}: {r['headline']}"
                  f" - {r.get('analyst_note') or 'Rejected by analyst'}" for r in rejected]
        lines += [f"  - [Not applied] {r['event_id']}: {r['analyst_note']}" for r in held]
        with RUN_LOG.open("a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
