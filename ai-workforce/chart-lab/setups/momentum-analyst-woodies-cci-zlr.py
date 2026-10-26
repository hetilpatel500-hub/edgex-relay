"""Woodies CCI zero-line reject (ZLR) with VWAP agreement, 5-minute bars.
Added 2026-10-13 by momentum-analyst via WebSearch (Woodies CCI: 14-period CCI, the zero-line reject is a momentum
pullback entry that buys the resumption of an established trend; sources are vendor/broker write-ups, not backtests,
and give no 5-minute numbers, so the thresholds below are this lab's fixed reading).
Parameters fixed BEFORE any P&L was seen: CCI length 14 on typical price (h+l+c)/3, built inside the session.
Long at the close of bar i between 10:30 and 14:30 ET when: CCI was above zero on at least 5 of the 6 bars i-7..i-2
(established uptrend), the prior bar's CCI sits within +/-50 of zero (the pullback reached the zero line), CCI is now
rising and above zero, and the close is above session VWAP. Mirror for short. At most one signal per side per session.
"""


def woodies_cci_zlr(s):
    b = s.bars
    n = 14
    tp = [(x.h + x.l + x.c) / 3 for x in b]
    cci = [None] * len(b)
    for i in range(n - 1, len(b)):
        w = tp[i - n + 1:i + 1]
        m = sum(w) / n
        md = sum(abs(v - m) for v in w) / n
        cci[i] = 0.0 if md == 0 else (tp[i] - m) / (0.015 * md)
    cnt = {1: 0, -1: 0}
    for i in range(n + 6, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        prev = cci[i - 7:i - 1]
        if any(v is None for v in prev) or cci[i - 1] is None:
            continue
        if (sum(1 for v in prev if v > 0) >= 5 and abs(cci[i - 1]) <= 50 and cci[i] > cci[i - 1] and cci[i] > 0
                and b[i].c > s.vwap[i] and cnt[1] < 1):
            cnt[1] += 1
            yield i, 1
        elif (sum(1 for v in prev if v < 0) >= 5 and abs(cci[i - 1]) <= 50 and cci[i] < cci[i - 1] and cci[i] < 0
                and b[i].c < s.vwap[i] and cnt[-1] < 1):
            cnt[-1] += 1
            yield i, -1


SETUPS = [
    dict(id='woodies_cci_zlr', name='Woodies CCI zero-line reject with VWAP', family='momentum', detect=woodies_cci_zlr,
         rules="CCI(14) on typical price has been above zero on at least 5 of the 6 bars before the last two (an "
               "established uptrend), the prior bar pulled back to within 50 of the zero line, and now CCI turns up "
               "back above zero with price closing above VWAP: leans long (mirror for short). Between 10:30 and 14:30 "
               "ET, one signal per side per session; tested with and against."),
]
