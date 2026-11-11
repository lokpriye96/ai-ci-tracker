"""Step 3 - Validate: the guard-rails that stop LLM errors reaching the database.

Every extracted event gets a list of `checks`. Hard failures reject the event;
soft failures send it to the human review queue. Only clean events are
auto-approved as "Verified".
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

from .config import (BLOCKED_DOMAINS, COMPANIES, EVENT_TYPES, PRIMARY_DOMAINS,
                     STRATEGIC_THEMES, TRACKING_START)


def _words(s: str) -> list[str]:
    return re.sub(r"[^a-z0-9$%.]+", " ", (s or "").lower()).split()


def canonical_company(name: str) -> str | None:
    n = (name or "").lower()
    for company, aliases in COMPANIES.items():
        if any(a.lower() in n for a in aliases):
            return company
    return None


def source_tier(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    if any(host.endswith(d) for d in BLOCKED_DOMAINS):
        return "Blocked"
    if any(host.endswith(d) for d in PRIMARY_DOMAINS):
        return "Primary"
    return "Secondary"


def quote_in_text(quote: str, text: str, min_overlap: float = 0.9) -> bool:
    """Anti-hallucination check: is the evidence quote really in the article?
    Allows for small punctuation/whitespace differences."""
    q, t = _words(quote), " ".join(_words(text))
    if not q or not t:
        return False
    if " ".join(q) in t:
        return True
    hits = sum(1 for w in q if w in t)
    return hits / len(q) >= min_overlap and len(q) >= 5


def validate_event(ev: dict, today: date | None = None) -> dict:
    """Return the event with `checks`, `validation_status` and `confidence` set."""
    today = today or date.today()
    hard, soft = [], []
    # LLMs sometimes return null or numbers; normalise every text field to a string
    for k in ("company", "event_date", "date_precision", "event_type", "counterparty",
              "counterparty_type", "headline", "summary", "strategic_theme", "industry_focus",
              "value_note", "evidence_quote", "confidence", "source_name", "source_url"):
        v = ev.get(k)
        ev[k] = "" if v is None else str(v).strip()

    company = canonical_company(ev.get("company", ""))
    if not company:
        hard.append("company not in tracked list")
    ev["company"] = company or ev.get("company", "")

    if ev.get("event_type") not in EVENT_TYPES:
        hard.append(f"unknown event_type '{ev.get('event_type')}'")

    try:
        d = datetime.strptime(ev.get("event_date", ""), "%Y-%m-%d").date()
        if d > today + timedelta(days=1):
            hard.append("event date is in the future")
        elif d < TRACKING_START:
            hard.append("event before tracking window")
    except (ValueError, TypeError):
        hard.append("event_date not YYYY-MM-DD")

    tier = source_tier(ev.get("source_url", ""))
    ev["source_tier"] = tier
    if not ev.get("source_url"):
        hard.append("no source URL")
    elif tier == "Blocked":
        hard.append("source domain not accepted")

    if ev.get("strategic_theme") not in STRATEGIC_THEMES:
        soft.append("theme outside taxonomy")

    article_text = ev.get("_article_text", "")
    if not article_text:
        soft.append("article text unavailable (headline only)")
    elif not quote_in_text(ev.get("evidence_quote", ""), article_text):
        soft.append("evidence quote not found in article (possible hallucination)")

    try:
        ev["deal_value_usd_m"] = (None if ev.get("deal_value_usd_m") in (None, "")
                                  else float(ev["deal_value_usd_m"]))
    except (TypeError, ValueError):
        ev["deal_value_usd_m"] = None
        soft.append("deal value not a number")
    if ev.get("deal_value_usd_m") is not None and not re.search(
            r"\$|usd|dollar", article_text, re.I):
        soft.append("USD value given but article shows no USD figure")

    if str(ev.get("confidence", "")).lower() == "low":
        soft.append("model confidence low")

    ev["checks"] = "; ".join(hard + soft) or "all checks passed"
    if hard:
        ev["validation_status"] = "Rejected"
    elif soft:
        ev["validation_status"] = "Needs review"
    else:
        ev["validation_status"] = "Verified"
    if ev["validation_status"] != "Verified" and ev.get("confidence") == "High":
        ev["confidence"] = "Medium"
    return ev


def is_duplicate(ev: dict, existing: list[dict], window_days: int = 30) -> bool:
    """Same company + type + counterparty (or near-identical headline) within N days."""
    try:
        d = datetime.strptime(ev["event_date"], "%Y-%m-%d").date()
    except (KeyError, ValueError, TypeError):
        return False
    cp = (ev.get("counterparty") or "").lower().split(" (")[0].strip()
    head = set(_words(ev.get("headline", "")))
    for old in existing:
        if old.get("company") != ev.get("company"):
            continue
        try:
            od = datetime.strptime(str(old["event_date"]), "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if abs((od - d).days) > window_days:
            continue
        old_cp = str(old.get("counterparty") or "").lower().split(" (")[0].strip()
        same_cp = cp and old_cp and (cp in old_cp or old_cp in cp)
        old_head = set(_words(str(old.get("headline", ""))))
        overlap = len(head & old_head) / max(1, len(head | old_head))
        if (same_cp and old.get("event_type") == ev.get("event_type")) or overlap > 0.6:
            return True
    return False
