"""Gann HiLo Activator state flip with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (Robert Krausz's HiLo Activator as described by LuxAlgo
and ProRealCode: SMA of the last 3 highs and SMA of the last 3 lows; a CLOSE above the high average flips the state up,
a close below the low average flips it down, intrabar pokes do not count). Parameters fixed BEFORE any P&L was seen:
length 3 (the published default), averages taken over the three bars before the current one. Long at the close of the
first bar between 10:30 and 14:30 ET that flips the state from down to up while the close is above session VWAP
(mirror for short). One signal per session.
"""

N = 3


def gann_hilo_flip(s):
    b = s.bars
    if len(b) < 20:
        return
    state = 0
    for i in range(N, len(b) - 1):
        hi = sum(x.h for x in b[i - N:i]) / N
        lo = sum(x.l for x in b[i - N:i]) / N
        new = 1 if b[i].c > hi else -1 if b[i].c < lo else state
        flipped = new != state and state != 0
        state = new
        if not flipped or b[i].m < 630 or b[i].m > 870:
            continue
        if state == 1 and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if state == -1 and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='gann_hilo_flip', name='Gann HiLo Activator flip with VWAP', family='trend',
         detect=gann_hilo_flip,
         rules="The HiLo Activator averages the highs and the lows of the last three bars. A 5-minute close above the "
               "high average turns the state up, a close below the low average turns it down. Between 10:30 and 14:30, "
               "the first flip from down to up that closes above VWAP leans long; the mirror flip below VWAP leans "
               "short. One signal per session; tested with and against."),
]
