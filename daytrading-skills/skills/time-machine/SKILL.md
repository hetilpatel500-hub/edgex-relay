---
name: time-machine
description: Simulates the rest of the trading day 10,000 times for one specific trade (entry, stop, target) using historical intraday price data, and reports how often it would have hit the target, hit the stop, or ended in between, plus expected R, an exact replay over past sessions and stress tests. Use when the user asks "what are the odds on this trade", "backtest this trade", "simulate my trade", "run the time machine", "how often would this hit my stop", "monte carlo my entry", or wants historical odds before risking money on a day trade.
---

# Time Machine

Takes one trade and replays the rest of today thousands of times using remixed bars from recent sessions at the same time of day. Output: probability of target, stop and "in between" (held to the close, or took partials then stopped), probability of making money, average result in R, the spread of outcomes, an exact replay of each past session, and robustness reruns.

This is a statistical what-if, not a prediction. Say so when you present it.

## 1. Get the trade

You need: **symbol, side, stop**, and usually **entry** and **target(s)**. Defaults if the user does not say:

- entry: the last price before the entry time
- entry time: now (latest bar) during market hours; otherwise ask for `--time HH:MM` (and `--date` for a past day)
- target: ask, or use `--rr 2` and say you assumed 2R
- flat-by: session close (16:00 New York for stocks)

If the user already ran the exit-planner skill, use its plan file: `--plan plan.json`.

## 2. Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/time_machine.py" --symbol AAPL --side long \
  --entry 187.50 --stop 186.20 --target 190.10
```

Common options:

| option | use |
|--------|-----|
| `--target 189,191 --split 50,50` | scale out; stop moves to breakeven after T1 by default |
| `--trail-r 1` | runner trails 1R behind the best price after T1 |
| `--time 10:15 --date 2026-10-20` | test a past entry; the report adds what actually happened that day |
| `--interval 1m --days 29` | finer bars for tight stops (Yahoo keeps ~30 days of 1m) |
| `--shares 200` / `--point-value 5` | dollar results (futures: MES 5, ES 50, NQ 20) |
| `--html report.html` | self-contained page with a price fan chart and odds-over-time chart |
| `--json` | machine-readable output |
| `--sims 20000 --seed 7` | more paths / reproducible run |
| `--demean` | remove the sample's intraday drift |
| `--vol-scale none` or `1.3` | turn off or override volatility matching |
| `--ambiguous worst` | assume the stop came first whenever one bar touched both |

Data defaults to 60 days of 5-minute bars. For data sources, connectors, CSVs and installs see `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`. `--source demo` runs on fake data to show the user what the report looks like; label it as fake.

## 3. Present the result

Lead with the three numbers the user asked for, then the money line:

> Out of 10,000 simulated rest-of-days: **target 31%**, **stop 45%**, **in between 24%** (14% green, 10% red at the close). It made money 45% of the time, averaging **+0.08R** per trade.

Then, briefly:

- **Edge check**: compare the target hit rate with the breakeven rate the report prints. Thin or negative average R means no historical edge at this stop/target.
- **Exact replay** (each past session once, unshuffled) should roughly agree with the simulation. A big gap means the result depends on a few unusual days.
- **Robustness**: if "drift removed" flips the average R from positive to negative, the "edge" was the stock's recent trend, not the trade structure. Worst-case fills show how much tight stops depend on intrabar order.
- **Notes**: repeat any warning the script prints (thin history, tight stop vs bar size, ambiguous bars, volatility scaling).
- Useful tweaks the numbers suggest: e.g. many paths were up 1R and still lost → partials or a breakeven stop; target rarely reached before the close → closer target.

Offer the HTML report (`--html`) when the user would like charts.

## How it works (for questions)

Each past session is cut into same-clock slots. A path starts at the entry and, slot by slot, borrows the bar from a random past session at that same time of day, sticking with that session for a random stretch (stationary block bootstrap, 30 minutes on average) before switching. That keeps the open/lunch/close volatility rhythm and short-term momentum. Returns are scaled to how volatile today has been so far versus the same window historically (clipped 0.5x-3x). Each path is managed by the plan: gap-through fills at the open, slippage on stops and market exits, partial targets, breakeven, trailing stop, flat-by exit. When a bar touches both stop and target, the OHLC heuristic decides (up bar: low first; down bar: high first), or worst-case with `--ambiguous worst`. Only sessions before the entry date are used, so testing a past date has no look-ahead.

Limits to state when relevant: it assumes the rest of today behaves like a remix of the sampled sessions; it cannot know about news, halts, or an FOMC afternoon unless such days are in the sample; 60 sessions is a small sample; it does not model the order book, so very tight stops and illiquid stocks look better than reality.

## Guardrails

- Never place or suggest placing an order from this skill. It reports odds; the user decides.
- Do not call a trade "safe" or "guaranteed". Historical odds are not a forecast and this is not financial advice.
- If the user plans to log the trade, pass the "made money" probability to the trade-journal skill as `--predicted-win` so it can check calibration later.
