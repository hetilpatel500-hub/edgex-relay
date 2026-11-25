"""Volume-confirmed 20-day breakout (daily).
Added 2026-10-04 by volume-vwap-analyst: the research queue held only tape items, so this run took the
documented rule that a breakout is only trusted when volume confirms it (Wyckoff/Weis effort-vs-result; Dow
volume-confirms-trend). d_donchian20 already tests the bare breakout; this tests whether the volume filter
adds anything. Rules fixed BEFORE any P&L was seen: 20-day channel, 1.5x the 50-day average volume,
close in the outer half of the day's range.
"""


def vol_confirmed_break(ser):
    n = len(ser.c)
    for j in range(51, n):
        hi20 = max(ser.h[j - 20:j])
        lo20 = min(ser.l[j - 20:j])
        avg = sum(ser.v[j - 50:j]) / 50
        if not avg or ser.v[j] < 1.5 * avg:
            continue
        rng = ser.h[j] - ser.l[j]
        if rng <= 0:
            continue
        pos = (ser.c[j] - ser.l[j]) / rng
        if ser.c[j] > hi20 and pos >= 0.5:
            yield j, 1
        elif ser.c[j] < lo20 and pos <= 0.5:
            yield j, -1


SETUPS = [
    dict(id='d_vol_confirmed_break', tf='D', name='Volume-confirmed 20-day breakout', family='volume (daily)',
         detect=vol_confirmed_break,
         rules="A daily close above the prior 20-day high (below the 20-day low) on volume at least 1.5x the "
               "prior 50-day average, closing in the upper (lower) half of the day's range, leans with the "
               "break into the next session. Tested with and against."),
]
