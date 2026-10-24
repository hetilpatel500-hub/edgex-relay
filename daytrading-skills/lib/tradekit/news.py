"""Breaking-news catalysts: fetch headlines, classify them, rank what can move a stock."""

from __future__ import annotations

import difflib
import email.utils
import json
import math
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

YAHOO_RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={t}&region=US&lang=en-US"
SEC_8K = ("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={t}&type=8-K&dateb=&owner=include"
          "&count=10&output=atom")
WIRES = {
    "GlobeNewswire": "https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/"
                     "GlobeNewswire%20-%20News%20about%20Public%20Companies",
    "PR Newswire": "https://www.prnewswire.com/rss/news-releases-list.rss",
}

# (catalyst, pattern, impact 1-5, direction +1/-1/0). First match wins, so specific rules come first.
RULES = [
    ("bankruptcy", r"\b(chapter 11|bankruptcy|insolven\w+)\b", 5, -1),
    ("fda approval", r"\bfda\b.{0,40}\b(approv\w+|clear\w+|grants?)\b|\bapproval\b.{0,40}\bfda\b", 5, 1),
    ("fda setback", r"\b(complete response letter|crl|clinical hold|refuse to file)\b|"
                    r"\bfda\b.{0,30}\b(rejects?|declines?)\b", 5, -1),
    ("acquisition target", r"\b(to be acquired|agrees? to be acquired|takeover (bid|offer)|buyout offer|"
                           r"acquired by|go(es|ing)? private)\b", 5, 1),
    ("guidance raise", r"\b(raises?|lifts?|boosts?|increases?|ups)\b.{0,40}\b(guidance|outlook|forecast)\b", 5, 1),
    ("guidance cut", r"\b(cuts?|lowers?|slashes?|reduces?|withdraws?)\b.{0,40}\b(guidance|outlook|forecast)\b|"
                     r"\bwarns?\b.{0,30}\b(revenue|sales|profit|earnings)\b", 5, -1),
    ("earnings beat", r"\b(beats?|tops?|exceeds?|surpass\w*|crush\w*)\b.{0,40}\b(estimates?|expectations?|"
                      r"consensus|views?)\b|\brecord (revenue|quarter|sales|earnings)\b", 4, 1),
    ("earnings miss", r"\b(miss(es|ed)?|falls? short of|below)\b.{0,40}\b(estimates?|expectations?|consensus|"
                      r"views?)\b", 4, -1),
    ("short report", r"\bshort[- ](seller|report)\b|\b(hindenburg|muddy waters|citron)\b", 4, -1),
    ("offering / dilution", r"\b(public offering|private placement|registered direct|at-the-market|atm program|"
                            r"convertible (senior )?notes|shelf registration|prices? .{0,30}offering)\b", 4, -1),
    ("reverse split", r"\breverse (stock )?split\b", 4, -1),
    ("delisting risk", r"\b(delist\w*|going concern|non-?compliance|minimum bid)\b", 4, -1),
    ("index inclusion", r"\b(join|joins|added to|to join|inclusion in)\b.{0,30}\b(s&p 500|s&p midcap|"
                        r"nasdaq-100|russell (1000|2000|3000))\b", 4, 1),
    ("trial data", r"\b(phase (1|2|3|i{1,3})|topline|pivotal)\b.{0,60}\b(results?|data|met|meets|endpoint)\b", 4, 0),
    ("trading halt", r"\b(trading halt|halted)\b", 4, 0),
    ("upgrade", r"\bupgrade[sd]?\b|\braised to (buy|outperform|overweight)\b|"
                r"\binitiat\w+\b.{0,40}\b(buy|outperform|overweight)\b", 3, 1),
    ("downgrade", r"\bdowngrade[sd]?\b|\bcut to (sell|underperform|underweight|neutral|hold)\b", 3, -1),
    ("merger / acquisition", r"\b(acquires?|acquisition|merger|merge|to buy|deal to buy|divest\w*|spin[- ]?off)\b",
     3, 0),
    ("contract / partnership", r"\b(awarded|wins?|secures?|lands?)\b.{0,40}\b(contract|order|deal)\b|"
                               r"\b(partnership|collaboration|strategic alliance|supply agreement)\b", 3, 1),
    ("buyback", r"\b(buyback|share repurchase|repurchase program)\b", 3, 1),
    ("legal / regulatory", r"\b(lawsuit|sues|sued|subpoena|investigation|probe|sec charges|doj|antitrust|"
                           r"class action|recall)\b", 3, -1),
    ("executive change", r"\b(ceo|cfo|chief executive|chief financial)\b.{0,40}\b(resign\w*|steps? down|depart\w*|"
                         r"fired|ousted|appoint\w*|names?|retire\w*)\b", 3, 0),
    ("earnings report", r"\b(q[1-4]|first|second|third|fourth)[- ]quarter\b.{0,40}\b(results|earnings)\b|"
                        r"\breports?\b.{0,40}\b(results|earnings)\b|\bearnings call\b", 3, 0),
    ("price target", r"\bprice target\b|\bpt\b.{0,10}\b(raised|cut|to)\b", 2, 0),
    ("stock split", r"\bstock split\b", 2, 1),
    ("dividend", r"\bdividend\b", 1, 0),
    ("sec filing", r"^(8-k|6-k|10-q|10-k|s-1|s-3|424b\d)\b", 2, 0),
]
_COMPILED = [(name, re.compile(pat, re.I), impact, d) for name, pat, impact, d in RULES]

