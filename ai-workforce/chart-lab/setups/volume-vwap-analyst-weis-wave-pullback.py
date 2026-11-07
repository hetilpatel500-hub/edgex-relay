"""Weis-wave volume: low-volume pullback after a high-volume thrust, 5-minute session bars.
Added 2026-10-14 by volume-vwap-analyst via WebSearch (David Weis, "Trades About to Happen"; Wyckoff effort vs result
read per swing wave instead of per bar). The lab has bar-level effort/result (squat bar, volume dry-up pullback) but not
wave-summed volume. Rules fixed BEFORE any P&L was seen: waves from a causal zigzag, a leg ends when the close gives back
1.0 ATR from the leg's extreme (high for up-legs, low for down-legs); wave volume = sum of bar volume from the leg's
start to its extreme bar. Long at the close of the bar that confirms the end of a pullback (down-leg), when the thrust
before it (up-leg) moved >= 2 ATR, the pullback retraced <= 62% of the thrust, pullback volume <= 0.6 x thrust volume,
and the close is above session VWAP. Mirror short. 10:00 to 14:30 ET, one signal per side per session.
"""


def weis_wave(s):
    b = s.bars
    n = len(b)
    if n < 15:
        return
    legs = []                 # (dir, start_i, ext_i, vol, start_price, ext_price)
    d = 0
    start = 0
    hi_i = lo_i = 0
    done = {1: False, -1: False}
    for i in range(1, n):
        if b[i].h > b[hi_i].h:
            hi_i = i
        if b[i].l < b[lo_i].l:
            lo_i = i
        thr = 1.0 * s.atr[i]
        flip = 0
        if d >= 0 and b[i].c < b[hi_i].h - thr and hi_i >= start and (d == 1 or hi_i > lo_i):
            # an up-leg ends at hi_i (or the first leg is an up-leg)
            sp = b[start].l if d == 1 else b[lo_i].l
            st = start if d == 1 else lo_i
            legs.append((1, st, hi_i, sum(x.v for x in b[st:hi_i + 1]), sp, b[hi_i].h))
            d, start, lo_i = -1, hi_i, i
            flip = -1
        elif d <= 0 and b[i].c > b[lo_i].l + thr and lo_i >= start and (d == -1 or lo_i > hi_i):
            sp = b[start].h if d == -1 else b[hi_i].h
            st = start if d == -1 else hi_i
            legs.append((-1, st, lo_i, sum(x.v for x in b[st:lo_i + 1]), sp, b[lo_i].l))
            d, start, hi_i = 1, lo_i, i
            flip = 1
        if not flip or len(legs) < 2 or b[i].m < 600 or b[i].m + 5 > 870:
            continue
        pb, th = legs[-1], legs[-2]          # pullback just completed, thrust before it
        if pb[0] == th[0]:
            continue
        thrust = abs(th[5] - th[4])
        pull = abs(pb[5] - pb[4])
        if thrust < 2.0 * s.atr[i] or pull > 0.62 * thrust or th[3] <= 0 or pb[3] > 0.6 * th[3]:
            continue
        if th[0] == 1 and pb[0] == -1 and not done[1] and b[i].c > s.vwap[i]:
            done[1] = True; yield i, 1
        elif th[0] == -1 and pb[0] == 1 and not done[-1] and b[i].c < s.vwap[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='weis_wave_pullback', name='Weis wave: low-volume pullback after a high-volume thrust', family='volume',
         detect=weis_wave,
         rules="Swing waves from a 1-ATR zigzag. After a thrust of at least 2 ATR, a counter-wave that retraces at most "
               "62% of it on at most 60% of its volume is complete once price turns back 1 ATR; that bar's close, on the "
               "thrust side of VWAP, signals continuation (long after an up-thrust, short after a down-thrust). 10:00 "
               "to 14:30 ET, one signal per side per session; tested with and against."),
]
