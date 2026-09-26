"""Seed intraday setups (5-minute bars, regular session).

Each setup's detect(s) yields (i, d): the signal is known at the close of bar i,
d is +1 (long bias) or -1 (short bias). The lab enters at the open of bar i+1.
Minutes are ET minutes after midnight (600 = 10:00, 840 = 14:00).
"""


def first(gen):
    for x in gen:
        yield x
        return


def orb15(s):
    b = s.bars
    for i in range(3, len(b)):
        if b[i].m >= 630:
            return
        if b[i].c > s.or_hi:
            yield i, 1; return
        if b[i].c < s.or_lo:
            yield i, -1; return


def ib_break(s):
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if b[i].c > s.ib_hi:
            yield i, 1; return
        if b[i].c < s.ib_lo:
            yield i, -1; return


def ib_break_fail(s):
    """IB breaks, then closes back inside the IB within 6 bars: fade it."""
    b = s.bars
    brk = None
    for i in range(12, len(b)):
        if b[i].m >= 870:
            return
        if brk is None:
            if b[i].c > s.ib_hi: brk = (i, 1)
            elif b[i].c < s.ib_lo: brk = (i, -1)
            continue
        j, d = brk
        if i - j > 6:
            return
        if (d == 1 and b[i].c < s.ib_hi) or (d == -1 and b[i].c > s.ib_lo):
            yield i, -d; return


def ivb_break(s):
    """Initial volume breakout: close beyond the high or low of the heaviest
    bar of the first 30 minutes, on 1.5x normal volume for that time of day."""
    b = s.bars
    for i in range(6, len(b)):
        if b[i].m >= 720:
            return
        r = s.rvol[i] or 0
        if b[i].c > s.ivb_hi and r >= 1.5:
            yield i, 1; return
        if b[i].c < s.ivb_lo and r >= 1.5:
            yield i, -1; return


def va_reentry(s):
    """80% rule, 5-minute version: open outside yesterday's value area, then 6
    straight closes back inside it -> lean toward the far side of the value area."""
    p = s.prior
    if p is None:
        return
    if p.val <= s.open <= p.vah:
        return
    d = 1 if s.open < p.val else -1
    run = 0
    b = s.bars
    for i in range(len(b)):
        if b[i].m >= 840:
            return
        run = run + 1 if p.val <= b[i].c <= p.vah else 0
        if run == 6:
            yield i, d; return


def poc_magnet(s):
    """Open inside yesterday's value area but away from its POC, first 30
    minutes move away from the POC fails (close back past the open) -> lean
    toward yesterday's POC."""
    p = s.prior
    if p is None or not (p.val <= s.open <= p.vah):
        return
    if abs(s.open - p.poc) < s.atr[0]:
        return
    d = 1 if s.open < p.poc else -1
    b = s.bars
    i = 5
    if (b[i].c - s.open) * d > 0:
        yield i, d


def vwap_reclaim(s):
    b = s.bars
    below = above = 0
    fired = 0
    for i in range(len(b)):
        c, w = b[i].c, s.vwap[i]
        if 600 <= b[i].m < 900 and fired < 2:
            r = s.rvol[i] or 0
            if below >= 6 and c > w and r >= 1.2:
                yield i, 1; fired += 1
            elif above >= 6 and c < w and r >= 1.2:
                yield i, -1; fired += 1
        below = below + 1 if c < w else 0
        above = above + 1 if c > w else 0


def vwap_2sd_revert(s):
    b = s.bars
    fired = 0
    for i in range(1, len(b)):
        if not (600 <= b[i].m < 900) or fired >= 2:
            continue
        up, dn = s.vwap[i - 1] + 2 * s.vsd[i - 1], s.vwap[i - 1] - 2 * s.vsd[i - 1]
        if b[i - 1].c > up and b[i].c < s.vwap[i] + 2 * s.vsd[i]:
            yield i, -1; fired += 1
        elif b[i - 1].c < dn and b[i].c > s.vwap[i] - 2 * s.vsd[i]:
            yield i, 1; fired += 1


def pd_sweep(s):
    """Liquidity sweep of yesterday's high or low: wick through, close back."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    hi_done = lo_done = False
    for i in range(3, len(b)):
        if b[i].m >= 900:
            return
        if not hi_done and b[i].h > p.hi and b[i].c < p.hi and b[i].o < p.hi:
            hi_done = True; yield i, -1
        if not lo_done and b[i].l < p.lo and b[i].c > p.lo and b[i].o > p.lo:
            lo_done = True; yield i, 1


def ib_sweep(s):
    """Sweep of the initial balance extreme that closes back inside."""
    b = s.bars
    hi_done = lo_done = False
    for i in range(12, len(b)):
        if b[i].m >= 900:
            return
        if not hi_done and b[i].h > s.ib_hi and b[i].c < s.ib_hi:
            hi_done = True; yield i, -1
        if not lo_done and b[i].l < s.ib_lo and b[i].c > s.ib_lo:
            lo_done = True; yield i, 1


def choch(s):
    """Change of character: the protected level of the trend breaks."""
    for i, ev in enumerate(s.event):
        if not (600 <= s.bars[i].m < 900):
            continue
        if ev == 'choch_up':
            yield i, 1
        elif ev == 'choch_dn':
            yield i, -1


def bos(s):
    """Break of structure in the trend's direction (continuation)."""
    n = 0
    for i, ev in enumerate(s.event):
        if not (600 <= s.bars[i].m < 900) or n >= 3:
            continue
        if ev == 'bos_up' and s.trend[i - 1] == 1:
            n += 1; yield i, 1
        elif ev == 'bos_dn' and s.trend[i - 1] == -1:
            n += 1; yield i, -1