# 8-K item numbers say what a filing is about before anyone writes a headline
SEC_ITEMS = {
    "1.01": ("material agreement", 3, 0), "1.03": ("bankruptcy", 5, -1), "2.01": ("merger / acquisition", 4, 0),
    "2.02": ("earnings report", 3, 0), "2.05": ("restructuring / layoffs", 3, 0),
    "2.06": ("impairment", 3, -1), "3.01": ("delisting risk", 4, -1), "3.02": ("offering / dilution", 4, -1),
    "4.02": ("restatement", 5, -1), "5.02": ("executive change", 3, 0), "7.01": ("reg FD disclosure", 2, 0),
    "8.01": ("other material event", 2, 0),
}
_SEC_ITEM = re.compile(r"\bItems?\s+(\d\.\d\d)\b", re.I)

_POS = re.compile(r"\b(surg\w+|soar\w*|jump\w*|rall\w+|spik\w+|beat\w*|record|strong\w*|upbeat|raise[sd]?|"
                  r"wins?|approv\w+|gain\w*|rebound\w*|outperform\w*|bullish|higher|tops?)\b", re.I)
_NEG = re.compile(r"\b(plung\w+|tumbl\w+|sink\w*|sank|slump\w*|miss\w*|weak\w*|cut\w*|warn\w*|recall\w*|"
                  r"lawsuit|probe|downgrad\w+|fall\w*|fell|drop\w*|slid\w*|bearish|lower\w*|halt\w*|loss(es)?)\b",
                  re.I)


@dataclass
class Item:
    ticker: str
    title: str
    source: str
    link: str = ""
    published: datetime | None = None
    summary: str = ""
    catalyst: str = "other"
    impact: int = 1
    direction: int = 0
    score: float = 0.0
    age_hours: float | None = None
    duplicates: int = 0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["published"] = self.published.isoformat() if self.published else None
        d["direction"] = {1: "bullish", -1: "bearish", 0: "unclear"}[self.direction]
        return d


# ---------------------------------------------------------------- fetching

def _get(url: str, timeout: int = 20, user_agent: str | None = None) -> str:
    ua = user_agent or "Mozilla/5.0 (daytrading-skills news scanner)"
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/rss+xml,application/xml"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed feed URLs
        return resp.read().decode("utf-8", "replace")


