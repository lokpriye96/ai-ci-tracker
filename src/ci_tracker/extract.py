"""Step 2 - Extract: turn one article into structured events with an LLM."""
from __future__ import annotations

from pathlib import Path

from .collect import Article
from .config import COMPANIES, COUNTERPARTY_TYPES, EVENT_TYPES, STRATEGIC_THEMES
from .llm import call_llm

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "extract_event.md"


def build_prompt(article: Article) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(
        companies=", ".join(COMPANIES),
        event_types=", ".join(EVENT_TYPES),
        themes=", ".join(STRATEGIC_THEMES),
        counterparty_types=", ".join(t for t in COUNTERPARTY_TYPES if t),
        title=article.title,
        source=article.source,
        published=article.published,
        url=article.url,
        text=article.text or "(article text unavailable - headline only)",
    )


def extract_events(article: Article) -> list[dict]:
    """Return raw event dicts, each tagged with its source article."""
    result = call_llm(build_prompt(article))
    events = result.get("events", []) if isinstance(result, dict) else []
    for ev in events:
        ev["source_name"] = article.source
        ev["source_url"] = article.url
        ev["_article_text"] = article.text
        ev["_article_title"] = article.title
    return events
