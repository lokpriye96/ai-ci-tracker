"""Step 1 - Collect: pull recent headlines per competitor from Google News RSS,
then fetch each article's text so the LLM reads the source, not just a headline."""
from __future__ import annotations

import html
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

import requests

from .config import COMPANIES, QUERY_TEMPLATES

RSS_URL = "https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
HEADERS = {"User-Agent": "Mozilla/5.0 (CI-Tracker research bot; contact via GitHub)"}


@dataclass
class Article:
    company: str
    title: str
    url: str
    published: str  # ISO date
    source: str
    text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def search_news(company: str, days: int = 30, per_query: int = 10) -> list[Article]:
    """Return de-duplicated recent articles for one company."""
    seen, out = set(), []
    for tpl in QUERY_TEMPLATES:
        q = urllib.parse.quote(tpl.format(name=company) + f" when:{days}d")
        resp = requests.get(RSS_URL.format(q=q), headers=HEADERS, timeout=20)
        resp.raise_for_status()
        items = list(ET.fromstring(resp.content).iter("item"))[:per_query]
        for item in items:
            title = html.unescape(item.findtext("title", "")).strip()
            key = re.sub(r"\W+", "", title.lower())[:80]
            if not title or key in seen:
                continue
            seen.add(key)
            pub = item.findtext("pubDate")
            out.append(Article(
                company=company,
                title=title,
                url=item.findtext("link", ""),
                published=parsedate_to_datetime(pub).date().isoformat() if pub else "",
                source=item.findtext("source", ""),
            ))
        time.sleep(1)  # be polite
    return out


class _TextExtractor(HTMLParser):
    """Minimal HTML -> text (keeps <p> and headings, drops scripts/nav)."""
    SKIP = {"script", "style", "nav", "footer", "header", "aside", "form"}

    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        if tag in {"p", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\n\s*\n+", "\n\n", "".join(self.parts)).strip()


def fetch_text(url: str, max_chars: int = 12000) -> str:
    """Download an article and return readable text ('' on failure)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    parser = _TextExtractor()
    parser.feed(resp.text)
    return parser.text()[:max_chars]


def collect_all(days: int = 30, per_query: int = 10, with_text: bool = True) -> list[Article]:
    articles = []
    for company in COMPANIES:
        found = search_news(company, days=days, per_query=per_query)
        if with_text:
            for a in found:
                a.text = fetch_text(a.url)
        articles.extend(found)
        print(f"  {company}: {len(found)} articles")
    return articles
