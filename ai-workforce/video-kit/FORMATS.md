# Video formats: what the video desk rotates through

Owner, 2026-09-25: "why are we getting stuck on one idea for a video". The
desk makes **three different videos every weekday** from this library, and
never the same thing on repeat. Video Trend Scout picks the set; the rules
are at the bottom.

Two engines build them:
- **Market engine** (`prep.py` → `make.py`) builds `spy-tape` and `mag7-race`.
- **Scene engine** (`make_scenes.py`) builds everything else. A writer
  composes the video as a list of scenes in a `scenes.json`, and there's
  no code to write. The scene types are `hook`, `bignum`, `bullets`, `bars`,
  `line`, `compare`, `steps`, `quote`, `reveal` (question → answer) and
  `sources` (outro with sources). Each scene's `vo` is spoken while it is
  on screen, and scene length follows the voice.

## The library

| id | Series | Engine | Data source | Example |
|---|---|---|---|---|
| `spy-tape` | The SPY Tape | market | Webull SPY 5-min bars | "SPY gapped down 0.49%. The gap filled at 12:15." |
| `mag7-race` | Mag 7 Scoreboard (Fridays) | market | Webull daily bars | "One Mag 7 stock went +16.9% in four days." |
| `earnings-breakdown` | Where The Money Went | scenes | Webull `get_income_statement` | "Nvidia made $96.2B in one quarter. Here's where every $100 went." |
| `movers` | Today's Biggest Movers | scenes | Webull `get_gainers_losers` / `get_most_active` | Top 5 gainers and losers as bars, plus one "why it's moving" only with a cited source |
| `sector-board` | Sector Scoreboard | scenes | Webull `get_market_sectors` | Which sectors led and lagged this week |
| `earnings-week` | Earnings This Week | scenes | Webull `get_stock_earnings_calendar` | The 5 biggest reports coming, with dates |
| `explainer` | Trading, Explained | scenes | the definition + a real Webull example | VWAP, gap fill, opening range, theta, IV crush, float, short interest |
| `money-skill` | Make Money With AI | scenes | `MONEY-MAP.md` + cited research | "How people actually price an AI chatbot build", with real price bands from BRAND.md |
| `ai-this-week` | AI This Week | scenes | WebSearch; every story in 2+ independent outlets | "Google is putting AI chips in space on Oct 1." |
| `myth-fact` | Myth vs Fact | scenes | cited sources | "Myth: most day traders make money." Only with a real cited study. |
| `quiz` | Guess The Chart / Guess Which | scenes | Webull | Hide the ticker, show the move, reveal the answer |
| `studio` | Inside The AI Studio | scenes | this repo and the office DB | What the agents shipped this week, using real records only |

New series are welcome. Commentary Scriptwriter or Video Trend Scout adds
a row here (a `suggestions` doc from the hourly shift is fine) once it
has a real, checkable data source.

## Rotation rules (Video Trend Scout)

1. **Three videos per weekday run, from three different rows.** Fridays add
   `mag7-race` as a fourth.
2. **At least one market video** (`spy-tape`, `movers`, `sector-board`,
   `earnings-breakdown`, `earnings-week` or `quiz`), **one teaching video**
   (`explainer`, `money-skill` or `myth-fact`) and **one news or interactive video**
   (`ai-this-week`, `quiz` or `studio`).
3. **No series runs two days in a row**, and `spy-tape` runs at most twice a week.
   The one exception is a day the market did something unusual (a move over
   1% or a gap over 0.5%).
4. **No topic repeats within 30 days.** No second VWAP explainer, no second
   NVDA breakdown for the same quarter.
5. Check the office DB `videos` collection for history before picking.
   After delivery, add one doc per video: {date, series, topic, title,
   artifact, seconds}.

## Fact rules (Video Fact-Checker)

- Webull numbers: trace each one to the raw tool response saved in `raw/`.
- News: each story must appear in **2+ independent outlets** found via
  WebSearch, with the dates checked. Anything older than 14 days isn't "this week";
  the MIT robot story in Sep 2026 search results was a Dec 2025 paper, so it was dropped.
  Name the outlets in the `sources` scene and the caption.
- No reason for a price move unless a cited source states it. No trade calls.
  Market and money videos carry "Educational only. Not financial advice."
- Nothing about a private person, and no unverified claims about anyone.
