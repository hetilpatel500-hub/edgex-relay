"""Noise Area breakout (Zarattini, Aziz, Barbon 2024, "Beat the Market", SPY intraday momentum).
Added 2026-09-30 by session-gap-specialist via WebSearch (SSRN 4824172, Concretum Group).
Bands around the open sized by the typical move so far at each time of day over
the last 14 sessions; a close outside them at a half-hour mark is treated as
abnormal demand/supply. Parameters (14 days, 1.0 sigma, half-hour checks) are
the paper's and were fixed before any P&L was seen. Only the entry is tested
here; exits come from the lab's standard grid.
"""


def noise_area_break(s):
    """Upper band = max(open, prior close) * (1 + sigma), lower = min(open, prior close) * (1 - sigma),
    sigma = mean of the last 14 sessions' |close/open - 1| at the same time of day.
    At each half-hour mark from 10:00 to 15:30 the first close outside the band is the signal
    (long above, short below). One per day."""
    b = s.bars
    if s.prior is None:
        return
    up_hi = max(s.open, s.prior.close)
    up_lo = min(s.open, s.prior.close)
    for i in range(len(b)):
        m = b[i].m
        if (m + 5) % 30 or m + 5 < 600 or m + 5 > 930:
            continue
        vals, p = [], s.prior
        while p is not None and len(vals) < 14:
            for j, x in enumerate(p.bars):
                if x.m == m:
                    vals.append(abs(x.c / p.bars[0].o - 1))
                    break
            p = p.prior
        if len(vals) < 14:
            continue
        sig = sum(vals) / 14
        if b[i].c > up_hi * (1 + sig):
            yield i, 1
            return
        if b[i].c < up_lo * (1 - sig):
            yield i, -1
            return


SETUPS = [
    dict(id='noise_area_break', name='Noise Area breakout (14-day average move bands around the open)', family='session',
         detect=noise_area_break,
         rules="Build bands around the open from the average move at this time of day over the last 14 sessions "
               "(upper from the higher of open and yesterday's close, lower from the lower). At a half-hour mark "
               "from 10:00 to 15:30, the first close outside a band leans with the break. One per day."),
]
