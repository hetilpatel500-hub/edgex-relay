---
name: risk-guard
description: Enforces the trader's own risk rules - daily loss limit, max trades per day, cooldown after a losing streak, max open positions and open risk, per-trade risk cap, minimum reward:risk, no-trade time windows, giving back a green day and a pattern-day-trader reminder - and gives a CLEAR / CAUTION / BLOCKED verdict before each trade using today's journal. Use when the user asks "can I take this trade", "check my risk", "am I done for the day", "how much can I still lose today", "set my daily loss limit", or before any new entry.
---

# Risk guard

The rules you set when calm, checked when you are not.

## Set the rules once

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/risk_guard.py" init --account 30000 --max-risk-pct 1 \
  --max-daily-loss-pct 2 --max-trades 5 --max-losses-in-row 3 --cooldown 30 --min-rr 1.5
python3 "${CLAUDE_SKILL_DIR}/scripts/risk_guard.py" init --show
```

Other settings: `--max-daily-loss` (dollars), `--max-open`, `--max-open-risk-pct`, `--no-trade "09:30-09:35,15:55-16:00"`, `--protect-after 500 --max-giveback-pct 50` (once up $500, stop if half of the peak is given back). Settings live in `~/.daytrading-skills/risk.json` (`DAYTRADING_HOME` changes the folder). Ask the user for their numbers; do not invent an account size.

## Before every trade

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/risk_guard.py" check --symbol AAPL --side long \
  --entry 187.50 --stop 186.20 --target 190.10 --shares 200
python3 "${CLAUDE_SKILL_DIR}/scripts/risk_guard.py" status
```

The check reads today's trades from the trade-journal skill's CSV, so it is only as good as the journal. Exit code 1 means BLOCKED. `--time HH:MM` checks against a different time.

## Present it

Lead with the verdict:

- **BLOCKED**: say which rule and stop there. Do not help the user work around their own limit (no "just size down to 1 share" or "change the limit"). If they want to change a rule, suggest doing it outside market hours.
- **CAUTION**: list the cautions and let them decide.
- **CLEAR**: one line, plus the max size allowed.

Always say how much room is left before the daily stop.

## Guardrails

The pattern-day-trader line is a reminder to check the broker's current rules, not legal advice. Never place orders.
