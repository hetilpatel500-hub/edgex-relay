"""Chande VIDYA (CMO 9, EMA 12) break away from a flattened line, with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (VIDYA: Chande 1996, VIDYA = P*F*|CMO| + prev*(1-F*|CMO|),
F = 2/(N+1); MetaTrader 5 defaults CMO 9, EMA 12; LuxAlgo reads price breaking away from a flattened VIDYA as the possible start
of a directional phase; no source gives explicit entry rules, so these are the lab's own).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: CMO 9, EMA 12, seeded with the session's first close (built
inside the session, needs 10 bars); flat = the line moved less than 0.05 ATR over the prior 3 bars; signal when the close
crosses the line right after a flat stretch and sits on the same side of VWAP, 10:30 to 14:30 ET, at most 2 signals per
side per session.
"""


def vidya_flat_break(s):
    b = s.bars
    n_cmo, f = 9, 2 / 13
    v = [b[0].c]
    for i in range(1, len(b)):
        if i < n_cmo:
            v.append(b[i].c)
            continue
        ups = sum(max(b[k].c - b[k - 1].c, 0) for k in range(i - n_cmo + 1, i + 1))
        dns = sum(max(b[k - 1].c - b[k].c, 0) for k in range(i - n_cmo + 1, i + 1))
        k_ = f * abs((ups - dns) / (ups + dns)) if ups + dns else 0
        v.append(b[i].c * k_ + v[-1] * (1 - k_))
    cnt = {1: 0, -1: 0}
    for i in range(n_cmo + 4, len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        if abs(v[i - 1] - v[i - 4]) >= 0.05 * s.atr[i]:
            continue
        up = b[i].c > v[i] and b[i - 1].c <= v[i - 1]
        dn = b[i].c < v[i] and b[i - 1].c >= v[i - 1]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='vidya_flat_break', name='VIDYA (9/12) break away from a flat line with VWAP', family='trend',
         detect=vidya_flat_break,
         rules="Chande's VIDYA (CMO 9, EMA 12): when the line has gone flat (moved under 0.05 ATR over the last 3 bars), "
               "a 5-minute close crossing above it with the close above VWAP leans long; crossing below with the close "
               "below VWAP leans short. 10:30 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
