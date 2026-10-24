# Day-trading skills for Claude

Eleven free, open-source skills that turn Claude into a day-trading research desk. Each skill does one job: find setups, check the news, map levels, read the market, time the entry, size the position, plan the exit, check your risk, keep your journal. The headline act is the **Time Machine**: give it a trade and it replays the rest of the trading day 10,000 times from historical price data, so you see how often that exact trade hit the target, hit the stop or ended somewhere in between before you risk a dollar.

> **Analysis only.** No skill places, changes or cancels orders, even when a brokerage connector is available. Historical odds are not predictions and nothing here is financial advice. Day trading loses most people money; size accordingly.

## The 11 skills

| # | Skill | Job | Ask Claude something like |
|---|-------|-----|-----------------------------|
| 1 | **chart-scanner** | Scans hundreds or thousands of daily charts for gaps, volume spikes, breakouts, squeezes, bull flags, EMA pullbacks, relative strength and oversold bounces | "Scan the market for breakouts" |
| 2 | **news-catalyst** | Pulls breaking headlines and SEC 8-Ks, classifies the catalyst (guidance, FDA, M&A, dilution, downgrades...) with a bullish/bearish lean and impact score | "Why is SMCI moving?" |
| 3 | **premarket-game-plan** | Ranks gappers by gap vs ATR, premarket volume and catalyst; writes if-then plans around premarket and prior-day levels | "Build my game plan for the open" |
| 4 | **key-levels** | Support/resistance ladder: prior day, premarket, opening range, VWAP bands, pivots, volume profile, swing zones, weekly and 52-week levels | "Where are the levels on NVDA?" |
| 5 | **market-regime** | Trend-up / trend-down / range / volatile from index trend, efficiency, VIX and breadth, with a playbook and size multiplier | "Is today a trend day?" |
| 6 | **entry-signal** | Watches for opening-range breaks, VWAP reclaims and rejections, trend pullbacks, high/low-of-day breaks and red-to-green, with trigger, stop and quality score; can keep watching and alert | "Tell me when AMD triggers an entry" |
| 7 | **position-sizer** | Shares or contracts for a fixed risk, with slippage, commissions, buying power and futures point values | "How many shares if my stop is 186.20?" |
| 8 | **exit-planner** | Stop from structure or volatility, targets at real levels or R multiples, scale-outs, breakeven, trailing and time stops | "Where should I take profit?" |
| 9 | **time-machine** | Simulates the rest of the day 10,000 times for your exact trade and reports target / stop / in-between odds, expected R and stress tests | "What are the odds on this trade?" |
| 10 | **risk-guard** | Daily loss limit, max trades, losing-streak cooldown, open risk, no-trade windows: CLEAR / CAUTION / BLOCKED before each trade | "Can I take this trade?" |
| 11 | **trade-journal** | Logs trades and finds what works: by setup, hour, side and tag, tilt and overtrading patterns, and how well the Time Machine's odds matched reality | "How am I doing this month?" |

They chain together: regime → scanner → news → premarket plan → levels → entry signal → exit plan → **time machine** → sizer → risk guard → journal. Ask Claude for the whole morning routine and it will run them in order.

## The Time Machine

```
TIME MACHINE · DEMO long @ 97.68 · 2026-10-24 10:45 → 16:00 · 10,000 simulated rest-of-days
Plan: long @ 97.68 · stop 97.09 (-1R = 0.59) · T1 98.85 (+2.00R, 100%)
History: 42 sessions of 5m bars, 63 bars simulated, avg block 30 min, vol ×1.00

OUTCOMES
  Hit target ...............  33.6%  ██████████····················
  Hit stop .................  62.9%  ███████████████████···········
  Ended in between .........   3.5%  █·····························
     held to close, green ..   2.5%
     held to close, red ....   1.0%
  Made money overall .......  36.1%  ███████████···················

EXPECTANCY
  Average result +0.05R (+0.03/share)
  This reward:risk needs a 33.3% hit rate to break even; the simulation hit the target 33.6% of the time

EXACT REPLAY · each of the 42 eligible past sessions once, no reshuffling
  target 33.3% · stop 59.5% · in between 7.1% · made money 40.5% · avg +0.13R

ROBUSTNESS · same trade, different assumptions
  drift removed ...... target 31.3% · stop 64.8% · in between 3.9% · made money 34.1% · avg -0.01R
  volatility +25% .... target 34.8% · stop 64.0% · in between 1.1% · made money 35.8% · avg +0.05R
  worst-case fills ... target 33.1% · stop 62.8% · in between 4.0% · made money 36.0% · avg +0.04R
```

