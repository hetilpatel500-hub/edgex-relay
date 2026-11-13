"""The Strat 2-1-2 reversal on 15-minute candles, built from 5-minute bars.

From Rob Smith's "The Strat" (candle numbering: 1 = inside bar, 2U = takes
out only the prior high, 2D = only the prior low). 15-minute candles are
3-bar blocks from the open; a 2-1-2 reversal is a directional candle (2U or
2D), an inside candle, then the first 5-minute close beyond the inside
candle's opposite extreme. Before 15:00, one signal per session.
Reference: https://trendspider.com/learning-center/thestrat-candlestick-patterns-a-traders-guide/

Snapshot from the Edgex chart lab (12 US symbols, 2026-05-15 to 2026-10-23,
OOS from 2026-09-09): validated when FADED with the vwap+rvol filter and a
2 ATR stop held to the close: 46 OOS trades, 48% win, +0.38R avg, PF 1.75,
t 1.66. Re-test on your own data before relying on it.
"""


def strat_212_reversal(s):
    b = s.bars
    n = len(b)
    blocks = n // 3
    hi = lambda k: max(x.h for x in b[k * 3:k * 3 + 3])
    lo = lambda k: min(x.l for x in b[k * 3:k * 3 + 3])
    for k in range(2, blocks):
        ah, al, ph, pl = hi(k - 1), lo(k - 1), hi(k - 2), lo(k - 2)
        up, dn = ah > ph and al >= pl, al < pl and ah <= ph
        if not (up or dn):
            continue
        bh, bl = hi(k), lo(k)
        if not (bh < ah and bl > al):
            continue
        for i in range((k + 1) * 3, n):
            if b[i].m >= 900:
                break
            if up and b[i].c < bl:
                yield i, -1
                return
            if dn and b[i].c > bh:
                yield i, 1
                return


SETUPS = [
    dict(id='strat_212_reversal', name='Strat 2-1-2 reversal (15-minute)', family='pattern',
         detect=strat_212_reversal,
         rules="On 15-minute candles, a candle that takes out only the prior high (2U) or only the prior low (2D), "
               "then an inside candle: the first 5-minute close below the inside candle's low after a 2U leans "
               "short, and above its high after a 2D leans long, before 15:00."),
]
