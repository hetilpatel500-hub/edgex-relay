"""Engulfing or hammer at VWAP, POC or IB extreme.
Added 2026-09-27 by candlestick-specialist: candlestick family, next open
line of the research queue in ai-workforce/chart-lab/README.md.
"""


def _near_level(s, i, atr):
    """True if bar i's range sits within 0.25 ATR of session VWAP, the
    developing POC so far, or an IB extreme -- all known at the time, no
    look-ahead."""
    if not atr:
        return False
    lo, hi = s.bars[i].l, s.bars[i].h
    levels = [s.vwap[i]]
    if i >= 11:
        levels += [s.ib_hi, s.ib_lo]
    if i >= 5:
        import core
        poc, _, _ = core.profile(s.bars[:i + 1])
        levels.append(poc)
    return any(lo - 0.25 * atr <= lvl <= hi + 0.25 * atr for lvl in levels)


def engulfing_hammer_at_level(s):
    """A bullish engulfing (this candle's body fully covers the prior body,
    closing up) or a hammer (lower wick >= 2x the body, closing in the upper
    half of the range) at a session level leans long; the bearish mirrors
    (bearish engulfing, shooting star) lean short."""
    b = s.bars
    fired = 0
    for i in range(1, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        o, h, l, c = b[i].o, b[i].h, b[i].l, b[i].c
        rng = h - l
        if rng <= 0:
            continue
        po, pc = b[i - 1].o, b[i - 1].c
        body = abs(c - o)
        upper_wick, lower_wick = h - max(o, c), min(o, c) - l
        bull_engulf = c > o and pc < po and c >= po and o <= pc
        bear_engulf = c < o and pc > po and c <= po and o >= pc
        hammer = c >= o and lower_wick >= 2 * body and upper_wick <= 0.25 * rng
        shooting_star = c <= o and upper_wick >= 2 * body and lower_wick <= 0.25 * rng
        d = 1 if (bull_engulf or hammer) else (-1 if (bear_engulf or shooting_star) else None)
        if d is None:
            continue
        if not _near_level(s, i, s.atr[i]):
            continue
        fired += 1
        yield i, d


SETUPS = [
    dict(id='engulfing_hammer_at_level', name='Engulfing / hammer at a session level', family='candlestick',
         detect=engulfing_hammer_at_level,
         rules="A bullish engulfing or hammer candle within 0.25 ATR of VWAP, the developing POC, or an IB "
               "extreme leans long; a bearish engulfing or shooting star at the same levels leans short, "
               "before 15:00."),
]
