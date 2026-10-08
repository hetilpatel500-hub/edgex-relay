"""EMA 9/21 crossover (golden cross / death cross) on 5-minute bars.
Added 2026-09-28 by trend-moving-average-analyst: research queue in
ai-workforce/chart-lab/README.md is exhausted for non-tape lines (every
other line already has a coded, backtested setup, confirmed against
PLAYBOOK.md and setups/ -- README.md's checkboxes were simply never ticked
after that work), and the "waiting for tape" order-flow lines stay blocked
(tape/ holds 0 sessions). This run used WebSearch for a documented,
untested technique in trend-moving-average-analyst's own family: the EMA
9/21 crossover, distinct from ema9_20_pullback already tested (which fires
on a pullback TO EMA9 inside an established trend). This setup instead
fires on the CROSS ITSELF. Per
https://stockpathshala.com/ema-crossover-for-intraday/ and
https://tradersagency.com/blog/moving-average-crossover-strategy-golden-cross-death-cross,
a "golden cross" is the faster EMA crossing above the slower one (bullish),
a "death cross" the mirror (bearish); the 9/21 pair is the commonly cited
intraday combination.
"""


def _ema(closes, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in closes:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def ema9_21_crossover(s):
    """EMA9 and EMA21 of 5-minute closes. The first bar where EMA9 closes
    from at-or-below to above EMA21 (golden cross) leans long; the mirror
    cross (death cross) leans short. One signal per side per session,
    before 15:00, after a 21-bar warmup."""
    b = s.bars
    closes = [x.c for x in b]
    e9, e21 = _ema(closes, 9), _ema(closes, 21)
    fired_long = fired_short = False
    for i in range(21, len(b)):
        if b[i].m >= 900:
            break
        if not fired_long and e9[i - 1] <= e21[i - 1] and e9[i] > e21[i]:
            fired_long = True
            yield i, 1
        if not fired_short and e9[i - 1] >= e21[i - 1] and e9[i] < e21[i]:
            fired_short = True
            yield i, -1


SETUPS = [
    dict(id='ema9_21_crossover', name='EMA 9/21 crossover (golden/death cross)', family='trend',
         detect=ema9_21_crossover,
         rules="EMA9 crossing above EMA21 (golden cross) leans long; EMA9 crossing below EMA21 (death "
               "cross) leans short. One signal per side per session, before 15:00, after a 21-bar warmup."),
]
