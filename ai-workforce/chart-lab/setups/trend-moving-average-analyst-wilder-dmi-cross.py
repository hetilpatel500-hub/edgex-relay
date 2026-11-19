"""Wilder Directional Movement (+DI / -DI) cross gated by ADX >= 25 and rising, with VWAP agreement, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Wilder's DMI: +DI/-DI crossover gives direction, ADX
above 25 marks a trend, per the Capital.com and Tradejini write-ups; the sources disagree on whether ADX must be above
25 at the cross itself, this version requires it at the cross; Wilder's next-day extreme-point rule is not used, it has
no intraday equivalent in the sources).
Parameters fixed BEFORE any P&L was seen: Wilder smoothing, length 14, built inside the session from its first bar;
ADX = Wilder-smoothed DX of length 14. Long at the close of the first bar between 11:45 and 14:30 ET where +DI crosses
above -DI, ADX >= 25 and ADX is above its prior bar, and the close is above session VWAP (mirror for short). At most one
signal per side per session.
"""


def wilder_dmi_cross(s):
    b = s.bars
    n = 14
    N = len(b)
    pdm, mdm, tr = [0.0], [0.0], [b[0].h - b[0].l]
    for i in range(1, N):
        up, dn = b[i].h - b[i - 1].h, b[i - 1].l - b[i].l
        pdm.append(up if up > dn and up > 0 else 0.0)
        mdm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c)))
    if N < 2 * n + 2:
        return
    sp, sm, st = sum(pdm[1:n + 1]), sum(mdm[1:n + 1]), sum(tr[1:n + 1])
    pdi, mdi, dx = [None] * N, [None] * N, [None] * N
    for i in range(n, N):
        if i > n:
            sp = sp - sp / n + pdm[i]
            sm = sm - sm / n + mdm[i]
            st = st - st / n + tr[i]
        if st > 0:
            pdi[i], mdi[i] = 100 * sp / st, 100 * sm / st
            t = pdi[i] + mdi[i]
            dx[i] = 100 * abs(pdi[i] - mdi[i]) / t if t > 0 else 0.0
    adx = [None] * N
    first = 2 * n - 1
    if any(v is None for v in dx[n:first + 1]):
        return
    adx[first] = sum(dx[n:first + 1]) / n
    for i in range(first + 1, N):
        adx[i] = (adx[i - 1] * (n - 1) + (dx[i] if dx[i] is not None else adx[i - 1])) / n
    cnt = {1: 0, -1: 0}
    for i in range(first + 1, N - 1):
        if b[i].m < 705 or b[i].m > 870 or pdi[i - 1] is None:
            continue
        if adx[i] < 25 or adx[i] <= adx[i - 1]:
            continue
        if pdi[i] > mdi[i] and pdi[i - 1] <= mdi[i - 1] and b[i].c > s.vwap[i] and cnt[1] < 1:
            cnt[1] += 1
            yield i, 1
        elif mdi[i] > pdi[i] and mdi[i - 1] <= pdi[i - 1] and b[i].c < s.vwap[i] and cnt[-1] < 1:
            cnt[-1] += 1
            yield i, -1


SETUPS = [
    dict(id='wilder_dmi_adx_cross', name='Wilder DMI cross gated by ADX >= 25 and rising, with VWAP', family='trend',
         detect=wilder_dmi_cross,
         rules="Wilder's directional movement on 14 five-minute bars: between 11:45 and 14:30 ET, when +DI crosses "
               "above -DI while ADX is at least 25 and rising and price closes above VWAP, it leans long; the "
               "mirror (-DI over +DI, price under VWAP) leans short. One signal per side per session; tested "
               "with and against."),
]
