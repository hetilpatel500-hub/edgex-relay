"""CCI(20) extreme re-entry.
Added 2026-10-02 by momentum-analyst: Lambert's Commodity Channel Index, the
classic reading that a close back inside +/-100 after an excursion beyond +/-200
marks an exhausted thrust (StockCharts / Investopedia CCI guides). Not yet in the
lab. Rules fixed before any P&L was seen.
"""


def cci_reentry(s):
    """CCI(20) on 5-minute typical price (h+l+c)/3 built inside the session:
    (tp - sma20) / (0.015 * mean absolute deviation). When CCI was below -200
    within the last 3 bars and this bar closes back above -100, it leans long;
    mirror for above +200 and back below +100. 10:30 to 14:30 ET, at most 2
    signals per side per session."""
    b = s.bars
    n = 20
    tp = [(y.h + y.l + y.c) / 3 for y in b]
    cci = [None] * len(b)
    for i in range(n - 1, len(b)):
        w = tp[i - n + 1:i + 1]
        m = sum(w) / n
        md = sum(abs(x - m) for x in w) / n
        cci[i] = (tp[i] - m) / (0.015 * md) if md > 0 else 0.0
    cnt = {1: 0, -1: 0}
    for i in range(n + 2, len(b)):
        if b[i].m < 630 or b[i].m >= 870 or cci[i] is None:
            continue
        rec = [c for c in cci[i - 3:i] if c is not None]
        if cci[i] > -100 and rec and min(rec) < -200 and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif cci[i] < 100 and rec and max(rec) > 200 and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='cci_extreme_reentry', name='CCI(20) extreme re-entry', family='momentum',
         detect=cci_reentry,
         rules="Commodity Channel Index (20 five-minute bars, typical price): after CCI dips below -200 "
               "within the last three bars and a bar closes back above -100, it leans long; the mirror "
               "(above +200, then back under +100) leans short. 10:30 to 14:30 ET, at most two signals "
               "per side per session."),
]