def protected_hold(s):
    """Pullback that tests the protected level and holds (rejection bar)."""
    b = s.bars
    used = set()
    for i in range(1, len(b)):
        if not (600 <= b[i].m < 900):
            continue
        t, p = s.trend[i], s.prot[i]
        if p is None or t == 0 or p in used:
            continue
        a = s.atr[i]
        if t == 1 and b[i].l <= p + 0.25 * a and b[i].c > p and b[i].c > b[i].o:
            used.add(p); yield i, 1
        elif t == -1 and b[i].h >= p - 0.25 * a and b[i].c < p and b[i].c < b[i].o:
            used.add(p); yield i, -1


def gap_fill(s):
    p = s.prior
    if p is None:
        return
    g = s.open / p.close - 1
    if abs(g) < 0.0025:
        return
    d = -1 if g > 0 else 1        # toward yesterday's close
    i = 5
    if (s.bars[i].c - s.open) * d > 0:
        yield i, d


def power_hour(s):
    b = s.bars
    for i in range(len(b)):
        if b[i].m == 895:     # the 14:55 bar closes at 15:00
            if b[i].c > s.vwap[i] and b[i].c > s.ib_hi:
                yield i, 1
            elif b[i].c < s.vwap[i] and b[i].c < s.ib_lo:
                yield i, -1
            return


def va_edge_rejection(s):
    """Test of yesterday's value-area edge from inside, rejected."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    n = 0
    for i in range(1, len(b)):
        if not (600 <= b[i].m < 900) or n >= 2:
            continue
        if b[i].h >= p.vah and b[i].c < p.vah and b[i - 1].c < p.vah and b[i].c < b[i].o:
            n += 1; yield i, -1
        elif b[i].l <= p.val and b[i].c > p.val and b[i - 1].c > p.val and b[i].c > b[i].o:
            n += 1; yield i, 1


def outside_va_acceptance(s):
    """Price leaves yesterday's value area and holds outside for 6 bars
    (acceptance) -> continuation away from value."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    up = dn = 0
    for i in range(len(b)):
        if b[i].m >= 840:
            return
        up = up + 1 if b[i].c > p.vah else 0
        dn = dn + 1 if b[i].c < p.val else 0
        if b[i].m >= 600 and up == 6:
            yield i, 1; return
        if b[i].m >= 600 and dn == 6:
            yield i, -1; return


SETUPS = [
    dict(id='orb15', name='15-minute opening range breakout', family='opening range', detect=orb15,
         rules='First 5-minute close beyond the 9:30-9:45 range, before 10:30.'),
    dict(id='ib_break', name='Initial balance breakout', family='initial balance', detect=ib_break,
         rules='First 5-minute close beyond the first-hour (9:30-10:30) high or low, before 14:00.'),
    dict(id='ib_break_fail', name='Failed IB breakout (fade)', family='initial balance', detect=ib_break_fail,
         rules='IB breaks, then closes back inside within 30 minutes; lean the other way.'),
    dict(id='ivb_break', name='Initial volume breakout', family='volume', detect=ivb_break,
         rules='Close beyond the high/low of the heaviest-volume bar of the first 30 minutes, on 1.5x normal volume for the time of day, before 12:00.'),
    dict(id='va_reentry', name='Value-area re-entry (80% rule)', family='volume profile', detect=va_reentry,
         rules="Open outside yesterday's value area, then 30 minutes of closes back inside; lean toward the far edge."),
    dict(id='poc_magnet', name="Pull to yesterday's POC", family='volume profile', detect=poc_magnet,
         rules="Open inside yesterday's value area at least 1 ATR from its POC and drifting toward it after 30 minutes."),
    dict(id='va_edge_rejection', name='Value-area edge rejection', family='volume profile', detect=va_edge_rejection,
         rules="Probe of yesterday's VAH/VAL from inside that closes back inside on a rejection bar."),
    dict(id='outside_va_acceptance', name='Acceptance outside value', family='volume profile', detect=outside_va_acceptance,
         rules="Six straight closes above yesterday's VAH (or below VAL) after 10:00; lean with it."),
    dict(id='vwap_reclaim', name='VWAP reclaim / loss', family='vwap', detect=vwap_reclaim,
         rules='30+ minutes on one side of VWAP, then a close through it on 1.2x normal volume.'),
    dict(id='vwap_2sd_revert', name='VWAP 2-sigma snap-back', family='vwap', detect=vwap_2sd_revert,
         rules='Close outside the 2-sigma VWAP band, next close back inside; lean toward VWAP.'),
    dict(id='pd_sweep', name="Sweep of yesterday's high/low", family='liquidity', detect=pd_sweep,
         rules="Wick through yesterday's high (low) and close back below (above) it."),
    dict(id='ib_sweep', name='Sweep of the IB extreme', family='liquidity', detect=ib_sweep,
         rules='After 10:30, wick beyond the IB high (low) and close back inside.'),
    dict(id='choch', name='Change of character (protected level breaks)', family='structure', detect=choch,
         rules='The protected swing that held the trend is closed through.'),
    dict(id='bos', name='Break of structure (continuation)', family='structure', detect=bos,
         rules="Close beyond the last swing in the trend's direction."),
    dict(id='protected_hold', name='Protected level holds', family='structure', detect=protected_hold,
         rules='Pullback to within 0.25 ATR of the protected level, closes back on the trend side with a rejection bar.'),
    dict(id='gap_fill', name='Gap fill attempt', family='gaps', detect=gap_fill,
         rules="Gap of 0.25%+ and the first 30 minutes already moving back toward yesterday's close."),
    dict(id='power_hour', name='Power-hour trend', family='time of day', detect=power_hour,
         rules='At 15:00, price above VWAP and above the IB high (or below both); lean with it into the close.'),
]
