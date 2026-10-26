"""Multi-day balance area breakout (overlapping value areas).
Added 2026-10-01 by volume-vwap-analyst, from a WebSearch run (marketprofile.info
IB breakout strategy; bookmap.com market profile in intraday trading): several
days of overlapping value areas mean a balanced market, and a strong move out
of that balance is said to resume a trend (while IB breaks inside it are said
to fail). Rules and the 70% overlap threshold were fixed before any P&L was
seen; everything is known at the signal bar's close.
"""


def balance_area_break(s):
    p = s.prior
    if p is None or p.prior is None:
        return
    q = p.prior
    lo, hi = max(p.val, q.val), min(p.vah, q.vah)
    narrow = min(p.vah - p.val, q.vah - q.val)
    if narrow <= 0 or hi - lo < 0.7 * narrow:
        return
    top, bot = max(p.vah, q.vah), min(p.val, q.val)
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if b[i].c > top:
            yield i, 1; return
        if b[i].c < bot:
            yield i, -1; return


SETUPS = [
    dict(id='balance_area_break', name='Two-day balance area breakout', family='volume profile',
         detect=balance_area_break,
         rules="If yesterday's and the day before's 70% value areas overlap by at least 70% of the narrower one, "
               "the first 5-minute close after the initial balance (first hour) and before 14:00 beyond the "
               "outer edge of the two value areas leans in the break direction. Tested with and against; "
               "one signal per session."),
]
