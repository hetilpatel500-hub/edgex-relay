---
name: chart-scanner
description: Scans hundreds or thousands of daily stock charts for day-trading setups (gaps, volume spikes, breakouts and breakdowns, squeezes, bull flags, EMA pullbacks, relative strength, oversold bounces) and ranks the best candidates. Use when the user asks to "scan the market", "find stocks to trade today", "what's setting up", "find breakouts", "scan for gappers", "build a watchlist", or wants trading opportunities across many tickers.
---

# Chart scanner

Pulls daily bars for a universe, filters for liquidity, runs ten setup detectors and ranks the hits. Stocks that trigger several setups at once get a confluence bonus.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scan.py"                         # bundled ~200 liquid names
python3 "${CLAUDE_SKILL_DIR}/scripts/scan.py" --universe us-all --top 40   # every US-listed common stock
python3 "${CLAUDE_SKILL_DIR}/scripts/scan.py" --tickers AAPL,NVDA,TSLA --setups breakout,bull-flag
```

| option | use |
|--------|-----|
| `--universe` | `liquid` (default), `us-all` (~6,000 stocks from the Nasdaq Trader symbol directory; takes a few minutes on Yahoo), `us-all-etfs`, or a text file of tickers |
| `--setups` | any of `gap-up, gap-down, volume-spike, breakout, breakdown, squeeze, bull-flag, ema-pullback, relative-strength, oversold-bounce` |
| `--direction long\|short` | one side only |
| `--min-price 5 --min-dollar-volume 20e6 --min-atr-pct 2` | tighten the liquidity and movement filters (defaults: $2, $5M/day, any ATR) |
| `--gap-pct 4` | gap threshold (default 3%) |
| `--json > scan.json` | save results; the premarket-game-plan skill reads this file with `--from-scan` |
| `--csv-dir DIR` | offline: one `<SYMBOL>.csv` of daily bars per ticker |

While the market is open the last bar is today's partial bar; relative volume is projected to the full day with a typical intraday volume curve, so early-morning RVOL is a rough estimate. Data sources and installs: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

## Present the results

- Show the ranked table, then a one-line "why" for the top 5-10.
- Group by theme when it helps (gappers vs. breakouts vs. pullbacks), and point out sector clusters.
- Suggest the next step: news-catalyst on the top names to see *why* they are moving, then key-levels or premarket-game-plan.
- The score ranks how cleanly a chart matches a pattern. It is not a probability of profit; do not describe it as one.

## Guardrails

Analysis only: never place orders. Pattern hits are candidates for a closer look, not recommendations.
