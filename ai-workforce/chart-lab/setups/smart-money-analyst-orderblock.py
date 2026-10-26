"""Order block: last opposite candle before a displacement, first retest.
Added 2026-09-27 by smart-money-analyst: order-flow family, next open line of
the research queue in ai-workforce/chart-lab/README.md.
"""


def order_block(s):
    """A displacement is a single 5-minute bar with range >= 1.5x the ATR at
    that bar that closes in the top/bottom third of its range (a strong,
    one-directional push). The order block is the last opposite-colored
    candle before that bar (last down-close candle before an up displacement,
    last up-close candle before a down displacement); its full high-low range
    is the zone. The first later bar that trades back into the zone and
    closes back out the far side (continuing the displacement's direction)
    confirms the block held; a close all the way through the zone's near-to-
    far side against the displacement cancels it."""
    b = s.bars
    zones = []      # (lo, hi, d): d=1 bullish block below price (support), -1 bearish above (resistance)
    fired = 0
    for i in range(1, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        rng = b[i].h - b[i].l
        atr = s.atr[i]
        alive, signal = [], None
        for lo, hi, d in zones:
            if d == 1:
                if b[i].c < lo:
                    continue                                   # traded through: cancel
                if signal is None and b[i].l <= hi and b[i].c > hi:
                    signal = 1; continue                        # retested and held: used
            else:
                if b[i].c > hi:
                    continue
                if signal is None and b[i].h >= lo and b[i].c < lo:
                    signal = -1; continue
            alive.append((lo, hi, d))
        zones = alive
        if signal is not None:
            fired += 1
            yield i, signal
        if atr and rng >= 1.5 * atr:
            if b[i].c > b[i].o and b[i].c >= b[i].l + 0.67 * rng and b[i - 1].c < b[i - 1].o:
                zones.append((b[i - 1].l, b[i - 1].h, 1))
            elif b[i].c < b[i].o and b[i].c <= b[i].l + 0.33 * rng and b[i - 1].c > b[i - 1].o:
                zones.append((b[i - 1].l, b[i - 1].h, -1))


SETUPS = [
    dict(id='order_block', name='Order block first retest', family='order flow', detect=order_block,
         rules="A displacement bar (range >= 1.5x ATR, closing in the outer third of its range) marks the last "
               "opposite-colored candle before it as an order block. The first bar that trades back into that "
               "candle's range and closes back out the displacement side confirms the block held, before 15:00. "
               "A close through the block against the displacement cancels it."),
]
