"""VWAP 2-sigma stretch in a low-efficiency (choppy) tape, snap-back reading.
Added 2026-10-15 by volume-vwap-analyst: new idea (WebSearch 2026-10-15 on VWAP deviation bands used as range-day
fades). The lab already tests the plain VWAP 2-sigma snap-back; the new piece is the regime gate, Kaufman's
Efficiency Ratio, so the stretch is only read as a fade when the tape has been going nowhere.
Every number below was fixed before any P&L was seen; everything is known at the signal bar's close.
"""


def er_vwap_2sd(s):
    b = s.bars
    done = {1: False, -1: False}
    n = 20
    for i in range(n, len(b)):
        if b[i].m < 660 or b[i].m + 5 > 870:
            continue
        sd = s.vsd[i]
        if sd <= 0:
            continue
        net = abs(b[i].c - b[i - n].c)
        path = sum(abs(b[k].c - b[k - 1].c) for k in range(i - n + 1, i + 1))
        if path <= 0 or net / path >= 0.25:
            continue
        # snap-back direction: long when the close is 2 sigma below VWAP, short when 2 sigma above
        if not done[1] and b[i].c <= s.vwap[i] - 2 * sd:
            done[1] = True; yield i, 1
        elif not done[-1] and b[i].c >= s.vwap[i] + 2 * sd:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='er_vwap_2sd', name='VWAP 2-sigma stretch in a choppy tape (efficiency-ratio gated)', family='volume',
         detect=er_vwap_2sd,
         rules="Between 11:00 and 14:30 ET, when Kaufman's Efficiency Ratio over the last 20 closes (net move divided "
               "by the sum of bar-to-bar moves) is below 0.25, a bar that closes 2 or more VWAP standard deviations "
               "below VWAP signals a long back toward VWAP, and 2 or more above signals a short. One signal per side "
               "per session. Tested with and against; the stretch is only read when the tape has been going nowhere."),
]
