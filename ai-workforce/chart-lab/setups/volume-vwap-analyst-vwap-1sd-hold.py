"""VWAP +/-1 SD band acceptance and first pullback (trend continuation).
Added 2026-09-29 by volume-vwap-analyst: WebSearch idea (VWAP with standard
deviation bands: price that breaks beyond +1 SD and stays there shows
directional pressure; enter on the pullback that holds the band; sources
trendsandbreakouts.com/vwap-bands, tradingsim.com VWAP guide, tradezella.com
VWAP guide). The lab only tested the 2 SD snap-back (vwap_2sd_revert).
Parameters fixed before testing: two consecutive closes beyond 1 SD, then
the first bar whose low/high touches the band and closes back on the trend
side; 10:00-14:30; one signal per side per session.
"""


def vwap_1sd_hold(s):
    b = s.bars
    done = set()
    for i in range(3, len(b)):
        m = b[i].m
        if m < 600:
            continue
        if m >= 870:
            return
        sd = s.vsd[i]
        if not sd:
            continue
        for d in (1, -1):
            if d in done:
                continue
            band = lambda k: s.vwap[k] + d * s.vsd[k]
            accepted = any(all(d * (b[k].c - band(k)) > 0 for k in (j, j + 1)) for j in range(max(0, i - 12), i - 1))
            touch = (b[i].l <= band(i)) if d == 1 else (b[i].h >= band(i))
            held = d * (b[i].c - band(i)) > 0
            if accepted and touch and held:
                done.add(d)
                yield i, d


SETUPS = [
    dict(id='vwap_1sd_hold', name='VWAP 1 SD band first pullback holds', family='volume',
         detect=vwap_1sd_hold,
         rules="After two consecutive 5-minute closes beyond the +1 SD VWAP band (or below -1 SD) within the "
               "last hour, the first bar that touches the band and closes back on the trend side leans with "
               "the trend, 10:00-14:30, once per side per session."),
]
