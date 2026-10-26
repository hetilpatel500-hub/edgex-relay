"""Range-expansion day, first VWAP pullback in the day's direction.
Added 2026-10-06 by volatility-analyst: the README queue is fully coded, so this run took the
"trend days (range already near or above average daily range early) are bought/sold on pullbacks,
not chased" idea from ADR / range-expansion literature (continuation counterpart of adr_exhaustion,
which fades the extreme). Rules fixed before any P&L was seen.
"""


def range_expansion_vwap_pullback(s):
    """ADR = mean high-low of the previous 10 full sessions (at least 5). If the developing range
    reaches 70% of ADR by 11:00 ET, the day's direction is the side of VWAP price closed on at the
    time. After that, when a bar's low (high) touches VWAP and the bar closes back on the trend side
    of it, signal with the trend. One signal per session, to 14:30 ET."""
    ranges, p = [], s.prior
    while p is not None and len(ranges) < 10:
        ranges.append(p.hi - p.lo)
        p = p.prior
    if len(ranges) < 5:
        return
    adr = sum(ranges) / len(ranges)
    b = s.bars
    hi, lo = b[0].h, b[0].l
    direction = 0
    for i in range(1, len(b)):
        x = b[i]
        hi, lo = max(hi, x.h), min(lo, x.l)
        if not direction:
            if x.m <= 660 and hi - lo >= 0.7 * adr:
                direction = 1 if x.c > s.vwap[i] else -1
            continue
        if x.m >= 870:
            return
        if direction == 1 and x.l <= s.vwap[i] < x.c:
            yield i, 1
            return
        if direction == -1 and x.h >= s.vwap[i] > x.c:
            yield i, -1
            return


SETUPS = [
    dict(id='range_expansion_vwap_pullback', name='Range-expansion day, first VWAP pullback', family='volatility',
         detect=range_expansion_vwap_pullback,
         rules="When the day's range has already reached 70% of the 10-day average daily range by 11:00 ET, "
               "the side of VWAP price is on sets the day's direction. The first bar that touches VWAP and closes "
               "back on the trend side signals with the trend (tested with and against). One signal per session, "
               "until 14:30 ET."),
]
