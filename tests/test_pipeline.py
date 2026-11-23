"""Offline tests: run with  pytest -q  (no API key or internet needed)."""
import csv
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["CI_LLM_PROVIDER"] = "mock"
os.environ["CI_MOCK_RESPONSE"] = str(ROOT / "tests/fixtures/mock_llm_response.json")

from ci_tracker.collect import Article  # noqa: E402
from ci_tracker.config import EVENT_TYPES, STRATEGIC_THEMES  # noqa: E402
from ci_tracker.extract import build_prompt, extract_events  # noqa: E402
from ci_tracker.validate import (canonical_company, is_duplicate, quote_in_text,  # noqa: E402
                                 source_tier, validate_event)

TODAY = date(2026, 11, 11)
TEXT = (ROOT / "tests/fixtures/sample_article.txt").read_text(encoding="utf-8")
ARTICLE = Article("Infosys", "Infosys partners with ExampleAI Labs", "https://www.infosys.com/x",
                  "2026-11-02", "Infosys", TEXT)


def test_prompt_contains_article_and_rules():
    p = build_prompt(ARTICLE)
    assert "ExampleAI Labs" in p and "evidence_quote" in p and "Acquisition" in p


def test_end_to_end_mock_extraction_and_validation():
    events = [validate_event(e, TODAY) for e in extract_events(ARTICLE)]
    status = [e["validation_status"] for e in events]
    assert status == ["Verified", "Needs review", "Rejected"]
    assert "hallucination" in events[1]["checks"]
    assert "company not in tracked list" in events[2]["checks"]
    assert events[0]["source_tier"] == "Primary"


def test_company_aliases():
    assert canonical_company("Tata Consultancy Services Ltd") == "TCS"
    assert canonical_company("HCLSoftware") == "HCLTech"
    assert canonical_company("Deloitte") is None


def test_source_tiers():
    assert source_tier("https://www.prnewswire.com/news/abc") == "Primary"
    assert source_tier("https://www.business-standard.com/x") == "Secondary"
    assert source_tier("https://www.reddit.com/r/x") == "Blocked"


def test_quote_check_tolerates_punctuation():
    assert quote_in_text("Infosys today announced a strategic partnership, with ExampleAI Labs",
                         TEXT)
    assert not quote_in_text("Infosys will acquire a bank", TEXT)


def test_duplicate_detection_against_seed_db():
    with (ROOT / "data/ci_events.csv").open(encoding="utf-8") as f:
        db = list(csv.DictReader(f))
    dup = {"company": "Infosys", "event_date": "2026-02-18", "event_type": "Partnership",
           "counterparty": "Anthropic", "headline": "Infosys teams up with Anthropic"}
    new = {"company": "Infosys", "event_date": "2026-11-02", "event_type": "Partnership",
           "counterparty": "ExampleAI Labs", "headline": "Infosys partners with ExampleAI"}
    assert is_duplicate(dup, db)
    assert not is_duplicate(new, db)


