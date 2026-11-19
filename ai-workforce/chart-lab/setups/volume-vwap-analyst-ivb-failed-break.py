"""Initial volume bar failed breakout.
Added 2026-10-01 by volume-vwap-analyst: volume/VWAP family. The queue was
empty apart from tape items; the owner's list names the initial volume
breakout, and ivb_break tests only the continuation. This tests the failure:
a close beyond the initial volume bar that is taken back within 3 bars.
"""


def ivb_failed_break(s):
    """After the initial volume bar (heaviest of the first 30 minutes) is
    complete, a 5-minute close beyond its high (low) that closes back inside
    the bar's range within the next 3 bars is a failed break; the signal is
    the close back inside, leaning against the break. 10:00-14:00, one per
    session."""
    b = s.bars
    hi, lo = s.ivb_hi, s.ivb_lo
    if hi <= lo:
        return
    start = max(s.ivb_i + 1, 6)
    for i in range(start, len(b) - 3):
        if b[i].m >= 840:
            break
        brk = 1 if b[i].c > hi else (-1 if b[i].c < lo else 0)
        if not brk:
            continue
        for j in range(i + 1, i + 4):
            if b[j].m >= 840:
                return
            if lo <= b[j].c <= hi:
                yield j, -brk
                return
            if brk * (b[j].c - (hi if brk == 1 else lo)) <= 0:
                break
        return


SETUPS = [
    dict(id='ivb_failed_break', name='Initial volume bar failed breakout', family='volume',
         detect=ivb_failed_break,
         rules="After the first 30 minutes, the heaviest 5-minute bar defines the initial volume bar. A close "
               "beyond its high or low that is taken back inside its range within 3 bars is a failed break; "
               "the close back inside leans against the break, 10:00 to 14:00. One signal per session."),
]
