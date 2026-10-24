---
name: trade-journal
description: Logs day trades to a local CSV journal and analyzes them - win rate, profit factor, expectancy in R, drawdown, streaks, results by setup, hour, side and tag, tilt and overtrading patterns, and whether the time-machine's predicted odds matched what actually happened. Use when the user says "log this trade", "I just closed...", "journal", "how am I doing", "what are my stats", "which setups work for me", "review my trading", or "what time of day do I lose money".
---

# Trade journal

Every trade logged, so the numbers can tell you what works.

## Log trades

```bash
J="${CLAUDE_SKILL_DIR}/scripts/journal.py"
python3 "$J" add --symbol AAPL --side long --entry 187.50 --exit 189.90 --shares 200 --stop 186.20 \
  --setup ORB --entry-time "2026-10-23 09:52" --exit-time "2026-10-23 10:40" --tags "a+,news"
python3 "$J" open --symbol NVDA --side short --entry 131.20 --shares 100 --stop 132.00 --setup "VWAP rejection"
python3 "$J" list --open
python3 "$J" close --id 3f9a1c2e --exit 129.80
```

- Always ask for the **initial stop**: without it the journal cannot measure R.
- Use setup names consistently (the entry-signal names work well: ORB, VWAP reclaim, Trend pullback, HOD break, Red-to-green).
- If the trade was run through the time machine, add `--predicted-win <made-money probability>` and `--predicted-r <average R>`.
- Futures: `--point-value 5` for MES, 50 for ES.
- Times default to now (New York). The journal lives at `~/.daytrading-skills/journal.csv`; `--journal PATH` or `DAYTRADING_HOME` changes it. The risk-guard skill reads the same file.

Importing from a broker: if a brokerage connector can list filled orders, or the user exports a CSV, pair buys and sells into round trips and log each with `add`. Confirm the mapping with the user before writing many rows.

## Review

```bash
python3 "$J" stats
python3 "$J" stats --since 2026-09-01 --setup ORB
python3 "$J" --json stats
```

Present: net P&L, win rate, expectancy in R, profit factor, max drawdown; the best and worst setup and hour; the "what the numbers say" insights; and the time-machine calibration when there are 5+ predicted trades (Brier under 0.25 beats a coin flip). End with one or two concrete changes the data supports, such as dropping a losing setup or a cooldown rule. Keep in mind that fewer than about 30 trades is a small sample.

## Guardrails

The journal stays on the user's machine. Do not upload it anywhere unless they ask. Never place orders.
