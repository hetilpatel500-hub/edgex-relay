"""Open relative to yesterday's last 30 minutes, confirmed by VWAP at 10:00.
Added 2026-10-04 by session-gap-specialist via WebSearch (TradingView open-source scripts and write-ups that
classify the day by where the open sits against the previous session's last 30-minute range and whether
VWAP holds). Rules fixed BEFORE any P&L was seen: last 6 bars of yesterday, decision at the 10:00 close,
first-half-hour range must not have re-entered yesterday's last-30 range.
"""


def prior_last30_open(s):
    """Yesterday's last 30 minutes (6 five-minute bars) give a range. If today opens above its high and, at the
    10:00 close, price is still above that high and above VWAP, lean long (trend day up). If it opens below
    its low and price is still below it and below VWAP, lean short. One signal per session."""
    p = s.prior
    if p is None or len(p.bars) < 6:
        return
    hi = max(x.h for x in p.bars[-6:])
    lo = min(x.l for x in p.bars[-6:])
    b = s.bars
    i = 5
    if len(b) <= i or b[i].m != 595:
        return
    c = b[i].c
    if s.open > hi and min(x.l for x in b[:i + 1]) > hi and c > s.vwap[i]:
        yield i, 1
    elif s.open < lo and max(x.h for x in b[:i + 1]) < lo and c < s.vwap[i]:
        yield i, -1


SETUPS = [
    dict(id='prior_last30_open', name="Open outside yesterday's last 30 minutes, holding at 10:00",
         family='session', detect=prior_last30_open,
         rules="When today opens above (below) the high (low) of yesterday's last 30 minutes and no bar in the "
               "first 30 minutes trades back into it, and at the 10:00 close price is above (below) VWAP, "
               "lean with the open. Tested with and against; one signal per session."),
]
