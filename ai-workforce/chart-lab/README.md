# Chart Desk lab

Owner directives, 2026-09-26: "I want the chart desk to keep on improving every
moment, don't just let them sit around: learn new technical analysis, new
profitable patterns, use Webull's data to backtest the chart desk's knowledge
and improve using that", and "use heat map, level 2 data, POC, initial volume
breakout, protection level, initial balance breakout area, price action,
volume profile, deep trades, footprint chart, liquidity heatmap, VWAP and many
more ... make new patterns, test those out, make sure it's profitable; always
when the market is open keep track of all this and prices in real time".

**Analysis only.** The lab never places, stages or suggests orders, and only
uses Webull's read-only tools (`get_stock_bars`, `get_stock_tick`,
`get_stock_quotes`, `get_stock_capital_flow`, `get_stock_snapshot`). Edgex
Capital is a separate operation and nothing here touches it. Past results are
not a promise: the lab exists to separate ideas that held up on data they were
never tuned on from ideas that didn't.

## What's here

| File | What it does |
|---|---|
| `data/` | Webull bars, gzip CSV: `<SYM>_M5.csv.gz` (5-minute, regular hours) and `<SYM>_D.csv.gz` (daily) for SPY QQQ IWM DIA AAPL MSFT NVDA AMZN GOOGL META TSLA AMD |
| `ingest.py` | Merges saved `get_stock_bars` responses into `data/` |
| `core.py` | Sessions and levels: VWAP bands, 15-min opening range, initial balance, initial volume bar, volume profile (POC/VAH/VAL), yesterday's levels, swing structure with break of structure / change of character and the protected level; simulated exits and stats |
| `setups/*.py` | Detectors. Every file exports `SETUPS`, a list of `dict(id, name, family, rules, detect[, tf='D'])`; `detect(session)` yields `(bar index, +1/-1)` |
| `lab.py` | Backtests every setup (method below), writes `out/results.json`, `PLAYBOOK.md` and `frozen.json` |
| `publish.py` | Turns results into Office DB docs under `out/db/` |
| `live.py` | Live read of one symbol: levels, footprint rebuilt from ticks, big prints, level 2 book, money flow, playbook setups that fired today |
| `state.py` | Moves `frozen.json` and the day's tape rows through the DB (hourly sessions can't push) |
| `tape/` | One gzip JSONL per day: hourly order-flow rows per symbol (delta, big prints, book imbalance, walls, large-order money flow) |
| `PLAYBOOK.md` | The current playbook, generated |

## Method (never loosen it to make something pass)

- Signal at a bar's close, simulated entry at the next bar's open, round-trip
  costs of 2 bps (ETFs) / 3 bps (stocks). Stops and targets in ATR; intraday
  trades are flat at the close. If a bar touches stop and target, the stop counts.
- Each setup is tested with and against its signal ("fade"), with 9 filters
  and 7 exits. One variant is chosen on the first 70% of dates only, then
  judged once on the last 30% (held out).
- **validated**: in-sample ≥ +0.05R, held-out n ≥ 30, ≥ +0.05R, profit factor ≥ 1.1,
  t ≥ 1.5, at least half the symbols positive. **promising**: positive on both
  but short of that. **rejected** / **insufficient** otherwise.
- The first time a setup is validated or promising, its variant is **frozen**
  with the date. Every later trading day is a true forward test of that exact
  variant. A frozen setup with 30+ forward trades averaging below −0.05R is
  **retired**.
- Random entries lose about the cost of trading (−0.14 to −0.20R intraday);
  `results.json` reports each setup's edge over that.
- The more variants tried, the more likely a good number is luck. The lab
  records the count; the Devil's Advocate reads it before anything is called
  an edge.

## Three Routines

