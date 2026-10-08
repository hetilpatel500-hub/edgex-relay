"""Composite setups: several auction/order-flow ideas that have to agree.
Added 2026-09-26 as the lab's first batch of new patterns."""
import core


def ib_ivb_acceptance(s):
    """IB breakout in the same direction as an earlier initial-volume
    breakout, with price already outside yesterday's value area."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    ivb_dir = None
    for i in range(6, len(b)):
        if b[i].m >= 840:
            return
        if ivb_dir is None:
            if b[i].c > s.ivb_hi: ivb_dir = 1
            elif b[i].c < s.ivb_lo: ivb_dir = -1
        if i < 12 or ivb_dir is None:
            continue
        if ivb_dir == 1 and b[i].c > s.ib_hi and b[i].c > p.vah:
            yield i, 1; return
        if ivb_dir == -1 and b[i].c < s.ib_lo and b[i].c < p.val:
            yield i, -1; return


def poc_migration(s):
    """By 11:30 the developing POC has moved outside yesterday's value area:
    value is migrating; lean the way it moved."""
    p = s.prior
    if p is None:
        return
    i = 23                          # the 11:25 bar closes at 11:30
    poc, _, _ = core.profile(s.bars[:i + 1])
    if poc > p.vah:
        yield i, 1
    elif poc < p.val:
        yield i, -1


def protected_at_vwap(s):
    """Pullback to a protected level that sits within 0.25 ATR of VWAP and
    holds (two levels agreeing)."""
    b = s.bars
    used = set()
    for i in range(12, len(b)):
        if not (600 <= b[i].m < 900):
            continue
        t, pr, a, w = s.trend[i], s.prot[i], s.atr[i], s.vwap[i]
        if pr is None or t == 0 or pr in used or abs(pr - w) > 0.25 * a:
            continue
        if t == 1 and b[i].l <= pr + 0.25 * a and b[i].c > pr and b[i].c > w:
            used.add(pr); yield i, 1
        elif t == -1 and b[i].h >= pr - 0.25 * a and b[i].c < pr and b[i].c < w:
            used.add(pr); yield i, -1


def sweep_then_vwap(s):
    """Liquidity sweep of yesterday's high/low or the IB extreme, then within
    30 minutes a close back across VWAP (the sweep trapped traders)."""
    p = s.prior
    b = s.bars
    sweep = None
    for i in range(3, len(b)):
        if b[i].m >= 900:
            return
        hi_lv = [x for x in (p.hi if p else None, s.ib_hi if i >= 12 else None) if x is not None]
        lo_lv = [x for x in (p.lo if p else None, s.ib_lo if i >= 12 else None) if x is not None]
        if any(b[i].h > x and b[i].c < x for x in hi_lv):
            sweep = (i, -1)
        elif any(b[i].l < x and b[i].c > x for x in lo_lv):
            sweep = (i, 1)
        if sweep and i - sweep[0] <= 6:
            j, d = sweep
            if (d == -1 and b[i].c < s.vwap[i] and b[i - 1].c >= s.vwap[i - 1]) or \
               (d == 1 and b[i].c > s.vwap[i] and b[i - 1].c <= s.vwap[i - 1]):
                yield i, d; return


SETUPS = [
    dict(id='ib_ivb_acceptance', name='IB + initial-volume breakout outside value', family='initial balance', detect=ib_ivb_acceptance,
         rules="IB breakout in the same direction as an earlier initial-volume breakout, with price already outside yesterday's value area."),
    dict(id='poc_migration', name='POC migration by 11:30', family='volume profile', detect=poc_migration,
         rules="At 11:30 the developing POC sits outside yesterday's value area; lean the way value moved."),
    dict(id='protected_at_vwap', name='Protected level at VWAP holds', family='structure', detect=protected_at_vwap,
         rules='Pullback to a protected level within 0.25 ATR of VWAP that closes back on the trend side of both.'),
    dict(id='sweep_then_vwap', name='Sweep, then VWAP cross', family='liquidity', detect=sweep_then_vwap,
         rules="Sweep of yesterday's high/low or the IB extreme, then within 30 minutes a close back across VWAP."),
]
