---
name: key-levels
description: Maps the support and resistance levels day traders watch around the current price - prior day high/low/close, premarket high/low, opening range, VWAP and its bands, floor pivots, volume-profile POC and value area, swing zones, 20-day and 52-week extremes, weekly levels and round numbers - merged into one ladder with strength ratings. Use when the user asks "where are the levels on X", "support and resistance", "where's VWAP", "what's the premarket high", "where would I put a stop", or needs levels for entries, stops or targets.
---

# Key levels

One ladder of levels above and below price, with nearby levels merged into confluence zones.

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/levels.py" --symbol NVDA
python3 "${CLAUDE_SKILL_DIR}/scripts/levels.py" --symbol SPY --orb 5 --count 8
python3 "${CLAUDE_SKILL_DIR}/scripts/levels.py" --symbol MES=F --json
```

| option | use |
|--------|-----|
| `--price` | measure distances from this price instead of the last trade |
| `--orb 5\|15\|30` | opening-range length (default 15 minutes) |
| `--profile-days` | sessions in the volume profile (default 5) |
| `--count` | levels per side (default 6) |
| `--json` | for other tools |

Uses 30 days of 5-minute bars with extended hours plus daily bars. Data help: `${CLAUDE_SKILL_DIR}/../../reference/data-sources.md`.

## Read the ladder

- **Stars** (1-5) are strength: prior-day and premarket extremes, VWAP and POC rate high; levels that coincide with others get stars added and list the others in parentheses.
- **ATRs** column: distance in daily ATRs. A level 0.1 ATR away is "here"; 1+ ATR away is a stretch for one day.
- The closing line gives room to the nearest level on each side and the reward:risk of a long from here.

## Present it

List the 2-3 most important levels on each side in words ("first resistance is the premarket high at 96.00, then yesterday's high at 97.40"), call out confluence, and say what a break or hold of the nearest level would mean. The exit-planner skill uses these same levels for stops and targets.

## Guardrails

Levels are reference points, not predictions. Never place orders.
