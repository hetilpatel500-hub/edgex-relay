---
name: news-catalyst
description: Tracks breaking news that could move specific stocks. Pulls fresh headlines (Yahoo Finance, SEC 8-K filings, press-release wires), classifies each catalyst (earnings beat/miss, guidance, FDA, M&A, offerings and dilution, up/downgrades, legal, index changes) with a bullish/bearish lean and an impact score. Use when the user asks "why is X moving", "any news on my watchlist", "check catalysts", "what's the news on these gappers", "is there a reason it's up", or wants breaking news for stocks they might trade.
---

# News catalyst

Finds what is moving a stock and how much it matters for a day trade.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/news_scan.py" --tickers NVDA,SMCI,PLTR
python3 "${CLAUDE_SKILL_DIR}/scripts/news_scan.py" --tickers-file watchlist.txt --hours 12 --wires
python3 "${CLAUDE_SKILL_DIR}/scripts/news_scan.py" --wires-only --hours 2     # anything new on the wires
python3 "${CLAUDE_SKILL_DIR}/scripts/news_scan.py" --tickers NVDA --json > news.json
```

| option | use |
|--------|-----|
| `--hours` | look-back window (default 24) |
| `--wires` / `--wires-only` | add GlobeNewswire + PR Newswire press releases (matched by "(NASDAQ: XYZ)" tags) |
| `--no-sec` | skip SEC EDGAR 8-K filings (EDGAR asks for a contact in `SEC_USER_AGENT`, e.g. `"Jane Doe jane@example.com"`) |
| `--input file.json` | classify headlines you gathered elsewhere: a JSON list of `{ticker, title, published, source, link}` |
| `--json` | save for the premarket-game-plan skill (`--news news.json`) |

Scores mix catalyst impact (bankruptcy, FDA, guidance and buyouts are 5/5; dividends 1/5) with freshness (6-hour half-life). Near-duplicate headlines are folded together and counted.

## When the feeds are blocked or thin

1. If a news or brokerage connector is available, pull headlines with it, save them as the `--input` JSON and rank them with the script.
2. Otherwise use web search for `"<TICKER> stock news today"` and the company's investor-relations page, then pass what you find through `--input`.
3. For anything rated impact 4-5, open the primary source (the 8-K, the press release) before summarizing it.

## Present the results

For each ticker: the top catalyst, its lean (▲ bullish, ▼ bearish, • unclear), how old it is, and one line on why it matters for a day trade. Flag:

- **dilution** (offerings, ATMs, convertibles): gap-ups often fade
- **"priced in"** risk: news more than a day old, or a stock already up several ATRs
- **unclear direction** on big catalysts (trial data, M&A where the company is the buyer): read the source first

The classifier is keyword-based. Re-read headlines yourself and correct obvious misreads instead of repeating them.

## Guardrails

Do not present headlines as trade recommendations or invent news. Quote and link sources. Never place orders.
