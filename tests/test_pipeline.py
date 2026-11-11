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
