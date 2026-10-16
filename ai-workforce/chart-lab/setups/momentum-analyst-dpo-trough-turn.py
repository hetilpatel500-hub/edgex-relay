"""Detrended Price Oscillator (10) trough/peak turn with a confirming candle, 5-minute session bars.
Added 2026-10-14 by momentum-analyst via WebSearch (LightningChart / Capital.com DPO write-ups): DPO = close minus the
SMA(n) shifted back n/2+1 bars strips the trend and leaves the short cycle; the documented entry is a trough below zero
that starts to turn up, with a price reversal candle as the trigger. Not in the lab before (DPO never tested).
Parameters fixed BEFORE any P&L was seen: n = 10, shift = 6 bars, session-only (restarted each day).
Long at the close of the first bar between 10:30 and 14:30 ET where DPO[i-1] < 0, DPO[i-1] <= DPO[i-2], DPO[i] > DPO[i-1]
and the bar closes above its open (mirror short: DPO[i-1] > 0, a peak, turns down, bar closes below its open).
One per side per session.
"""


def dpo_turn(s):
    b = s.bars
    n, sh = 10, 6
    dpo = [None] * len(b)
    for i in range(len(b)):
        j = i - sh
        if j - n + 1 >= 0:
            dpo[i] = b[i].c - sum(x.c for x in b[j - n + 1:j + 1]) / n
    done = {1: False, -1: False}
    for i in range(2, len(b)):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        if None in (dpo[i], dpo[i - 1], dpo[i - 2]):
            continue
        if not done[1] and dpo[i - 1] < 0 and dpo[i - 1] <= dpo[i - 2] and dpo[i] > dpo[i - 1] and b[i].c > b[i].o:
            done[1] = True; yield i, 1
        elif not done[-1] and dpo[i - 1] > 0 and dpo[i - 1] >= dpo[i - 2] and dpo[i] < dpo[i - 1] and b[i].c < b[i].o:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='dpo_trough_turn', name='Detrended Price Oscillator (10) trough/peak turn', family='momentum',
         detect=dpo_turn,
         rules="DPO(10) (close minus the 10-bar average shifted back 6 bars) is below zero, bottoms and ticks up "
               "on a bar that closes above its open (mirror: above zero, peaks, ticks down on a down bar), between "
               "10:30 and 14:30. One signal per side per session; tested with and against."),
]
