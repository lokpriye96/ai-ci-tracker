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


def write_run_log(args, articles, raw, verified, review, rejected, dupes, llm_errors, error_samples) -> None:
    """Append a human-readable record of this run (public proof the pipeline runs)."""
    import os
    from datetime import datetime, timezone
    provider = os.getenv("CI_LLM_PROVIDER", "gemini")
    from ci_tracker.llm import _GEMINI_MODEL_CACHE
    model = _GEMINI_MODEL_CACHE.get("name") or os.getenv("CI_LLM_MODEL", "") or "default"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"\n## Run {stamp}" + (" (dry run)" if args.dry_run else ""),
             f"- Trigger: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'local'}"
             + (f" · run {os.getenv('GITHUB_RUN_ID')}" if os.getenv('GITHUB_RUN_ID') else ""),
             f"- LLM: {provider} / {model} · look-back {args.days} days",
             f"- Articles sent to LLM: {len(articles)} · LLM errors: {llm_errors}",
             f"- Candidate events: {len(raw)} → verified {len(verified)}, needs review {len(review)}, "
             f"rejected {len(rejected)}, duplicates skipped {dupes}"]
    from ci_tracker.collect import COLLECTION_STATS
    for st in COLLECTION_STATS:
        lines.append(f"  - Collected: {st}")
    for err in error_samples:
        lines.append(f"  - LLM error sample: {err}")
    for ev in verified + review:
        lines.append(f"  - [{ev['validation_status']}] {ev['event_id']} {ev['company']}: "
                     f"{ev.get('headline', '')} ({ev.get('source_url', '')})")
    for ev in rejected:
        lines.append(f"  - [Rejected] {ev.get('company', '?')}: {ev.get('headline', '')} - {ev.get('checks', '')}")
    log = ROOT / "outputs" / "run_log.md"
    if not log.exists():
        log.write_text("# Pipeline run log\n\nEvery automated or manual run is recorded here.\n",
                       encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--max-per-company", type=int, default=6,
                    help="cap on articles sent to the LLM per competitor")
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
        articles = collect_all(args.days, args.per_query, max_per_company=args.max_per_company,
                               skip_urls={r.get("source_url", "") for r in db})
    print(f"    {len(articles)} articles")

    print("2/3 Extracting events with LLM ...")
    import os
    import time
    delay = float(os.getenv("CI_LLM_DELAY", "0"))  # pacing for free-tier rate limits
    raw, llm_errors, error_samples = [], 0, []
    for i, a in enumerate(articles, 1):
        try:
            raw.extend(extract_events(a))
        except Exception as exc:  # keep going if one call fails
            llm_errors += 1
            if len(error_samples) < 3:
                error_samples.append(str(exc)[:300])
            print(f"    ! article {i} skipped: {exc}", flush=True)
        if delay:
            time.sleep(delay)
    print(f"    {len(raw)} candidate events")

    print("3/3 Validating ...")
    verified, review, rejected, dupes = [], [], [], 0
    for ev in raw:
        if not isinstance(ev, dict):
            continue
        try:
            ev = validate_event(ev)
        except Exception as exc:  # never let one malformed event stop the run
            error_samples.append(f"validation error: {exc}"[:300])
            continue
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

    if not args.demo:
        write_run_log(args, articles, raw, verified, review, rejected, dupes, llm_errors, error_samples)
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
