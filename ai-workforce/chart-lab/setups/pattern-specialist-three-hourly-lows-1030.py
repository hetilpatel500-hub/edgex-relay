"""Three lower hourly lows and highs in a row, read at 10:30 ET.
Added 2026-10-06 by pattern-specialist: from a public hourly-bar backtest write-up
(quantifiedstrategies.com, "intraday trading strategies backtest": long at the 10:30
close after the third lower low and lower high in a row). The README queue is fully coded,
so this took a documented technique the lab had not tested. Rules fixed before any P&L was seen.
"""


def _hourly(bars):
    return [(max(x.h for x in bars[k:k + 12]), min(x.l for x in bars[k:k + 12]))
            for k in range(0, len(bars), 12)]


def three_hourly_lows_1030(s):
    """Hourly bars are 12-bar blocks from 9:30 (the last block of a session may be partial). The
    sequence is the prior session's last two blocks plus today's 9:30-10:30 block. Three blocks in
    a row each with a lower high and lower low than the one before (the prior session's last two
    blocks and today's first, so four blocks making three steps) signal at the 10:30 close: long
    after the down run, short after the mirror (higher highs and higher lows). One check per session."""
    p = s.prior
    b = s.bars
    if p is None or len(b) < 12 or len(p.bars) < 36:
        return
    seq = _hourly(p.bars)[-3:] + _hourly(b[:12])[:1]
    if len(seq) < 4:
        return
    down = all(seq[k][0] < seq[k - 1][0] and seq[k][1] < seq[k - 1][1] for k in (1, 2, 3))
    up = all(seq[k][0] > seq[k - 1][0] and seq[k][1] > seq[k - 1][1] for k in (1, 2, 3))
    if down:
        yield 11, 1
    elif up:
        yield 11, -1


SETUPS = [
    dict(id='three_hourly_lows_1030', name='Three lower hourly highs and lows in a row, read at 10:30',
         family='pattern', detect=three_hourly_lows_1030,
         rules="Hourly bars (12 five-minute bars from 9:30). Look at the prior session's last three hourly bars and "
               "today's first one (9:30-10:30). If each of the three steps made a lower high and a lower low, signal at "
               "the 10:30 close (the published version buys it; the mirror with higher highs and higher lows is the "
               "short side). Tested with and against, one signal per session."),
]