def _parse_time(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip()
    try:
        dt = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def parse_feed(xml_text: str, ticker: str, source: str) -> list[Item]:
    """RSS 2.0 or Atom into Items."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    items = []
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        get = {c.tag.rsplit("}", 1)[-1]: c for c in node}
        title = (get["title"].text or "").strip() if "title" in get else ""
        if not title:
            continue
        link = ""
        if "link" in get:
            link = get["link"].get("href") or (get["link"].text or "").strip()
        when = None
        for k in ("pubDate", "published", "updated", "date"):
            if k in get:
                when = _parse_time(get[k].text)
                if when:
                    break
        summary = ""
        for k in ("description", "summary", "content"):
            if k in get and get[k].text:
                summary = re.sub(r"<[^>]+>", " ", get[k].text)
                summary = re.sub(r"\s+", " ", summary).strip()[:400]
                break
        items.append(Item(ticker, title, source, link, when, summary))
    return items


def fetch_ticker(ticker: str, sec: bool = True, getter=_get) -> tuple[list[Item], list[str]]:
    items, errors = [], []
    try:
        items += parse_feed(getter(YAHOO_RSS.format(t=urllib.parse.quote(ticker))), ticker, "Yahoo Finance")
    except Exception as exc:  # noqa: BLE001 - one dead feed should not stop the scan
        errors.append(f"Yahoo {ticker}: {exc}")
    if sec:
        ua = os.environ.get("SEC_USER_AGENT", "daytrading-skills research (set SEC_USER_AGENT)")
        try:
            for it in parse_feed(getter(SEC_8K.format(t=urllib.parse.quote(ticker)), user_agent=ua), ticker,
                                 "SEC EDGAR"):
                it.tags.append("primary source")
                items.append(it)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"SEC {ticker}: {exc}")
    return items, errors


_EXCH = re.compile(r"\((?:NYSE(?: American)?|NASDAQ|Nasdaq|NYSE Arca|OTCQX|OTCQB|CBOE)[:\s]+([A-Z][A-Z.\-]{0,5})\)")


def fetch_wires(tickers: list[str] | None, getter=_get) -> tuple[list[Item], list[str]]:
    """Press-release firehoses; keeps items tagged with one of ``tickers`` (or all if None)."""
    want = {t.upper() for t in tickers} if tickers else None
    items, errors = [], []
    for name, url in WIRES.items():
        try:
            raw = parse_feed(getter(url), "", name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
            continue
        for it in raw:
            found = _EXCH.findall(it.title + " " + it.summary)
            for sym in dict.fromkeys(found):
                if want is None or sym in want:
                    items.append(Item(sym, it.title, name, it.link, it.published, it.summary, tags=["press release"]))
    return items, errors


def load_items(path: str) -> list[Item]:
    """Headlines gathered elsewhere (web search, a broker connector) as JSON [{ticker,title,...}]."""
    with open(os.path.expanduser(path)) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("items") or data.get("news") or []
    out = []
    for d in data:
        title = d.get("title") or d.get("headline") or ""
        if not title:
            continue
        out.append(Item(str(d.get("ticker") or d.get("symbol") or "").upper(), title,
                        d.get("source") or "provided", d.get("link") or d.get("url") or "",
                        _parse_time(d.get("published") or d.get("time") or d.get("date")),
                        d.get("summary") or ""))
    return out


# ---------------------------------------------------------------- scoring

def classify(item: Item) -> Item:
    text = f"{item.title}. {item.summary[:200]}"
    if item.source == "SEC EDGAR":
        found = [SEC_ITEMS[n] for n in _SEC_ITEM.findall(item.summary) if n in SEC_ITEMS]
        if found:
            item.catalyst, item.impact, item.direction = max(found, key=lambda x: x[1])
            item.tags.append("8-K")
            return item
    for name, rx, impact, d in _COMPILED:
        if rx.search(item.title) or (name not in ("sec filing",) and rx.search(text)):
            item.catalyst, item.impact, item.direction = name, impact, d
            break
    if item.direction == 0:
        pos, neg = len(_POS.findall(text)), len(_NEG.findall(text))
        if item.catalyst == "price target":
            pos += 2 * bool(re.search(r"\b(raise[sd]?|lift\w*|boost\w*|hike\w*)\b", text, re.I))
            neg += 2 * bool(re.search(r"\b(cut\w*|lower\w*|slash\w*|trim\w*)\b", text, re.I))
        item.direction = (pos > neg) - (neg > pos)
    return item


def score(item: Item, now: datetime, half_life_hours: float = 6.0) -> Item:
    if item.published:
        item.age_hours = max(0.0, (now - item.published).total_seconds() / 3600)
        fresh = 0.5 ** (item.age_hours / half_life_hours)
    else:
        fresh = 0.5
    weight = 1.0 if ("primary source" in item.tags or "press release" in item.tags) else 0.9
    item.score = round(min(100.0, item.impact * 20 * (0.25 + 0.75 * fresh) * weight), 1)
    return item


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower())[:90]


def dedupe(items: list[Item], threshold: float = 0.82) -> list[Item]:
    kept: list[Item] = []
    for it in sorted(items, key=lambda x: -x.score):
        twin = next((k for k in kept if k.ticker == it.ticker and
                     difflib.SequenceMatcher(None, _norm(k.title), _norm(it.title)).ratio() >= threshold), None)
        if twin:
            twin.duplicates += 1
        else:
            kept.append(it)
    return kept


def rank(items: list[Item], hours: float = 24, now: datetime | None = None) -> list[Item]:
    now = now or datetime.now(timezone.utc)
    out = []
    for it in items:
        classify(it)
        score(it, now)
        if it.age_hours is not None and it.age_hours > hours:
            continue
        out.append(it)
    out = dedupe(out)
    out.sort(key=lambda x: (-x.score, x.age_hours if x.age_hours is not None else 1e9))
    return out


def ago(hours: float | None) -> str:
    if hours is None:
        return "?"
    if hours < 1:
        return f"{max(1, math.floor(hours * 60))}m"
    if hours < 48:
        return f"{hours:.0f}h"
    return f"{hours / 24:.0f}d"
