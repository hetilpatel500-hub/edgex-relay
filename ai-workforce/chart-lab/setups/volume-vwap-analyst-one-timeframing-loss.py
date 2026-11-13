"""One-timeframing loss (Dalton auction theory).
Added 2026-10-03 by volume-vwap-analyst: the queue's testable lines are all coded,
so this run used a documented market-profile idea not yet in the lab: "one-time
framing" (each bar makes a higher low, or each a lower high) shows one side in
control; the first bar that trades back through the prior bar's far end signals
that control has been lost. Distinct from bos/choch (swing pivots) and
key_reversal (session extreme).
"""

N = 6   # consecutive one-time-framing bars required


def otf_loss(s):
    """After N consecutive bars that each make a higher high and a higher low
    (one-timeframing up), the first bar that closes below the prior bar's low
    leans short; N bars each with a lower high and lower low, then a close above
    the prior bar's high, leans long. After 10:00, before 15:00, at most 2 per session."""
    b = s.bars
    up = dn = 0
    fired = 0
    for i in range(1, len(b)):
        if b[i].m >= 900 or fired >= 2:
            return
        d = None
        if up >= N and b[i].c < b[i - 1].l:
            d = -1
        elif dn >= N and b[i].c > b[i - 1].h:
            d = 1
        up = up + 1 if (b[i].h > b[i - 1].h and b[i].l > b[i - 1].l) else 0
        dn = dn + 1 if (b[i].h < b[i - 1].h and b[i].l < b[i - 1].l) else 0
        if d and b[i].m >= 600:
            fired += 1
            yield i, d


SETUPS = [
    dict(id='otf_loss', name='One-timeframing loss of control', family='volume', detect=otf_loss,
         rules="After six straight bars that each make a higher high and higher low (or lower high and lower "
               "low), the first bar closing through the prior bar's far end shows the controlling side has "
               "stopped; lean against the old run. After 10:00, before 15:00, at most two per session."),
]
