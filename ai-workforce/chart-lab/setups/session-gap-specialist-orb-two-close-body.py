"""15-minute opening range breakout confirmed by two strong closes.
Added 2026-10-04 by session-gap-specialist via WebSearch (Concretum ORB write-up and TradingView ORB scripts:
confirmation filters "two closes outside the range" and "candle body at least 60% of its range"). orb15 and
or5_break enter on the first close beyond the range; this waits for confirmation. Parameters fixed BEFORE any
P&L was seen: range = high/low of 09:30-09:45, two consecutive 5-minute closes beyond the same side, the second
bar's body at least 60% of its high-low range and in the break direction, signal at that close, before 11:00,
first signal only. The lab tests it with and against.
"""


def orb_two_close_body(s):
    b = s.bars
    hi, lo = s.or_hi, s.or_lo
    for i in range(4, len(b)):
        if b[i].m >= 660:
            return
        for d, out in ((1, lambda x: x.c > hi), (-1, lambda x: x.c < lo)):
            if out(b[i]) and out(b[i - 1]):
                rng = b[i].h - b[i].l
                if rng > 0 and d * (b[i].c - b[i].o) >= 0.6 * rng:
                    yield i, d
                    return


SETUPS = [
    dict(id='orb_two_close_body', name='15-min opening range break, two closes and a strong body', family='opening range',
         detect=orb_two_close_body,
         rules="The high and low of 09:30-09:45 set the range. Two consecutive 5-minute closes beyond the same side, "
               "the second with a body of at least 60% of its range in the break direction, before 11:00: lean "
               "that way at the second close, once per session. Tested with and against, like every setup."),
]