def test_seed_db_respects_taxonomy():
    with (ROOT / "data/ci_events.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 50
    for r in rows:
        assert r["event_type"] in EVENT_TYPES, r["event_id"]
        assert r["strategic_theme"] in STRATEGIC_THEMES, r["event_id"]
        assert r["source_url"].startswith("https://"), r["event_id"]
    assert len({r["event_id"] for r in rows}) == len(rows)


def test_gdelt_parsing_and_event_filter():
    from ci_tracker.collect import looks_like_event, parse_gdelt
    items = [
        {"url": "https://example.com/a", "title": "Infosys partners with ExampleAI on agentic AI",
         "seendate": "20261102T101500Z", "domain": "example.com"},
        {"url": "https://example.com/b", "title": "Infosys partners with ExampleAI on agentic AI",
         "seendate": "20261102T101500Z", "domain": "example.com"},  # duplicate headline
        {"url": "https://example.com/c", "title": "Infosys share price today: stock closes flat",
         "seendate": "20261103T080000Z", "domain": "example.com"},
    ]
    arts = parse_gdelt("Infosys", items)
    assert len(arts) == 2 and arts[0].published == "2026-11-02"
    assert [looks_like_event(a) for a in arts] == [True, False]


def test_llm_providers():
    from ci_tracker.llm import DEFAULT_MODELS
    assert set(DEFAULT_MODELS) == {"gemini", "anthropic", "openai"}


def test_bing_parsing_extracts_real_url():
    from ci_tracker.collect import parse_bing
    xml = b"""<rss><channel><item><title>TCS partners with ExampleAI on agentic AI</title>
    <link>http://www.bing.com/news/apiclick.aspx?ref=FexRss&amp;url=https%3a%2f%2fwww.example.com%2fnews%2ftcs&amp;c=1</link>
    <pubDate>Tue, 10 Nov 2026 08:00:00 GMT</pubDate></item></channel></rss>"""
    arts = parse_bing("TCS", xml)
    assert arts[0].url == "https://www.example.com/news/tcs" and arts[0].published == "2026-11-10"


def test_validation_survives_null_fields():
    ev = {"company": "TCS", "event_date": None, "event_type": "Partnership", "headline": None,
          "counterparty": None, "deal_value_usd_m": "n/a", "source_url": "https://www.tcs.com/x",
          "evidence_quote": None, "confidence": None, "_article_text": "TCS text"}
    out = validate_event(ev, TODAY)
    assert out["validation_status"] == "Rejected" and "event_date" in out["checks"]


def test_dedup_catches_same_event_without_counterparty():
    old = [{"company": "Capgemini", "event_date": "2026-11-09", "event_type": "Deal / GCC",
            "counterparty": "European Commission AI Office", "headline": "Capgemini leads EU AI consortium",
            "summary": "Capgemini will lead a consortium to support the European Commission AI Office on advanced AI risks."}]
    new = {"company": "Capgemini", "event_date": "2026-11-05", "event_type": "Deal / GCC", "counterparty": "",
           "headline": "", "summary": "Capgemini was selected by the European Commission AI Office to lead a consortium on advanced AI risks."}
    assert is_duplicate(new, old)


def test_blank_headline_gets_fallback():
    import json, os
    from pathlib import Path
    fx = Path("/tmp/blank_headline.json")
    fx.write_text(json.dumps({"events": [{"company": "Infosys", "headline": "",
                                          "summary": "Infosys partners with ExampleAI. More text."}]}))
    os.environ["CI_MOCK_RESPONSE"] = str(fx)
    try:
        ev = extract_events(ARTICLE)[0]
    finally:
        os.environ["CI_MOCK_RESPONSE"] = str(ROOT / "tests/fixtures/mock_llm_response.json")
    assert ev["headline"] == "Infosys partners with ExampleAI"


def test_old_deal_mentioned_again_is_duplicate():
    # e.g. a Nov 2026 article that refers back to the Jul 2025 WNS acquisition
    old = [{"company": "Capgemini", "event_date": "2025-07-07", "event_type": "Acquisition",
            "counterparty": "WNS", "headline": "Capgemini to acquire WNS for $3.3B"}]
    again = {"company": "Capgemini", "event_date": "2026-11-12", "event_type": "Acquisition",
             "counterparty": "WNS", "headline": "Capgemini completes WNS integration"}
    assert is_duplicate(again, old)


def test_one_article_one_event_per_counterparty():
    url = "https://example.com/techm-google"
    old = [{"company": "Tech Mahindra", "event_date": "2026-10-05", "event_type": "Partnership",
            "counterparty": "Google Cloud", "headline": "Tech Mahindra expands Google Cloud tie-up",
            "source_url": url}]
    split = {"company": "Tech Mahindra", "event_date": "2026-10-05", "event_type": "Talent / CoE",
             "counterparty": "Google Cloud", "headline": "Tech Mahindra trains staff on Gemini",
             "source_url": url}
    assert is_duplicate(split, old)


def test_blank_company_falls_back_to_article_company():
    ev = {"company": "", "_article_company": "Accenture", "event_date": "2026-11-10",
          "event_type": "Deal / GCC", "headline": "Qantas outsources roles", "source_url": "https://example.com/q",
          "strategic_theme": "Intelligent operations", "_article_text": "Qantas and Accenture"}
    assert validate_event(ev, TODAY)["company"] == "Accenture"


def test_new_ids_never_reuse_retired_ids():
    sys.path.insert(0, str(ROOT))
    from run_pipeline import next_id, read_csv, DB, RETIRED
    retired = {r["event_id"].split(" ")[0] for r in read_csv(RETIRED)}
    for company in ("Capgemini", "HCLTech", "Wipro", "Accenture", "Tech Mahindra"):
        assert next_id(company, read_csv(DB)) not in retired


def test_database_has_no_duplicate_ids_or_shared_sources():
    with (ROOT / "data/ci_events.csv").open(encoding="utf-8") as f:
        db = list(csv.DictReader(f))
    ids = [r["event_id"] for r in db]
    assert len(ids) == len(set(ids))
    urls = [r["source_url"] for r in db]
    assert len(urls) == len(set(urls)), "two events cite the same article"


def test_apply_review_publishes_approved_and_blocks_bad_rows(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT))
    import shutil
    import apply_review as ar
    for name in ("ci_events.csv", "retired_ids.csv"):
        shutil.copy(ROOT / "data" / name, tmp_path / name)
    db_fields, db = ar.read(tmp_path / "ci_events.csv")
    base = {k: "" for k in db_fields}
    good = dict(base, decision="Approve", event_id="TEST-001", company="Infosys",
                event_date="2026-11-20", event_type="Partnership", strategic_theme="Frontier-lab alliance",
                headline="Good event", source_url="https://example.com/new-article",
                validation_status="Awaiting approval")
    same_article = dict(good, event_id="TEST-002", headline="Second event, same article")
    reused = dict(good, event_id="TEST-003", source_url=db[0]["source_url"])
    bad = dict(good, decision="Reject", event_id="TEST-004", analyst_note="Mislabelled company")
    waiting = dict(good, decision="", event_id="TEST-005", source_url="https://example.com/other")
    q_fields = ["decision", "analyst_note"] + db_fields
    with (tmp_path / "review_queue.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=q_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows([good, same_article, reused, bad, waiting])
    monkeypatch.setattr(ar, "DB", tmp_path / "ci_events.csv")
    monkeypatch.setattr(ar, "REVIEW", tmp_path / "review_queue.csv")
    monkeypatch.setattr(ar, "RETIRED", tmp_path / "retired_ids.csv")
    monkeypatch.setattr(ar, "RUN_LOG", tmp_path / "run_log.md")
    ar.main()
    _, new_db = ar.read(tmp_path / "ci_events.csv")
    _, queue = ar.read(tmp_path / "review_queue.csv")
    assert len(new_db) == len(db) + 1 and new_db[-1]["event_id"] == "TEST-001"
    assert new_db[-1]["validation_status"] == "Verified"
    assert {r["event_id"] for r in queue} == {"TEST-002", "TEST-003", "TEST-005"}
    assert all(r["analyst_note"].startswith("Not applied") for r in queue if r["event_id"] != "TEST-005")
    assert "TEST-004" in (tmp_path / "retired_ids.csv").read_text(encoding="utf-8")
