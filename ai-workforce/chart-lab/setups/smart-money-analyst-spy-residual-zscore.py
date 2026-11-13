"""Beta-adjusted residual versus SPY, z-score stretch.
Added 2026-10-15 by smart-money-analyst (WebSearch 2026-10-15: stock-vs-index residual spreads modelled as
mean-reverting with a rolling hedge ratio and a z-scored residual, per the intraday pairs / residual
literature; nobody published out-of-sample numbers for single names against SPY, so it is tested here).
Parameters fixed BEFORE any P&L was seen:
  beta   least-squares slope of the stock's 5-minute returns on SPY's, over the previous 20 sessions
         (only sessions already closed, so no lookahead); at least 10 prior sessions needed.
  resid  stock return from today's open minus beta times SPY's return from today's open, at each bar close.
  sigma  standard deviation of that residual over all bars of the previous 20 sessions (same beta).
  z      resid / sigma. Signal at the close of a bar between 10:30 and 14:30 ET when |z| >= 2.5,
         once per side per session. Direction of the signal = the stretch (up for z > 0); the lab tests
         it with and against ("fade" is the mean-reversion reading). SPY itself is skipped.
"""
import math
import core

_spy = {}
_cache = {}


def _spy_day(day):
    if not _spy:
        for x in core.sessions('SPY'):
            _spy[x.day] = x
    return _spy


def _rets(b):
    return [b[k].c / b[k - 1].c - 1 for k in range(1, len(b))]


def _stats(sym, sessions):
    """Per session: (beta, sigma) from the 20 sessions before it."""
    spy = _spy_day(None)
    out = {}
    hist = []   # (stock bars, spy bars)
    for s in sessions:
        p = spy.get(s.day)
        if p is not None and len(p.bars) == len(s.bars):
            if len(hist) >= 10:
                h = hist[-20:]
                sx = sy = sxx = sxy = n = 0
                for sb, pb in h:
                    for a, c in zip(_rets(sb), _rets(pb)):
                        sx += c; sy += a; sxx += c * c; sxy += c * a; n += 1
                den = n * sxx - sx * sx
                beta = (n * sxy - sx * sy) / den if den else None
                if beta is not None:
                    res = []
                    for sb, pb in h:
                        for k in range(1, len(sb)):
                            res.append((sb[k].c / sb[0].o - 1) - beta * (pb[k].c / pb[0].o - 1))
                    m = sum(res) / len(res)
                    sd = math.sqrt(sum((r - m) ** 2 for r in res) / len(res))
                    out[s.day] = (beta, sd)
            hist.append((s.bars, p.bars))
    return out


def spy_residual_z(s):
    if s.sym == 'SPY':
        return
    key = s.sym
    if key not in _cache:
        _cache[key] = _stats(s.sym, core.sessions(s.sym))
    st = _cache[key].get(s.day)
    p = _spy_day(None).get(s.day)
    if st is None or p is None or len(p.bars) != len(s.bars) or not st[1]:
        return
    beta, sd = st
    b = s.bars
    fired = set()
    for i in range(12, len(b) - 1):
        if not (630 <= b[i].m <= 870):
            continue
        r = (b[i].c / b[0].o - 1) - beta * (p.bars[i].c / p.bars[0].o - 1)
        z = r / sd
        d = 1 if z >= 2.5 else -1 if z <= -2.5 else 0
        if d and d not in fired:
            fired.add(d)
            yield i, d


SETUPS = [
    dict(id='spy_residual_z', name='Beta-adjusted residual vs SPY, z-score stretch', family='smart-money',
         detect=spy_residual_z,
         rules="Take the stock's move from the open minus its beta (last 20 sessions, 5-minute returns) times "
               "SPY's move from the open. Divide by the standard deviation of that residual over the same 20 "
               "sessions. Between 10:30 and 14:30, when the z-score reaches +/-2.5 at a bar close, the signal "
               "points the way of the stretch; once per side per session. SPY is skipped. The lab tests it "
               "with the stretch and against it (mean reversion of the spread)."),
]
