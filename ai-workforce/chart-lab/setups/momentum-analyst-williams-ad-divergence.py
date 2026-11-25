"""Williams Accumulation/Distribution divergence at a new session extreme.
Added 2026-10-11 by momentum-analyst via WebSearch (luxalgo.com Williams A/D concept page, StockSharp indicator
docs, a TradingView educational script: all describe it as a price-only line built from true highs and lows,
used mainly for divergence; none report intraday results, so this is an untested adaptation). Rules fixed BEFORE
any P&L was seen. Distinct from obv/pvt divergence: no volume is used. Per 5-minute bar: if close > previous close
add close - min(low, previous close); if close < previous close subtract max(high, previous close) - close.
Signal at the close of a bar that sets a new session closing high (low) at least 6 bars after the previous closing
high (low), after bar 18 and before 14:30 ET, while the Williams A/D sits below (above) its value at that previous
extreme. One signal per session.
"""


def williams_ad_divergence(s):
    b = s.bars
    ad = 0.0
    hi_c = lo_c = None
    hi_i = lo_i = 0
    hi_a = lo_a = 0.0
    for i, x in enumerate(b):
        if i > 0:
            pc = b[i - 1].c
            if x.c > pc:
                ad += x.c - min(x.l, pc)
            elif x.c < pc:
                ad -= max(x.h, pc) - x.c
        if hi_c is None:
            hi_c = lo_c = x.c
            hi_i = lo_i = i
            hi_a = lo_a = ad
            continue
        late = i >= 18 and x.m <= 870 and i + 1 < len(b)
        if x.c > hi_c:
            if late and i - hi_i >= 6 and ad < hi_a:
                yield i, -1
                return
            hi_c, hi_i, hi_a = x.c, i, ad
        if x.c < lo_c:
            if late and i - lo_i >= 6 and ad > lo_a:
                yield i, 1
                return
            lo_c, lo_i, lo_a = x.c, i, ad


SETUPS = [
    dict(id='williams_ad_divergence', name='Williams Accumulation/Distribution divergence at a new session extreme',
         family='momentum', detect=williams_ad_divergence,
         rules="Williams Accumulation/Distribution (a price-only running sum: up bars add the close minus the true "
               "low, down bars subtract the true high minus the close) fails to confirm a new session closing high "
               "(it sits below its value at the previous high, at least 6 bars earlier) leans short; a new closing "
               "low on a line above its value at the previous low leans long. After 18 bars, before 14:30 ET, one "
               "signal a session; tested with and against."),
]
