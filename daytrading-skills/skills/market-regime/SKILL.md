---
name: market-regime
description: Classifies the overall market as trending up, trending down, ranging or volatile from SPY/QQQ/IWM trend, efficiency, volatility percentile, VIX and breadth, with an early read on today's tape, and turns that into a playbook - position-size multiplier, setups to favor and setups to avoid. Use when the user asks "what's the market doing", "is it a trend day", "should I be aggressive today", "market conditions", "risk-on or risk-off", or before planning the trading day.
---

# Market regime

Answers "what kind of day is it?" so the other skills can lean the right way.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/regime.py"                 # SPY, QQQ, IWM + VIX
python3 "${CLAUDE_SKILL_DIR}/scripts/regime.py" --breadth --intraday
python3 "${CLAUDE_SKILL_DIR}/scripts/regime.py" --indexes SPY,QQQ --json
```

| option | use |
|--------|-----|
| `--indexes` | ETFs to read (default SPY,QQQ,IWM) |
| `--vix ^VIX` / `--vix none` | volatility index (Yahoo only) |
| `--breadth` | share of the liquid universe above its 20 EMA (downloads ~200 charts) |
| `--intraday` | trend-day vs. chop read from the first index's 5-minute bars today |

Data help: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

## Labels

| label | meaning | size |
|-------|---------|------|
| trend-up | indexes above rising EMAs, efficient moves | 100% |
| trend-down | below falling EMAs | 75% |
| range | mixed trend, choppy (efficiency under 0.3) | 75% |
| volatile | VIX 28+ or index ATR in the top 15% of the year | 50% |

## Present it

One line with the label and size, the 2-3 reasons that drove it, today's intraday read if available, and the playbook (favor / avoid). Pass the label to the entry-signal skill as `--regime <label>` so its quality scores account for it.

## Guardrails

The regime is a backdrop, not a signal. It changes intraday; re-run it after the first hour if conditions look different. Never place orders.
