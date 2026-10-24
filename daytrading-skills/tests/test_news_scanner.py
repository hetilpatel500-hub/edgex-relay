from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from tradekit import news as nw, scanner as sc

NOW = datetime(2026, 10, 23, 14, 0, tzinfo=timezone.utc)

RSS = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Acme raises full-year guidance after record quarter</title><link>https://x/1</link>
<pubDate>Thu, 23 Oct 2026 13:00:00 GMT</pubDate><description>&lt;p&gt;Shares jump&lt;/p&gt;</description></item>
<item><title>Acme lifts full-year guidance after record quarter</title><link>https://x/2</link>
<pubDate>Thu, 23 Oct 2026 12:30:00 GMT</pubDate></item>
<item><title>Old news: Acme declares quarterly dividend</title><pubDate>Mon, 13 Oct 2026 12:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>8-K - Current report</title><link href="https://sec.gov/a"/><updated>2026-10-23T09:00:00-04:00</updated>
<summary type="html">Items 2.02 Results of Operations; Item 9.01 Financial Statements</summary></entry>
</feed>"""


@pytest.mark.parametrize("title,catalyst,direction", [
    ("FDA approves Acme's lead drug", "fda approval", 1),
    ("Acme receives complete response letter from FDA", "fda setback", -1),
    ("Acme announces $200 million public offering of common stock", "offering / dilution", -1),
    ("Acme to be acquired by MegaCorp for $40 per share", "acquisition target", 1),
    ("Acme downgraded to Underperform at BofA", "downgrade", -1),
    ("Acme Q3 earnings miss estimates as sales slow", "earnings miss", -1),
    ("Acme files for Chapter 11 bankruptcy protection", "bankruptcy", -1),
    ("Analyst raises Acme price target to $95", "price target", 1),
    ("Acme to join S&P 500", "index inclusion", 1),
])
def test_classify(title, catalyst, direction):
    it = nw.classify(nw.Item("ACME", title, "test"))
    assert it.catalyst == catalyst and it.direction == direction


def test_parse_rss_rank_dedupe_and_window():
    items = nw.parse_feed(RSS, "ACME", "Yahoo Finance")
    assert len(items) == 3 and items[0].summary == "Shares jump"
    ranked = nw.rank(items, hours=24, now=NOW)
    assert len(ranked) == 1  # the near-duplicate folds in, the old dividend drops out
    assert ranked[0].duplicates == 1 and ranked[0].catalyst == "guidance raise"


def test_sec_8k_items_and_wire_tickers():
    sec = nw.parse_feed(ATOM, "ACME", "SEC EDGAR")
    it = nw.classify(sec[0])
    assert it.catalyst == "earnings report" and "8-K" in it.tags

    wire = """<rss><channel><item><title>Acme Corp (NASDAQ: ACME) wins $50M Army contract</title>
    <pubDate>Thu, 23 Oct 2026 13:30:00 GMT</pubDate></item></channel></rss>"""
    got, errs = nw.fetch_wires(["ACME"], getter=lambda url, **_: wire)
    assert not errs and {i.ticker for i in got} == {"ACME"}


def test_fetch_ticker_survives_dead_feeds():
    def boom(url, **_):
        raise OSError("blocked")

    items, errors = nw.fetch_ticker("ACME", getter=boom)
    assert items == [] and len(errors) == 2


def test_parse_nasdaq_directory():
    text = ("Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
            "AAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N\n"
            "QQQ|Invesco QQQ Trust|G|N|N|100|Y|N\n"
            "ZXZZT|NASDAQ TEST STOCK|G|Y|N|100|N|N\n"
            "ACMEW|Acme Corp - Warrant|G|N|N|100|N|N\n"
            "File Creation Time: 1023202608:00|||||||\n")
    assert sc.parse_nasdaq_directory(text) == ["AAPL"]
    other = ("ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\n"
             "BRK.B|Berkshire Hathaway Class B|N|BRK.B|N|100|N|BRK=B\n")
    assert sc.parse_nasdaq_directory(other) == ["BRK-B"]


def _daily(closes, volume=1e6, last_volume=None):
    idx = pd.date_range("2026-01-02", periods=len(closes), freq="B", tz="America/New_York")
    c = np.asarray(closes, float)
    df = pd.DataFrame({"open": np.r_[c[0], c[:-1]], "high": c * 1.005, "low": c * 0.995, "close": c,
                       "volume": volume}, index=idx)
    if last_volume:
        df.iloc[-1, df.columns.get_loc("volume")] = last_volume
    return df


def test_scanner_finds_breakout_and_filters_liquidity():
    rng = np.random.default_rng(3)
    base = list(50 + rng.normal(0, 0.3, 80))
    breakout = _daily(base + [54.0], last_volume=3e6)
    breakout.iloc[-1, breakout.columns.get_loc("high")] = 54.05
    quiet = _daily(list(50 + rng.normal(0, 0.3, 81)))
    illiquid = _daily(base + [54.0], volume=1_000, last_volume=3_000)
    rows, stats = sc.scan({"BRK": breakout, "QUIET": quiet, "THIN": illiquid}, sc.Filters(),
                          now=pd.Timestamp("2026-06-01 18:00", tz="America/New_York"))
    syms = {r["symbol"]: r for r in rows}
    assert "BRK" in syms and "breakout" in syms["BRK"]["setups"]
    assert "THIN" not in syms and stats["passed_filters"] == 2


def test_session_volume_curve_is_monotonic():
    pts = [sc.session_volume_fraction(m) for m in range(570, 961, 15)]
    assert pts[0] == 0 and pts[-1] == 1 and all(b >= a for a, b in zip(pts, pts[1:]))
