"""Raschke / Connors Momentum Pinball, first-hour breakout in the direction of a stretched prior day.
Added 2026-09-30 by momentum-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (mql5.com/en/articles/2825, WH SelfInvest,
StrategyQuant forum) for a documented, untested Street Smarts setup. Distinct
from rsi2_extreme and d_ibs_extreme: the daily reading is only a filter, the
entry is the break of the first hour's range.
"""
import core


def _pinball(s):
    """3-period Wilder RSI of the 1-day change in close (the LBR/RSI Pinball
    indicator) as of the prior session's close; None if the chain is too short."""
    closes, p = [], s.prior
    while p is not None and len(closes) < 30:
        closes.append(p.close)
        p = p.prior
    closes.reverse()
    if len(closes) < 10:
        return None
    diffs = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    return core.rsi(diffs, 3)[-1]


def momentum_pinball(s):
    """Prior day's Pinball reading under 30 arms a long, over 70 arms a short.
    After the first hour (9:30-10:30), the first bar that closes beyond the
    first-hour high (long) or low (short), before 14:00, is the signal. One per day."""
    r = _pinball(s)
    if r is None or 30 <= r <= 70:
        return
    d = 1 if r < 30 else -1
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if d == 1 and b[i].c > s.ib_hi or d == -1 and b[i].c < s.ib_lo:
            yield i, d
            return


SETUPS = [
    dict(id='momentum_pinball', name='Momentum Pinball: first-hour break after a stretched prior day', family='momentum',
         detect=momentum_pinball,
         rules="If yesterday's 3-period RSI of the daily change in close (Raschke's Pinball) closed under 30, "
               "look only for longs; over 70, only shorts. After the first hour, lean with the first close "
               "beyond that hour's high (long) or low (short), before 14:00. One per day."),
]
