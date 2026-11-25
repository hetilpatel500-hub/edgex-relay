"""Fair value gap (3-bar imbalance) first retest.
Added 2026-09-26 by smart-money-analyst: order-flow family, next open line of
the research queue in ai-workforce/chart-lab/README.md.
"""


def fvg_retest(s):
    """A fair value gap is a 3-bar imbalance: bar1's high sits below bar3's
    low (bullish, an untraded range that should act as support) or bar1's low
    sits above bar3's high (bearish, resistance). The first later bar that
    trades back into an open gap and closes back through its near edge
    confirms the gap held; lean with the gap's original direction. A close
    all the way through the gap's far edge fills it and cancels the zone."""
    b = s.bars
    zones = []      # (bot, top, d): d=1 bullish gap below price (support), -1 bearish above (resistance)
    fired = 0
    for i in range(len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        alive, signal = [], None
        for bot, top, d in zones:
            if d == 1:
                if b[i].c < bot:
                    continue                                    # gap filled: drop it
                if signal is None and b[i].l <= top and b[i].c > top:
                    signal = 1; continue                         # retested and held: used
            else:
                if b[i].c > top:
                    continue
                if signal is None and b[i].h >= bot and b[i].c < bot:
                    signal = -1; continue
            alive.append((bot, top, d))
        zones = alive
        if signal is not None:
            fired += 1
            yield i, signal
        if i >= 2:
            if b[i - 2].h < b[i].l:
                zones.append((b[i - 2].h, b[i].l, 1))
            elif b[i - 2].l > b[i].h:
                zones.append((b[i].h, b[i - 2].l, -1))


SETUPS = [
    dict(id='fvg_retest', name='Fair value gap first retest', family='order flow', detect=fvg_retest,
         rules="3-bar imbalance (bar1 high < bar3 low, or bar1 low > bar3 high) leaves an unfilled gap; "
               "the first bar that trades back into it and closes back through the near edge confirms the "
               "gap held as support/resistance, before 15:00. A close through the far edge fills and cancels it."),
]
