"""Breaker block: an order block that failed, retested from the other side.
Added 2026-10-15 by smart-money-analyst: new idea from outside the queue (ICT breaker block).
The lab tests the order block's first retest (order_block_retest) but not the flipped zone after the block fails.
Rules fixed BEFORE any P&L was seen.
"""


def breaker_block_retest(s):
    """Displacement and order block exactly as in order_block_retest (body at least 1.2 ATR, close in the extreme 25%
    of the range, block = last opposite-colour bar within 5 bars before it). The block fails when a bar within 15 bars
    after the displacement closes through the block's far side (below a bullish block's body, above a bearish one's).
    The failed block flips: a bullish block becomes resistance, a bearish one support. Within 15 bars after the
    failure, the first bar that trades back into the block's body (high >= body bottom for a flipped bullish block,
    low <= body top for a flipped bearish one) without closing through the body's far side and closes in the new
    direction (red for resistance, green for support) is the signal, judged at its close. A close through the far
    side voids it. Before 15:00 ET, at most 3 per session."""
    b = s.bars
    fired = 0
    for i in range(2, len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        atr = s.atr[i]
        if not atr:
            continue
        rng = b[i].h - b[i].l
        body = b[i].c - b[i].o
        if rng <= 0 or abs(body) < 1.2 * atr:
            continue
        d = 1 if body > 0 else -1
        if d == 1 and b[i].c < b[i].h - 0.25 * rng:
            continue
        if d == -1 and b[i].c > b[i].l + 0.25 * rng:
            continue
        k = None
        for q in range(i - 1, max(i - 6, -1), -1):
            if (b[q].c < b[q].o) if d == 1 else (b[q].c > b[q].o):
                k = q
                break
        if k is None:
            continue
        top, bot = max(b[k].o, b[k].c), min(b[k].o, b[k].c)
        f = None
        for j in range(i + 1, min(i + 16, len(b))):
            if d == 1 and b[j].c < bot or d == -1 and b[j].c > top:
                f = j
                break
        if f is None:
            continue
        for j in range(f + 1, min(f + 16, len(b))):
            if b[j].m >= 900:
                break
            if d == 1:       # flipped to resistance
                if b[j].c > top:
                    break
                if b[j].h >= bot:
                    if b[j].c < b[j].o:
                        fired += 1; yield j, -1
                    break
            else:            # flipped to support
                if b[j].c < bot:
                    break
                if b[j].l <= top:
                    if b[j].c > b[j].o:
                        fired += 1; yield j, 1
                    break


SETUPS = [
    dict(id='breaker_block_retest', name='Breaker block first retest', family='smart-money',
         detect=breaker_block_retest,
         rules="A big displacement bar (body 1.2 ATR or more, closing in its extreme quarter) leaves an order block, the "
               "last opposite-colour bar before it. If a later bar closes through the far side of that block within 15 "
               "bars, the block has failed and flips (a failed bullish block becomes resistance, a failed bearish "
               "block support). The first bar within 15 more bars that trades back into the block's body, does not "
               "close through its far side, and closes in the flipped direction is the signal. Before 15:00 ET, up to "
               "3 per session; tested with and against."),
]
