"""Run the CI tracker end to end.

  python run_pipeline.py                     # last 30 days of news, all 8 competitors
  python run_pipeline.py --days 7            # weekly refresh
  python run_pipeline.py --urls my_urls.txt  # analyst-supplied press-release URLs
  python run_pipeline.py --dry-run           # extract + validate, write nothing
  python run_pipeline.py --demo              # offline demo: sample article + mock LLM

Verified events are appended to data/ci_events.csv.
Events that fail a soft check go to data/review_queue.csv for a human decision.
Rejected events are logged in data/rejected_log.csv with the reason.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ci_tracker.collect import Article, collect_all, fetch_text  # noqa: E402
from ci_tracker.extract import extract_events  # noqa: E402
from ci_tracker.validate import canonical_company, is_duplicate, validate_event  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent
DB = ROOT / "data" / "ci_events.csv"
REVIEW = ROOT / "data" / "review_queue.csv"
REJECTED = ROOT / "data" / "rejected_log.csv"
PREFIX = {"Accenture": "ACN", "TCS": "TCS", "Infosys": "INF", "Wipro": "WIP",
          "HCLTech": "HCL", "Cognizant": "CTS", "Capgemini": "CAP", "Tech Mahindra": "TEM"}


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerows(rows)


def articles_from_urls(path: Path) -> list[Article]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        text = fetch_text(url)
        title = text.split("\n", 1)[0][:200] if text else url
        out.append(Article(company=canonical_company(title + " " + text[:2000]) or "",
                           title=title, url=url, published=date.today().isoformat(),
                           source=url.split("/")[2], text=text))
    return out


def next_id(company: str, existing: list[dict]) -> str:
    p = PREFIX.get(company, "OTH")
    nums = [int(r["event_id"].split("-")[1]) for r in existing
            if r.get("event_id", "").startswith(p + "-")]
    return f"{p}-{(max(nums) + 1 if nums else 1):03d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--per-query", type=int, default=8)
    ap.add_argument("--urls", type=Path, help="text file with one URL per line")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--demo", action="store_true", help="offline demo, implies --dry-run")
    args = ap.parse_args()
    if args.demo:
        import os
        os.environ["CI_LLM_PROVIDER"] = "mock"
        args.dry_run = True

    db = read_csv(DB)
    fields = list(db[0].keys()) if db else []
    print("1/3 Collecting articles ...")
    if args.demo:
        text = (ROOT / "tests/fixtures/sample_article.txt").read_text(encoding="utf-8")
        articles = [Article("Infosys", "Infosys partners with ExampleAI Labs (synthetic)",
                            "https://www.infosys.com/demo", "2026-11-02", "Infosys", text)]
    elif args.urls:
        articles = articles_from_urls(args.urls)
    else:
        articles = collect_all(args.days, args.per_query)
    print(f"    {len(articles)} articles")

    print("2/3 Extracting events with LLM ...")
    raw = []
    for i, a in enumerate(articles, 1):
        try:
            raw.extend(extract_events(a))
        except Exception as exc:  # keep going if one call fails
            print(f"    ! article {i} skipped: {exc}")
    print(f"    {len(raw)} candidate events")

    print("3/3 Validating ...")
    verified, review, rejected, dupes = [], [], [], 0
    for ev in raw:
        ev = validate_event(ev)
        if ev["validation_status"] == "Rejected":
            rejected.append(ev)
            continue
        if is_duplicate(ev, db + verified + review):
            dupes += 1
            continue
        ev["event_id"] = next_id(ev["company"], db + verified + review)
        (verified if ev["validation_status"] == "Verified" else review).append(ev)

    print(f"    verified {len(verified)} | review {len(review)} | "
          f"rejected {len(rejected)} | duplicates skipped {dupes}")
    for ev in verified + review:
        print(f"    [{ev['validation_status']}] {ev['company']}: {ev['headline']}  ({ev['checks']})")

    if args.dry_run:
        print("Dry run - nothing written.")
        return
    if verified:
        append_csv(DB, verified, fields)
    review_fields = fields + ["evidence_quote", "checks"]
    if review:
        append_csv(REVIEW, review, review_fields)
    if rejected:
        append_csv(REJECTED, rejected, ["company", "event_date", "event_type", "headline",
                                        "source_url", "checks"])
    print("Done. Rebuild outputs with:  python build_outputs.py")


if __name__ == "__main__":
    main()
