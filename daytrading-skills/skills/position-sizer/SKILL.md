---
name: position-sizer
description: Calculates how many shares or futures contracts to trade so a stop-out loses a fixed amount (percent of account or dollars), accounting for slippage, commissions, lot size, buying power and margin, and shows the 1R/2R/3R profit ladder. Knows futures point values (MES, ES, NQ, MNQ, CL, GC and micros). Use when the user asks "how many shares should I buy", "position size", "how big should I go", "size this trade", "how many contracts", or gives an entry and stop and an account size.
---

# Position sizer

Size comes from the stop, not from conviction.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/position_sizer.py" --account 30000 --risk-pct 1 --entry 187.50 --stop 186.20
python3 "${CLAUDE_SKILL_DIR}/scripts/position_sizer.py" --risk-dollars 150 --entry 52.10 --stop 51.60 --slippage 0.02
python3 "${CLAUDE_SKILL_DIR}/scripts/position_sizer.py" --account 10000 --risk-pct 0.5 --symbol MESZ6 --entry 6012.25 --stop 6006.75
```

| option | use |
|--------|-----|
| `--account` | equity; when omitted, the account saved by risk-guard (`risk_guard.py init --account`) is used |
| `--risk-pct` / `--risk-dollars` | risk budget (default: risk-guard's per-trade limit, else 1%) |
| `--target` | adds reward:risk |
| `--symbol MESZ6`, `/MES`, `MES=F` or `--contract MES` or `--point-value 5` | futures point value; a bare `ES` or `CL` is treated as the stock |
| `--buying-power`, `--max-position-pct`, `--margin` | caps on size (defaults: position no larger than the account) |
| `--commission`, `--slippage`, `--lot` | per-unit costs and rounding |

The output names which constraint limited the size (risk budget, buying power, margin...).

## Present it

"**133 shares**, risking $173 (0.7% of the account) if the 186.20 stop is hit" plus the constraint that set it and the 1R/2R/3R ladder. If the account size came from the default ($25,000) rather than the user, say so and ask for theirs.

## Guardrails

Warn when risk is above 2% per trade, when the stop is so tight that slippage dominates, or when the position needs margin. This is arithmetic, not advice. Never place orders.
