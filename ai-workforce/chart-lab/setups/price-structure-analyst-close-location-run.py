"""Three-bar close-location run to a new session extreme.
Added 2026-10-07 by price-structure-analyst via the lab queue (no existing setup measures consecutive
strong closes; this reads pure price action, not VWAP or profile levels).
Parameters fixed BEFORE any P&L was seen: between 10:00 and 14:00 ET, three consecutive 5-minute bars that each
close in the top 30% of their own range (bottom 30% for shorts), each with a higher close than the one before
(lower for shorts), and the third bar makes a new session high (low). Signal at the third bar's close, with the
move continuing (long) or faded ("fade" variant). One per side per session.
"""


def close_location_run(s):
    b = s.bars
    done = set()
    for i in range(5, len(b)):
        if b[i].m < 600 or b[i].m > 840:
            continue
        w = b[i - 2:i + 1]
        if any(x.h <= x.l for x in w):
            continue
        loc = [(x.c - x.l) / (x.h - x.l) for x in w]
        if all(q >= 0.7 for q in loc) and w[0].c < w[1].c < w[2].c and w[2].h >= max(x.h for x in b[:i + 1]) \
                and 1 not in done:
            done.add(1)
            yield i, 1
        elif all(q <= 0.3 for q in loc) and w[0].c > w[1].c > w[2].c and w[2].l <= min(x.l for x in b[:i + 1]) \
                and -1 not in done:
            done.add(-1)
            yield i, -1


SETUPS = [
    dict(id='close_location_run', name='Three strong closes into a new session extreme', family='structure',
         detect=close_location_run,
         rules="Between 10:00 and 14:00, three consecutive 5-minute bars each closing in the top 30% of their range "
               "with rising closes, the third printing a new session high, leans long; the mirror leans short. "
               "One per side per session; tested with and against."),
]
