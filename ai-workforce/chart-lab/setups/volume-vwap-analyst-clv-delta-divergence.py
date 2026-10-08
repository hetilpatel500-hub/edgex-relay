"""Cumulative intraday-intensity (CLV x volume) divergence on 5-minute bars.
Added 2026-10-01 by volume-vwap-analyst: the research queue was fully coded, so
this run used WebSearch (luxalgo.com Intraday Intensity: volume weighted by
where the close sits in the bar's range; tradingview.com / quantvps.com
Cumulative Volume Delta: price makes a new extreme the cumulative delta does
not). A bar-based stand-in for tick delta, which needs the tape. Thresholds
fixed before any P&L was seen. Distinct from volume_divergence_extreme (single
bar volume) and rsi_divergence (price oscillator).
"""


def clv_delta_divergence(s):
    """Cumulative sum of volume x (2*close - high - low)/(high - low) from the
    open. When a bar makes a new session high (low) at least 8 bars after the
    previous session high (low) but the cumulative sum sits below (above) its own
    value at that earlier extreme bar, and the bar closes back below (above)
    its open, signal against the extreme. One signal per side per session,
    10:30 to 14:30."""
    b = s.bars
    cum = []
    c = 0.0
    hi_i = lo_i = 0
    fired = set()
    for i, x in enumerate(b):
        r = x.h - x.l
        c += x.v * ((2 * x.c - x.h - x.l) / r if r > 0 else 0)
        cum.append(c)
        if i and 630 <= x.m < 870:
            if x.h > b[hi_i].h and i - hi_i >= 8 and cum[i] < cum[hi_i] and x.c < x.o and -1 not in fired:
                fired.add(-1)
                yield i, -1
            elif x.l < b[lo_i].l and i - lo_i >= 8 and cum[i] > cum[lo_i] and x.c > x.o and 1 not in fired:
                fired.add(1)
                yield i, 1
        if x.h > b[hi_i].h:
            hi_i = i
        if x.l < b[lo_i].l:
            lo_i = i


SETUPS = [
    dict(id='clv_delta_divergence', name='Cumulative buying/selling pressure divergence', family='volume',
         detect=clv_delta_divergence,
         rules="Add up each 5-minute bar's volume weighted by where it closed in its range (top = all buying, "
               "bottom = all selling). A new session high (low) at least 8 bars after the last one, with that running "
               "total below (above) where it stood at the earlier extreme, and a bar closing against the extreme, "
               "leans against the extreme (fade) or with it, both tested. One per side per session, 10:30 to 14:30."),
]
