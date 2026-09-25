# Video kit: data-driven shorts, rendered locally

Added 2026-09-25 by owner directive: the video agents make finished videos
and send them to the owner by email, instead of queuing posts that never
go out. This kit renders original, data-driven videos with no paid
credits and no third-party footage.

## What it makes

- `spy`: one SPY regular session as animated 5-minute candles with VWAP,
  the prior close, and callouts at the gap, low, biggest candle, high and
  close. Then a stats card and an outro.
- `mag`: a "guess which" hook, a bar race of the Magnificent 7 from the
  prior Friday's close through the latest close, the reveal, and an outro.

Each runs at 1080×1920 (Reels/Shorts/TikTok) or 1920×1080 (YouTube). The
layout switches automatically from `w`/`h`.

## Pipeline

1. **Data.** Pull Webull bars (read-only tools only):
   `get_stock_bars` with SPY M5 RTH for the session, and daily bars for the
   7 names plus SPY and QQQ. Write them into `data.js` as `SPY` and `MAG`.
   The current file holds the Sep 24, 2026 session and the Sep 18–24 week
   as a worked example. Every number on screen comes from here; never type
   one in by hand.
2. **Render.** Serve the folder (`python3 -m http.server 8765`), then run
   `node shoot.js spy 1080 1920 out.mp4`. It needs Playwright and an
   ffmpeg with libx264 (`pip install imageio-ffmpeg`, or set `FFMPEG`).
   `node shoot.js spy 1080 1920 stills 3 12 25` writes check frames.
3. **Music.** `python3 music.py <seconds> bed.wav <seed>` synthesizes a
   royalty-free bed that matches the video's length.
4. **Mux.** `ffmpeg -i out.mp4 -i bed.wav -c:v copy -c:a aac -b:a 160k -shortest final.mp4`.
5. **Deliver.** Files over about 20 MB can't be attached through the
   Gmail connector, so publish them on a private artifact page (player,
   caption, a Save button via the `downloads` capability) and email the
   owner that link together with the captions.

## Rules it follows

- The captions and outro say "Educational only, not financial advice" and
  name Webull as the source. Never add a trade call to a market video.
- Don't claim a reason for a move ("because of earnings…") unless a real,
  cited source says so. These videos show what happened, not why.
- Nothing here posts anywhere. The owner posts the files.

Fonts: Inter, Space Grotesk and JetBrains Mono, all under the SIL Open
Font License (`fonts/LICENSE-fonts.txt`).
