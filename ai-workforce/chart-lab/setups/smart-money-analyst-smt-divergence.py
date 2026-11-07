"""SMT divergence between correlated index ETFs at a session extreme.
Added 2026-10-13 by smart-money-analyst via WebSearch (ICT "smart money technique" descriptions: when correlated
indices fail to confirm each other at a new high or low, the one that made the new extreme has swept liquidity and
the move is read as exhausted; the sources are anecdotal, so this is a test, not an assumption).
Parameters fixed BEFORE any P&L was seen: pairs SPY-QQQ and IWM-DIA only (other symbols skipped). Look at bars
12-66 (10:30-15:00 ET). The signal is a bar whose high exceeds every earlier high of the session (the previous
session high was set at least 6 bars earlier), while the partner's high on the same bar does NOT exceed the
partner's own earlier session high; the mirror for lows. The signal is on the symbol that made the new extreme,
direction = the way it broke (long for a new high); the lab tests it with and against (fade). One signal per
session per symbol.
"""
import core

PAIR = {'SPY': 'QQQ', 'QQQ': 'SPY', 'IWM': 'DIA', 'DIA': 'IWM'}
_days = {}


def _partner(sym, day):
    if sym not in _days:
        _days[sym] = {x.day: x for x in core.sessions(sym)}
    return _days[sym].get(day)


def smt_divergence(s):
    if s.sym not in PAIR:
        return
    p = _partner(PAIR[s.sym], s.day)
    if p is None:
        return
    b, pb = s.bars, p.bars
    n = min(len(b), len(pb), 67)
    for i in range(12, n - 1):
        hi_prev = max(x.h for x in b[:i])
        lo_prev = min(x.l for x in b[:i])
        phi_prev = max(x.h for x in pb[:i])
        plo_prev = min(x.l for x in pb[:i])
        hi_age = i - max(range(i), key=lambda j: b[j].h)
        lo_age = i - min(range(i), key=lambda j: b[j].l)
        if b[i].h > hi_prev and hi_age >= 6 and pb[i].h <= phi_prev:
            yield i, 1
            return
        if b[i].l < lo_prev and lo_age >= 6 and pb[i].l >= plo_prev:
            yield i, -1
            return


SETUPS = [
    dict(id='smt_divergence', name='SMT divergence at a session extreme', family='smart-money',
         detect=smt_divergence,
         rules="Between 10:30 and 15:00, SPY or QQQ (or IWM or DIA) prints a new session high (or low) that "
               "is at least 6 bars past the previous one while its partner index fails to make a new high (or "
               "low) on the same bar. The signal is on the symbol that made the new extreme, in the direction "
               "it broke; tested with and against (fade). One signal per session per symbol."),
]