(Synthetic demo data; run `--source demo` to see it yourself.)

How it works:

1. Recent sessions (60 days of 5-minute bars by default, or 1-minute) are cut into clock-time slots. Each bar is stored as open/high/low/close moves relative to the previous close.
2. Each simulated path starts at your entry and, slot by slot, borrows the bar from a random past session **at the same time of day**, staying with that session for a random stretch (a stationary block bootstrap, 30 minutes on average). That keeps the open/lunch/close volatility rhythm and short-term momentum that a plain random walk throws away.
3. Moves are scaled to how volatile **today** has been so far versus the same window on past days.
4. The trade is managed on every path exactly as planned: stop, scale-out targets, breakeven after T1, trailing stop, flat-by time, gap-through fills at the open and slippage. Bars that touch both stop and target use the standard OHLC path rule, or worst-case on request.
5. Only sessions **before** the entry date are sampled, so testing a past trade has no look-ahead, and the report adds what actually happened that day.

You also get an exact replay over each historical session, reruns with the drift removed, volatility ±25% and worst-case fills, the distribution of R outcomes, time-to-target and time-to-stop, and optionally an HTML report with a price fan chart (`--html report.html`).

## Install

### Claude Code (recommended)

```
/plugin marketplace add hetilpatel500-hub/edgex-relay
/plugin install daytrading-skills@edgex
```

The skills need Python 3.10+ with numpy and pandas (plus yfinance for free data). The first time a skill runs without them it stops and prints the exact `pip install -r .../requirements.txt` command for your install, so you can just ask Claude to run it.

### From a clone

```bash
git clone https://github.com/hetilpatel500-hub/edgex-relay
cd edgex-relay/daytrading-skills
python3 -m pip install -r requirements.txt
claude --plugin-dir .
```

### Claude.ai or the API (single-skill uploads)

`python3 tools/package_skills.py` writes one self-contained zip per skill into `dist/` (the shared engine and data notes are copied into each). Upload the ones you want as custom skills in Claude's settings. Those sandboxes usually cannot reach Yahoo, so give Claude a CSV of bars or try `--source demo`.

## Market data

No paid data is needed. In order of preference, `--source auto` uses:

1. `--csv` files: your broker's export, or bars Claude fetched with any market-data connector you have
2. **Alpaca** (free account): set `ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` for years of 1-minute bars
3. **Yahoo Finance** via `yfinance` (no key): 1-minute bars for ~30 days, 5-minute for 60 days, daily for years

Plus `--source relay` for live futures bars from the [edgex-relay](../main.py) service in this repo, and `--source demo` for synthetic data. Details: [reference/data-sources.md](reference/data-sources.md).

Journal and risk settings are stored locally in `~/.daytrading-skills/` (`DAYTRADING_HOME` moves them).

## Layout

```
daytrading-skills/
├── .claude-plugin/plugin.json
├── skills/<skill>/SKILL.md          instructions Claude follows
├── skills/<skill>/scripts/*.py      thin command-line front ends
├── lib/tradekit/                    the shared, tested engine (data, levels, signals, montecarlo, ...)
├── reference/data-sources.md
├── tests/                           pytest suite
└── tools/package_skills.py          builds per-skill zips for claude.ai
```

Every script runs on its own too: `python3 skills/time-machine/scripts/time_machine.py --help`.

## Development

```bash
python3 -m pip install -r requirements.txt pytest
python3 -m pytest tests -q
```

Contributions welcome: new setups for the scanner, new entry signals, more data sources. Keep the math in `lib/tradekit`, add a test, and keep the skills analysis-only.

## License

MIT. See [LICENSE](LICENSE).
