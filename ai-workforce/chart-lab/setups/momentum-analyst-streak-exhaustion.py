"""Consecutive-close streak exhaustion on 5-minute bars.
Added 2026-09-30 by momentum-analyst: the research queue was fully coded, so
this run used WebSearch (tradezella.com mean reversion guide, tradewink.com
mean reversion guide: a run of same-direction bars followed by a reversal
candle). Thresholds fixed before any P&L was seen. Untested here. Distinct from
td_setup_nine (9 closes vs close 4 bars back) and raschke_310.
"""


def streak_exhaustion(s):
    """Six consecutive 5-minute closes in one direction (each close beyond the
    previous close) that together move at least 2.5 ATR, followed by a bar that
    closes against the run on a body of at least 0.3 of its range. Signal is the
    reversal bar, leaning against the run. One signal per session, 10:00 to 14:30."""
    b = s.bars
    run, dirn = 0, 0
    for i in range(1, len(b)):
        d = 1 if b[i].c > b[i - 1].c else (-1 if b[i].c < b[i - 1].c else 0)
        atr = s.atr[i]
        x = b[i]
        if run >= 6 and d == -dirn and d != 0 and atr and 600 <= x.m < 870:
            move = abs(b[i - 1].c - b[i - 1 - run].c)
            rng = x.h - x.l
            if move >= 2.5 * atr and rng > 0 and abs(x.c - x.o) >= 0.3 * rng and (x.c < x.o if d < 0 else x.c > x.o):
                yield i, d
                return
        if d != 0 and d == dirn:
            run += 1
        else:
            run, dirn = (1, d) if d != 0 else (0, 0)


SETUPS = [
    dict(id='streak_exhaustion', name='Six-close streak exhaustion', family='momentum',
         detect=streak_exhaustion,
         rules="Six 5-minute closes in a row in one direction covering at least 2.5 ATR, then a bar that closes "
               "against the run with a real body (30%+ of its range): leans against the run (fade) or with it, "
               "both tested. One signal per session, 10:00 to 14:30."),
]
