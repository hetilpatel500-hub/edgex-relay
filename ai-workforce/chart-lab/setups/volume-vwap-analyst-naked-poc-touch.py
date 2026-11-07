"""Naked POC first touch, 5-minute bars.
Added 2026-10-13 by volume-vwap-analyst via WebSearch (LuxAlgo and TradingView script descriptions: a naked POC is a
prior session's point of control that no later session has traded through; traders treat it as a revisit level or
magnet, and the sources say the evidence is anecdotal, so this is a test, not an assumption).
Parameters fixed BEFORE any P&L was seen: look back up to 10 chained sessions; a prior POC is naked if the high-low
range of every session after it (up to yesterday) never contained it. Use the most recent naked POC that is at least
1 ATR(14, 5-min) from today's open. Signal: the first bar between 10:00 and 15:00 ET whose range reaches the level;
direction = direction of travel into the level (long if it was reached from below). One signal per session.
"""


def naked_poc_touch(s):
    b = s.bars
    p = s.prior
    chain = []
    while p is not None and len(chain) < 10:
        chain.append(p)
        p = p.prior
    level = None
    for k, ps in enumerate(chain):          # k = 0 is yesterday
        if all(not (q.lo <= ps.poc <= q.hi) for q in chain[:k]):
            if abs(ps.poc - s.open) >= s.atr[0]:
                level = ps.poc
                break
    if level is None:
        return
    for i in range(1, len(b) - 1):
        if b[i].m < 600 or b[i].m > 900:
            continue
        if b[i].l <= level <= b[i].h:
            yield i, (1 if level > s.open else -1)
            return


SETUPS = [
    dict(id='naked_poc_touch', name='Naked POC first touch', family='volume profile',
         detect=naked_poc_touch,
         rules="A prior session's point of control that no later session has traded through is a naked POC. When "
               "today's price first reaches the most recent one (at least one ATR from the open) between 10:00 and "
               "15:00, the setup leans in the direction of travel into it; tested with and against (fade). One "
               "signal per session."),
]
