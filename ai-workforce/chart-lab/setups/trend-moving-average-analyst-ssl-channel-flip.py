"""SSL Channel (Semaphore Signal Level, 10) flip with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (SSL channel: SMA of highs and SMA of lows, default 10;
a close above the high-average turns the state bullish, a close below the low-average turns it bearish; the flip is the signal).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: N = 10 simple averages built inside the session,
state flips on the close, signal on a flip when the close is on the same side of VWAP, 10:30 to 14:30 ET,
at most 2 signals per side per session.
"""


def ssl_flip(s):
    b = s.bars
    n = 10
    state, cnt = 0, {1: 0, -1: 0}
    for i in range(n - 1, len(b)):
        hi = sum(x.h for x in b[i - n + 1:i + 1]) / n
        lo = sum(x.l for x in b[i - n + 1:i + 1]) / n
        new = 1 if b[i].c > hi else -1 if b[i].c < lo else state
        flipped = new != state and state != 0
        state = new
        if not flipped or b[i].m < 630 or b[i].m >= 870:
            continue
        if state == 1 and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif state == -1 and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='ssl10_flip_vwap', name='SSL Channel (10) flip with VWAP', family='trend',
         detect=ssl_flip,
         rules="Average of the last 10 highs and of the last 10 lows. A close above the high-average turns the "
               "channel bullish, a close below the low-average turns it bearish. A flip with the close on the "
               "same side of VWAP leans that way, 10:30 to 14:30 ET, at most two signals per side per session; "
               "tested with and against."),
]
