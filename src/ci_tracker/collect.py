"""Step 1 - Collect: find recent news per competitor, then fetch each article's
text so the LLM reads the source itself, not just a headline.

Primary source: GDELT DOC API (free, no key, returns direct publisher URLs).
Fallback: Google News RSS (its links are redirects, so text may be unavailable).
A keyword filter keeps only headlines that look like an event, to save LLM calls."""
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
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
BING_RSS = "https://www.bing.com/news/search"
EVENT_WORDS = re.compile(
    r"acqui|buy|stake|invest|partner|alliance|collaborat|tie-up|teams up|launch|unveil|"
    r"introduc|agentic|\bAI\b|GenAI|generative|deal|contract|wins|GCC|capability cent|"
    r"Centre of Excellence|Center of Excellence", re.I)
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


def search_gdelt(company: str, days: int = 14, max_records: int = 40) -> list[Article]:
    """Recent English-language articles that mention the company and AI."""
    query = f'"{company}" (AI OR "artificial intelligence" OR agentic) sourcelang:english'
    params = {"query": query, "mode": "ArtList", "format": "json", "sort": "DateDesc",
              "maxrecords": str(max_records), "timespan": f"{days}d"}
    resp = requests.get(GDELT_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    try:
        items = resp.json().get("articles", [])
    except ValueError:  # GDELT returns plain text on rate-limit or bad query
        return []
    return parse_gdelt(company, items)


def search_bing(company: str) -> list[Article]:
    """Bing News RSS. Its links carry the real publisher URL in a `url=` parameter."""
    params = {"q": f'"{company}" AI', "format": "rss", "setlang": "en-gb"}
    resp = requests.get(BING_RSS, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return parse_bing(company, resp.content)


def parse_bing(company: str, xml_bytes: bytes) -> list[Article]:
    seen, out = set(), []
    for item in ET.fromstring(xml_bytes).iter("item"):
        title = html.unescape(item.findtext("title", "")).strip()
        link = item.findtext("link", "")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
        url = q.get("url", [link])[0]
        key = re.sub(r"\W+", "", title.lower())[:80]
        if not title or key in seen:
            continue
        seen.add(key)
        pub = item.findtext("pubDate")
        try:
            published = parsedate_to_datetime(pub).date().isoformat() if pub else ""
        except (TypeError, ValueError):
            published = ""
        source = ""
        for child in item:
            if child.tag.endswith("Source"):
                source = (child.text or "").strip()
        out.append(Article(company=company, title=title, url=url, published=published,
                           source=source or urllib.parse.urlparse(url).netloc))
    return out


def parse_gdelt(company: str, items: list[dict]) -> list[Article]:
    seen, out = set(), []
    for it in items:
        title = (it.get("title") or "").strip()
        key = re.sub(r"\W+", "", title.lower())[:80]
        if not title or key in seen:
            continue
        seen.add(key)
        sd = it.get("seendate", "")
        published = f"{sd[0:4]}-{sd[4:6]}-{sd[6:8]}" if len(sd) >= 8 else ""
        out.append(Article(company=company, title=title, url=it.get("url", ""),
                           published=published, source=it.get("domain", "")))
    return out


def looks_like_event(a: Article) -> bool:
    return bool(EVENT_WORDS.search(a.title)) and a.company.split()[0].lower() in a.title.lower()


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


def fetch_text(url: str, max_chars: int = 6000) -> str:
    """Download an article and return readable text ('' on failure)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    parser = _TextExtractor()
    parser.feed(resp.text)
    return parser.text()[:max_chars]


COLLECTION_STATS: list[str] = []


def collect_all(days: int = 14, per_query: int = 8, with_text: bool = True,
                max_per_company: int = 6, skip_urls: set[str] | None = None) -> list[Article]:
    """Collect, filter to likely events, cap per company, then fetch article text."""
    skip_urls = skip_urls or set()
    articles = []
    for company in COMPANIES:
        found, source = [], "none"
        for name, fn in (("GDELT", lambda: search_gdelt(company, days=days)),
                         ("Bing News", lambda: search_bing(company)),
                         ("Google News", lambda: search_news(company, days=days, per_query=per_query))):
            try:
                found = [a for a in fn() if looks_like_event(a)]
            except (requests.RequestException, ET.ParseError, ValueError):
                found = []
            if found:
                source = name
                break
        candidates = [a for a in found if a.url not in skip_urls]
        picked = candidates[:max_per_company]
        if with_text:
            for a in picked:
                a.text = fetch_text(a.url)
        articles.extend(picked)
        with_text_n = sum(1 for a in picked if a.text)
        msg = (f"{company}: {len(found)} event-like via {source}, {len(picked)} kept, "
               f"{with_text_n} with article text")
        COLLECTION_STATS.append(msg)
        print("  " + msg, flush=True)
        time.sleep(6)  # GDELT asks for one request every 5 seconds
    return articles
