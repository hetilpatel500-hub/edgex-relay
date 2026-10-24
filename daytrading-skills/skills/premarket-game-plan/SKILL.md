---
name: premarket-game-plan
description: Builds the morning game plan before the open. Ranks gappers by gap size versus ATR, premarket volume and catalyst, assigns A/B/C tiers, maps premarket high/low and prior-day levels, and writes if-then long and short plans for each in-play stock. Use when the user asks for a "premarket plan", "game plan for today", "morning prep", "which gappers to watch", "watchlist for the open", or wants to prepare before the trading day starts.
---

# Premarket game plan

The morning routine: what is in play, where the levels are, and what you will do if price goes either way.

## Workflow

1. **Regime**: run the market-regime skill first. It sets size and which setups to favor.
2. **Candidates**: run chart-scanner with `--setups gap-up,gap-down,volume-spike --json > scan.json`, or take the user's watchlist.
3. **Catalysts**: run news-catalyst on those tickers with `--json > news.json`.
4. **Plan**:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/premarket.py" --from-scan scan.json --news news.json --top 8
python3 "${CLAUDE_SKILL_DIR}/scripts/premarket.py" --tickers NVDA,TSLA,PLTR      # quick version
```

Options: `--tickers-file`, `--top N`, `--json`, plus the shared data flags (5-minute bars with extended hours, 30 days). Yahoo includes premarket bars; a CSV must include them for premarket levels to appear. Data help: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

5. **Calendar**: check today's scheduled macro events (CPI, jobs, FOMC, big earnings) with a calendar connector if available, or web search. Note the times; the first minutes around a release are no-trade zones.

## Present the plan

A short document the user can trade from:

- Regime line and size (from market-regime)
- Event times to avoid
- **Tier A** (in play: gap bigger than about 1 daily ATR, heavy premarket volume, real catalyst) with each if-then plan
- **Tier B** to watch, Tier C listed only
- One line per name on what would cancel the idea (e.g. "fails back under premarket low")

Then offer the entry-signal skill to watch the A names after the open, and the time-machine skill to check odds before committing.

## Guardrails

Plans are conditional ("if it does X, consider Y"), never instructions to buy. Never place orders.
