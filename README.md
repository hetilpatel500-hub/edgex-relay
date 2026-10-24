# edgex-relay

Two things live in this repository:

1. **[daytrading-skills/](daytrading-skills/)**: 11 free, open-source day-trading skills for Claude, including the **Time Machine**, which takes your trade and simulates the rest of the trading day 10,000 times from historical price data to show how often it would have hit your target, hit your stop or ended in between. Start with the [skills README](daytrading-skills/README.md).
2. **[main.py](main.py)**: a small Flask relay that streams live 1-minute futures bars from Databento and serves them over HTTP (`/latest-bar`, `/candles`, `/health`). The skills can read from it with `--source relay`.

## Install the skills in Claude Code

```
/plugin marketplace add hetilpatel500-hub/edgex-relay
/plugin install daytrading-skills@edgex
```

| Skill | Job |
|-------|-----|
| chart-scanner | scan hundreds or thousands of charts for setups |
| news-catalyst | breaking news and SEC filings that could move a stock |
| premarket-game-plan | rank gappers and write if-then plans before the open |
| key-levels | support and resistance around the current price |
| market-regime | trend, range or volatile, and how hard to press |
| entry-signal | watch for the trigger, with a stop attached |
| position-sizer | shares or contracts for a fixed risk |
| exit-planner | stops, targets, scale-outs, trailing and time stops |
| **time-machine** | 10,000 simulated rest-of-days for your exact trade |
| risk-guard | daily loss limit, trade caps and cooldowns before each trade |
| trade-journal | log trades and find what actually works |

The skills analyse; they never place orders. Nothing here is financial advice.

## Run the relay

```bash
pip install -r requirements.txt
DATABENTO_API_KEY=... RELAY_API_KEY=... SYMBOL=MESZ6 gunicorn --workers 1 --threads 4 main:app
```

Then point the skills at it with `RELAY_URL=https://your-host RELAY_API_KEY=... --source relay`.
