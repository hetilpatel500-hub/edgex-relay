"""Thin-volume morning extreme: the first hour closes at its high (low) on less volume than yesterday's first hour.
Added 2026-10-07 by volume-vwap-analyst (participation vs. price extension; low-volume extension is often
read as unsupported, high-volume as accepted). Lab tests it with and against.
Parameters fixed BEFORE any P&L was seen: signal at the close of the 10:30 bar (bar 11); the close sits in the
top (bottom) 10% of the initial balance range; the IB range is at least 1 ATR; first-hour volume is below 80%
of yesterday's first-hour volume; one per session.
"""


def thin_morning_extreme(s):
    p = s.prior
    if p is None or len(s.bars) < 12 or len(p.bars) < 12:
        return
    rng = s.ib_hi - s.ib_lo
    if rng <= 0 or not s.atr[11] or rng < s.atr[11]:
        return
    v_today = sum(x.v for x in s.bars[:12])
    v_prior = sum(x.v for x in p.bars[:12])
    if v_prior <= 0 or v_today >= 0.8 * v_prior:
        return
    c = s.bars[11].c
    if c >= s.ib_hi - 0.1 * rng:
        yield 11, 1
    elif c <= s.ib_lo + 0.1 * rng:
        yield 11, -1


SETUPS = [
    dict(id='thin_morning_extreme', name='Thin-volume first-hour extreme', family='volume',
         detect=thin_morning_extreme,
         rules="At 10:30 the close is in the top (bottom) 10% of the first-hour range, the range is at least one "
               "ATR, and first-hour volume is under 80% of yesterday's first hour. One signal per session; "
               "tested with and against."),
]
