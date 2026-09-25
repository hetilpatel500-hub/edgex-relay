# Chart Desk

A 19-agent department built only to read the owner's chart screenshots.
It lives in its own room on the Studio Floor (north-east corner, door on
the west side) and opens from the **Chart Desk** button.

## How a run works

1. The owner drops, pastes or picks a screenshot (any ticker, any
   timeframe, even a phone photo of a screen) and optionally types the
   ticker, timeframe or a question.
2. **Full desk** (about 4-6 minutes):
   - **Chart Reader** reads the picture first: instrument, timeframe, price
     axis, last price, indicators shown, swings, recent candles. Everyone
     else works from those facts and checks them against the image.
   - Sixteen analysts run in parallel, each on one discipline with a
     written checklist it must go through item by item: price structure;
     trend and moving averages; support and resistance; supply/demand and
     smart money; chart patterns; candlesticks; momentum oscillators; MACD
     and divergences; volume and VWAP; Fibonacci and harmonics; Elliott
     waves; volatility and bands; sessions and gaps; Wyckoff phase;
     strategy playbook; risk.
   - **Devil's Advocate** checks every quoted price against the image and
     argues the other side.
   - **Head of Desk** weighs all of it and makes the call.
3. **Fast read** (about 1 minute): the Head of Desk alone works through the
   whole checklist in one pass.

The call gives: direction (up / down / sideways) with odds, confidence
and horizon, price now, target 1 and 2, the price that proves it wrong,
one trade idea with entry/stop/targets/reward-to-risk and its trigger,
reasons, what would flip it, risks, a key-level ladder, the devil's
advocate's warnings, and every analyst's checklist. The owner can ask
follow-up questions about the same chart.

## Rules

- **Runs on the owner's own Claude account**, from the page (the
  artifact's `sample` capability). The first run asks the owner to allow
  it; each full run is about 19 Claude calls with the image attached.
- **Analysis only.** Nothing on the desk connects to a brokerage or places
  orders. The Edgex Capital trading system stays separate.
- **Honest reads.** Prices come off the chart's axis and can be a tick or
  two off; an indicator that isn't on the chart is reported as "not
  shown", never invented. Confidence is calibrated (50 = coin flip).
- **Track record.** Every call is saved to the `chart_analyses`
  collection with a thumbnail. In History, the owner marks each one "hit
  target first", "proved wrong first" or "neither yet", and the desk shows
  its hit rate. Treat that number as meaningless until 20+ calls are
  scored.
- **Not part of the business shifts.** The Chart Desk agents have no docs
  in the `agents` collection and the hourly shifts never assign them work,
  never write to `chart_analyses`, and never count them for zero-idle.
  Their poses on the floor during a run are local to the page.
