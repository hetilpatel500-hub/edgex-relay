"""ADX-gated VWAP 2-sigma stretch fade.
Added 2026-10-01 by volatility-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (crosstrade.io VWAP reversion, edgeful.com
mean reversion) for a documented, untested idea: fade a VWAP stretch only when
a trend-strength regime filter (ADX(14) on 5-minute bars below 20) says the
market is not trending. Distinct from vwap_snapback, which has no regime gate.
"""


def _adx(b, n=14):
    """Wilder ADX per bar (None until enough bars), computed within the session."""
    out = [None] * len(b)
    tr_s = pdm_s = ndm_s = 0.0
    dx = []
    for i in range(1, len(b)):
        up, dn = b[i].h - b[i - 1].h, b[i - 1].l - b[i].l
        pdm = up if up > dn and up > 0 else 0.0
        ndm = dn if dn > up and dn > 0 else 0.0
        tr = max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c))
        if i <= n:
            tr_s += tr; pdm_s += pdm; ndm_s += ndm
        else:
            tr_s = tr_s - tr_s / n + tr
            pdm_s = pdm_s - pdm_s / n + pdm
            ndm_s = ndm_s - ndm_s / n + ndm
        if i >= n and tr_s > 0:
            pdi, ndi = 100 * pdm_s / tr_s, 100 * ndm_s / tr_s
            dx.append(100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi else 0.0)
            if len(dx) == n:
                out[i] = sum(dx) / n
            elif len(dx) > n:
                out[i] = (out[i - 1] * (n - 1) + dx[-1]) / n
    return out


def adx_vwap_fade(s):
    """With ADX(14) of the session's 5-minute bars below 20, the first bar whose
    close is beyond VWAP +/- 2 standard deviations (bands from 10:30 on) fades
    back toward VWAP. One signal per side per session, until 14:30."""
    b = s.bars
    adx = _adx(b)
    fired = set()
    for i in range(len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        if adx[i] is None or adx[i] >= 20 or not s.vsd[i]:
            continue
        up = s.vwap[i] + 2 * s.vsd[i]
        dn = s.vwap[i] - 2 * s.vsd[i]
        if b[i].c > up and -1 not in fired:
            fired.add(-1); yield i, -1
        elif b[i].c < dn and 1 not in fired:
            fired.add(1); yield i, 1


SETUPS = [
    dict(id='adx_vwap_fade', name='ADX-gated VWAP 2-sigma stretch fade', family='volatility', detect=adx_vwap_fade,
         rules="Only when ADX(14) on the session's 5-minute bars is below 20 (no trend): the first 5-minute close "
               "beyond VWAP +2 SD leans short, below VWAP -2 SD leans long, back toward VWAP. From 10:30 to 14:30 ET, "
               "one signal per side per session."),
]