| Routine | When | Where it runs | Steps below |
|---|---|---|---|
| Edgex Chart Desk lab | hourly at :08 | fresh session, no connectors (can't reach Webull or push) | 1, 4-9 |
| Edgex Chart Desk live tape | weekdays 9:38-15:38 ET, hourly | the owner's connected session (Webull read-only) | 2-3 |
| Edgex Chart Desk data refresh | weekdays 16:21 ET | the owner's connected session (Webull read-only, can push) | daily run |

Routines on this account can't attach connectors to fresh sessions, which is
why the Webull reads run in the owner's session and the research runs fresh
on the bars already in `data/`.

## Hourly lab run steps

Run from `ai-workforce/chart-lab`. Real clock (`date -u +%FT%TZ`) for every
timestamp. The Office DB is https://claude.ai/artifact/NzBSM8bbGtbqhariCBzfoH.

1. **Sync state.** Read `chart_lab_state/frozen` from the DB (save it to a file,
   `python3 state.py pull FILE`). Read `repo_changes` docs with
   `status: "pending"` whose `file` starts with `ai-workforce/chart-lab/` and
   create those files locally, so detectors from earlier runs exist here too.
2. **Fresh bars** (live-tape Routine only). Find the last bar in `data/SPY_M5.csv.gz`. If a newer
   session has traded, call `get_stock_bars` (symbols SPY,QQQ,IWM,DIA with
   category US_ETF, then the 8 stocks with US_STOCK; timespan M5, count up to
   1200, trading_sessions RTH, real_time_required false) and `timespan D`
   (count 20); save each response to a file and run `python3 ingest.py M5 FILES`
   / `python3 ingest.py D FILES`.
3. **Live tape** (live-tape Routine only, 9:30-16:00 ET on weekdays). For each of the 12 symbols:
   `get_stock_tick` (count "1000", trading_sessions "RTH"),
   `get_stock_quotes` (depth "50"; if refused, "10"), and for the 8 stocks
   `get_stock_capital_flow` (count 5). Save each and run
   `python3 live.py SYM --ticks F --book F [--flow F] --db`. Then write every
   `out/db/chart_live/<SYM>.json` to `chart_live/<SYM>` and append the printed
   rows to `chart_lab_state/tape-<YYYY-MM-DD>` (`{day, rows: [...]}`; update,
   don't replace, the rows already there).
4. **Research one new idea.** Take the next open line of the research queue
   below (or, when it's empty, use WebSearch for a documented intraday
   technique the lab hasn't tested, and add it to the queue). The agent who
   owns that family writes the detector in a new `setups/<agent>-<topic>.py`,
   following the contract above, with rules text a trader can read. Order-flow
   ideas that need tick or book history go on the queue marked "waiting for
   tape" until `tape/` holds 30+ sessions.
5. **Backtest.** `python3 lab.py --only NEW_ID` to check it runs, then
   `python3 lab.py`. Never edit the method, costs or thresholds to rescue a
   setup; a rejected idea is a finished result.
6. **Publish.** `python3 publish.py "<2-3 sentence summary: what was tested,
   which agent built it, held-out result and status, anything that changed in
   the forward tests>"` and `python3 state.py push`. Write to the DB in one
   batch: every `out/db/chart_playbook/*.json`, the new
   `out/db/chart_research/*.json`, and `out/db/chart_lab_state/frozen.json`.
7. **Queue the code.** For every new or changed file under `setups/` and for
   `PLAYBOOK.md`, write one `repo_changes` doc (`op: "create"` with the whole
   file as `new_str`, `status: "pending"`). The daily after-close run commits them.
8. **Agents.** Update the `agents` doc of every Chart Desk agent who worked this
   run (see the table below): `status: "working"` or `"done"`, `task`, `result`
   (one line with the real numbers), `updatedAt`. Only these 20 ids; never
   create any other agents doc.
9. Never publish anything, message anyone, or trade. If a Webull call fails,
   say so in the research summary; never fill in numbers.

## Daily after-close run (Routine "Edgex Chart Desk data refresh")

1. `git pull`. Apply pending `repo_changes` under `ai-workforce/chart-lab/`
   (mark them applied with the commit hash after pushing).
2. `python3 state.py pull` the DB's `chart_lab_state/frozen`; for each
   `chart_lab_state/tape-*` doc, `python3 state.py tape FILE`, then delete the
   doc once the file is committed.
3. Fetch today's M5 and D bars for all 12 symbols (as in step 2 above), ingest.
4. `python3 lab.py`, `python3 publish.py "<daily summary with the forward-test
   changes>"`, `python3 state.py push`, write the DB batch.
5. Commit `data/`, `tape/`, `setups/`, `frozen.json`, `PLAYBOOK.md`,
   `out/results.json` and push.

## Research queue

Owner's list first. Tick marks mean tested (see `PLAYBOOK.md` for the result).

- [x] Initial balance breakout / failed breakout / IB sweep (session-gap-specialist)
- [x] Initial volume breakout (volume-vwap-analyst)
- [x] POC: pull to yesterday's POC, POC migration (volume-vwap-analyst)
- [x] Value area: 80% rule re-entry, edge rejection, acceptance outside value (volume-vwap-analyst)
- [x] Protected level: holds / breaks (change of character), BOS (price-structure-analyst)
- [x] VWAP reclaim, VWAP 2-sigma snap-back (volume-vwap-analyst)
- [x] Liquidity sweeps of yesterday's high/low and IB extremes; sweep then VWAP cross (smart-money-analyst)
- [x] Composite: IB + IVB outside value; protected level at VWAP (strategy-playbook-analyst)
- [ ] Fair value gap (3-bar imbalance) first retest (smart-money-analyst)
- [ ] Order block: last opposite candle before a displacement, first retest (smart-money-analyst)
- [ ] EMA 9/20 pullback in a trending session (trend-moving-average-analyst)
- [ ] Bollinger squeeze → expansion on 5-minute bars (volatility-analyst)
- [ ] Inside bar / NR4 on 5-minute bars at a session level (candlestick-specialist)
- [ ] Engulfing or hammer at VWAP, POC or IB extreme (candlestick-specialist)
- [ ] RSI(14) divergence at the day's high/low (macd-divergence-analyst)
- [ ] MACD histogram flip with VWAP agreement (macd-divergence-analyst)
- [ ] 61.8% retracement of the opening drive holding (fibonacci-harmonics-analyst)
- [ ] ABC pullback after an impulse leg (elliott-wave-analyst)
- [ ] Spring / upthrust at the IB extreme (wyckoff-phase-analyst)
- [ ] Double top/bottom at a prior-day level (pattern-specialist)
- [ ] Bull/bear flag after a 2-ATR impulse (pattern-specialist)
- [ ] Single prints / poor high or low from yesterday's profile revisited (volume-vwap-analyst)
- [ ] Open type (open-drive, open-test-drive, open-rejection-reverse, open-auction) (session-gap-specialist)
- [ ] Gap-and-go vs gap-fade split by relative volume (session-gap-specialist)
- [ ] Time-of-day filter study: which setups only work before 11:00 (risk-manager)
- [ ] Exit study: trailing stop on the protected level vs fixed ATR exits (risk-manager)
- [ ] Waiting for tape: footprint delta divergence at a level (volume-vwap-analyst)
- [ ] Waiting for tape: absorption, big sell prints at a level while price holds (volume-vwap-analyst)
- [ ] Waiting for tape: stacked imbalances continuation (volume-vwap-analyst)
- [ ] Waiting for tape: level 2 wall pulled vs wall held (liquidity heatmap) (smart-money-analyst)
- [ ] Waiting for tape: large-order money flow confirming the daily trend (strategy-playbook-analyst)

## Who does what

| Agent (`agents/` id) | Lab job |
|---|---|
| chart-reader | Data steward: pulls and ingests Webull bars, checks gaps and half days |
| price-structure-analyst | Structure setups: BOS, change of character, protected levels |
| trend-moving-average-analyst | Moving-average and trend setups |
| support-resistance-mapper | Session levels: prior-day high/low/close, pivots, round numbers |
| smart-money-analyst | Liquidity sweeps, fair value gaps, order blocks, level 2 walls |
| pattern-specialist | Classic patterns: flags, double tops/bottoms, triangles |
| candlestick-specialist | Candle patterns at levels that matter |
| momentum-analyst | RSI / Stochastic setups |
| macd-divergence-analyst | MACD and divergences |
| volume-vwap-analyst | VWAP, volume profile, POC, value area, IB/IVB, footprint and tape |
| fibonacci-harmonics-analyst | Retracement and extension setups |
| elliott-wave-analyst | Impulse / correction swing setups |
| volatility-analyst | Squeezes, NR bars, ATR expansion; daily volatility setups |
| session-gap-specialist | Opening range, IB, gaps, open types, time of day |
| wyckoff-phase-analyst | Springs, upthrusts, effort vs result |
| strategy-playbook-analyst | Runs lab.py and publish.py, keeps the playbook and the queue |
| risk-manager | Exits, stops, costs, time-of-day filters |
| options-strategist | Checks validated setups' typical move size and speed against 0DTE decay (analysis only) |
| devil-s-advocate | Overfitting checks: variants tried, random baseline, forward-test verdicts, retirements |
| head-of-desk | Signs off each run's summary and what enters the playbook |
