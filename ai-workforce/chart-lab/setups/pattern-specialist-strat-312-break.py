"""The Strat 3-1-2 on 30-minute candles, built from the 5-minute bars.
Added 2026-10-07 by pattern-specialist via WebSearch: Rob Smith's "The Strat" (3 = outside candle, 1 = inside candle,
2 = candle that breaks the inside candle's high or low; the same source as strat_212_reversal,
https://trendspider.com/learning-center/thestrat-candlestick-patterns-a-traders-guide/).
Rules fixed BEFORE any P&L was seen: 30-minute candles are 6-bar blocks from the open. A = outside candle (takes out both
the high and low of the candle before it), B = the next candle, inside A (lower high and higher low). After B completes,
the first 5-minute close beyond B's high (long) or B's low (short) is the signal. One signal per session, before 15:00.
Distinct from strat_212_reversal (15-minute, directional first candle) and hourly_inside_break (no outside candle).
"""


def strat_312_break(s):
    b = s.bars
    n = len(b)
    blocks = n // 6
    hi = lambda k: max(x.h for x in b[k * 6:k * 6 + 6])
    lo = lambda k: min(x.l for x in b[k * 6:k * 6 + 6])
    for k in range(2, blocks):
        ah, al = hi(k - 1), lo(k - 1)
        if not (ah > hi(k - 2) and al < lo(k - 2)):
            continue
        bh, bl = hi(k), lo(k)
        if not (bh < ah and bl > al):
            continue
        for i in range((k + 1) * 6, n):
            if b[i].m >= 900:
                break
            if b[i].c > bh:
                yield i, 1
                return
            if b[i].c < bl:
                yield i, -1
                return


SETUPS = [
    dict(id='strat_312_break', name='Strat 3-1-2 break (30-minute)', family='pattern',
         detect=strat_312_break,
         rules="On 30-minute candles, an outside candle (3) followed by an inside candle (1): the first 5-minute "
               "close above the inside candle's high leans long, below its low leans short (2), before 15:00. "
               "One signal per session; tested with and against."),
]
