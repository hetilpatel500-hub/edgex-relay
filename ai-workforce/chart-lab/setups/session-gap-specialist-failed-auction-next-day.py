"""Failed auction, next-day reaction (Ray Barros' failed auction as described by LuxAlgo / MarketCalls / NexusFi pages).
Added 2026-10-07 by session-gap-specialist via the lab queue, from a WebSearch run. Sources are educational pages with
anecdotal numbers, not tested rules. Distinct from ib_break_fail (same-day) and ib_sweep: this reads YESTERDAY's failure.
Parameters fixed BEFORE any P&L was seen. Yesterday's initial balance is its first 12 bars. A failed upside auction:
a bar after the IB closes above the IB high, then within the next 6 bars a bar closes back at or below the IB high,
and yesterday's close is below the IB high. Mirror for the downside. If both sides failed yesterday, skip. Today, at
the first bar closing at or after 10:00 ET (and before 11:00), signal AGAINST the failed side (short after a failed
upside auction, long after a failed downside one) if today's open is inside yesterday's [low, high]. One signal per
session.
"""


def _failed(p):
    b = p.bars
    if len(b) < 24:
        return 0
    H, L = p.ib_hi, p.ib_lo
    up = dn = False
    for i in range(12, len(b) - 1):
        if not up and b[i].c > H:
            if any(x.c <= H for x in b[i + 1:i + 7]) and p.close < H:
                up = True
        if not dn and b[i].c < L:
            if any(x.c >= L for x in b[i + 1:i + 7]) and p.close > L:
                dn = True
    if up == dn:
        return 0
    return -1 if up else 1


def failed_auction_next_day(s):
    p = s.prior
    if p is None or not (p.lo < s.open < p.hi):
        return
    d = _failed(p)
    if not d:
        return
    for i, x in enumerate(s.bars):
        if 600 <= x.m < 660:
            yield i, d
            return


SETUPS = [
    dict(id='failed_auction_next_day', name="Yesterday's failed IB auction: next-day reaction", family='session',
         detect=failed_auction_next_day,
         rules="If yesterday broke its initial balance, closed back inside it within 30 minutes and finished the day "
               "inside it, the failed side is treated as unfinished business and today's first read at 10:00 ET "
               "leans the other way (short after a failed upside break, long after a failed downside break), when "
               "today opens inside yesterday's range. One signal per session; tested with and against."),
]
