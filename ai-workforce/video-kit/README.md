# Video kit: the video desk's production line

Owner directive, 2026-09-25: the video agents make finished videos with a
voiceover, check them, and email them to the owner. The owner posts them.
This kit is how they do it with no paid credits and no third-party footage.

It runs in the **Edgex video desk** Routine: every weekday after the close,
with a Mag 7 week recap on Fridays. Any session with the shell, the Webull
connector (read-only tools) and Gmail can run it by hand the same way.

## What it makes

| Video | Format | What's in it |
|---|---|---|
| `spy` | 9:16 short | The day's SPY session drawn candle by candle, with VWAP and the prior close. The drawing pauses at each callout (open, low, biggest candle, high, close) while the voice explains it. Then a stats card and an outro. |
| `mag` | 9:16 short | A "guess which" hook, then a bar race of the Magnificent 7 from last Friday's close. Then the reveal and the scoreboard. |
| `recap` | 16:9 | Both of the above in one landscape cut for YouTube (only when both exist). |

Voice: Kokoro-82M (Apache-2.0), an offline neural voice installed from npm by
`setup.sh`, using male voice `am_michael` at speed 1.12. Music is synthesized per video.

## The run, step by step (each step names the agent who owns it)

Work in a scratch folder, not in the repo. `KIT=ai-workforce/video-kit`.

0. **Setup.** Run `bash $KIT/setup.sh` once per machine. It takes about 10 s when cached.
1. **Video Trend Scout** chooses today's set: always `spy`, and `mag` on
   Fridays (or when the week already has 3+ sessions and something moved
   more than 5%). No other topics until the owner asks.
2. **Data.** Pull with the Webull **read-only** tools only, and save each response
   **exactly as returned** (the full JSON) to a file:
   - `raw/spy_m5.json` ← `get_stock_bars` symbols ["SPY"], category US_ETF,
     timespan M5, trading_sessions "RTH", count 160
   - `raw/daily.json` ← `get_stock_bars` symbols AAPL,MSFT,NVDA,GOOGL,AMZN,
     META,TSLA,SPY,QQQ, category US_STOCK, timespan D, count 10
3. **Prep.** Run `python3 $KIT/prep.py raw/spy_m5.json raw/daily.json story.json [--mag]`.
   It refuses an incomplete session. It writes every number, the on-screen
   text (`script.*.hook/outro`), the voiceover (`script.*.vo`), the captions
   and a `facts` list that traces each number to its bar.
4. **Commentary Scriptwriter + Hook Writer** may rewrite `script.*` and
   `captions.*` in story.json for punch. Only words change. Every number
   must stay one that appears in `facts`. Keep a VO line under ~20 words,
   because the chart pauses while it plays.
5. **Video Fact-Checker** checks every number in `script` and `captions`
   against `facts`. Then it checks each `facts` value against the raw JSON
   (open/high/low/close/volume of the named bar). Any mismatch goes back to
   step 4. Never state a reason for a move ("because of earnings…") unless a
   real, cited source says it.
6. **Voiceover/TTS Agent + Video Editor Agent.** The editor runs `python3 $KIT/make.py story.json out/`, which takes about 7–9 minutes.
   It produces `out/Edgex_*_9x16.mp4`, `out/Edgex_recap_*_16x9.mp4`,
   `out/review_*.png` (frames at every scene and callout),
   `out/report.json` (duration, resolution, audio, loudness, the exact
   spoken text) and `out/index.html` (the delivery page).
7. **Video Last Touch** looks at the review sheets (open the PNGs) and reads
   `report.json`:
   - **Copyright Compliance Reviewer**: all visuals are generated from data, the voice is Kokoro, the music is synthesized. Pass unless something else crept in.
   - **Content Policy Reviewer**: "Educational only. Not financial advice." is on screen and in each caption. There is no buy/sell call and no price target.
   - **Defamation & Harassment Screen**: no claims about people or companies beyond the price data.
   - **Brand & Tone Final Check**: no clipped or overlapping text, the numbers are readable, the brand bar is there, and the spoken text in `report.json` reads naturally. A failure goes back to step 4 or 6 with the exact fix.
   - **Publish Coordinator (Video)**: every MP4 exists and `report.json` shows h264 at 1080×1920 or 1920×1080, an aac audio track, mean volume between −26 and −14 dB, duration under 60 s for shorts, and every file under 15 MB. Then it stamps CLEARED — VIDEO LAST TOUCH. (For this kit, this replaces the vidIQ compose-job check.)
8. **Chief of Staff** approves or denies the delivery and logs a `decisions` doc.
9. **Delivery (YouTube Shorts Specialist + Instagram Reels Agent).** Publish
   `out/index.html` as a **new** private Artifact with `capabilities:
   {"downloads": true}` and every `out/*.mp4` and `out/poster_*.jpg` as
   supporting files at the same names. Then email the owner
   (hetilpatel500@gmail.com) the page link, one line per video, and each
   caption. Files can't be attached through the Gmail connector because
   they're too large.

If any step fails, send nothing half-done. Email the owner one short
note saying what failed and why, and log it.

## Rules

- Webull read-only tools only: get_stock_bars and get_stock_snapshot. Never an order, watchlist or account tool.
- Nothing is posted to any platform. The owner posts.
- Market videos show what happened, never what to trade.

## Files

`prep.py` (data → story.json), `make.py` (voice, timing, render, music,
mix, review sheets, report, page), `render.html` (the animation, fully
data-driven), `shoot.js` (Playwright frame capture → ffmpeg), `music.py`,
`page.py`, `setup.sh`. `examples/` holds the Sep 24, 2026 data as a test
fixture (`prep.py examples/spy_m5_2026-09-24.json examples/daily_2026-09-24.json s.json --mag`).
Fonts are Inter, Space Grotesk and JetBrains Mono (SIL OFL).
