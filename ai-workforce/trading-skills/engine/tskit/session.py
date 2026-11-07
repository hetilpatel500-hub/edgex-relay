"""Sessions, levels and daily series.

A port of the Edgex chart lab's core (same formulas, same names), so lab
setups written against `core.Session` and `core.Daily` run here unchanged.

Levels computed for every regular session (9:30-16:00 ET, 5-minute bars):
  vwap / vsd       session VWAP (typical price) and its volume-weighted stdev
  rvol             bar volume / mean volume of the same 5-minute slot over the
                   previous 20 sessions (None until 5 sessions of history)
  atr              ATR(14) of 5-minute true range, carried across sessions
  or_hi / or_lo    opening range, first 15 minutes
  ib_hi / ib_lo    initial balance, first 60 minutes
  ivb_*            initial volume bar: heaviest bar of the first 30 minutes
  poc / vah / val  volume profile (5 bps bins, 70% value area)
  prior            previous session object
  trend / prot / event
                   swing structure: pivots of 2 bars each side, trend, the
                   protected swing, and bos_up / bos_dn / choch_up / choch_dn
"""
import math, statistics as st
from . import data

ETFS = ['SPY', 'QQQ', 'IWM', 'DIA']
STOCKS = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'AMD']
UNIVERSE = ETFS + STOCKS
ETF_LIKE = set(ETFS) | {'VOO', 'VTI', 'IVV', 'XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLU', 'XLB', 'XLRE',
                        'XLC', 'SMH', 'SOXX', 'TLT', 'GLD', 'SLV', 'EEM', 'EFA', 'HYG', 'LQD', 'RSP'}
OPEN, CLOSE = 570, 960          # minutes after midnight ET
FULL_SESSION = 78               # 5-minute bars in a full regular session


def ordered(syms):
    """The lab's universe order first, then everything else alphabetically
    (drawdowns and random baselines depend on the order trades are read)."""
    return sorted(set(syms), key=lambda s: (UNIVERSE.index(s) if s in UNIVERSE else len(UNIVERSE), s))


def cost_bps(sym, override=None):
    """Round-trip cost (spread + slippage) charged to every simulated trade."""
    if override is not None:
        return float(override)
    return 2.0 if sym.upper() in ETF_LIKE else 3.0


class Bar:
    __slots__ = ('m', 'o', 'h', 'l', 'c', 'v')

    def __init__(self, m, o, h, l, c, v):
        self.m, self.o, self.h, self.l, self.c, self.v = m, o, h, l, c, v


def clock(m):
    return f'{m // 60}:{m % 60:02d}'


class Session:
    """One regular session plus every level the setups read."""

    def __init__(self, sym, day, bars):
        self.sym, self.day, self.bars = sym, day, bars
        self.prior = None
        self.partial = False

    def build(self, slot_hist, prev_close, atr_state):
        b = self.bars
        self.open = b[0].o
        self.vwap, self.vsd = [], []
        pv = vv = pv2 = 0.0
        for x in b:
            tp = (x.h + x.l + x.c) / 3
            pv += tp * x.v; vv += x.v; pv2 += tp * tp * x.v
            w = pv / vv if vv else tp
            self.vwap.append(w)
            self.vsd.append(math.sqrt(max(pv2 / vv - w * w, 0)) if vv else 0)
        self.rvol = []
        for k, x in enumerate(b):
            h = slot_hist.setdefault(k, [])
            avg = sum(h[-20:]) / len(h[-20:]) if len(h) >= 5 else None
            self.rvol.append(x.v / avg if avg else None)
        for k, x in enumerate(b):
            slot_hist[k].append(x.v)
        self.atr = []
        pc = prev_close
        for x in b:
            tr = x.h - x.l if pc is None else max(x.h - x.l, abs(x.h - pc), abs(x.l - pc))
            atr_state.append(tr)
            del atr_state[:-14]
            self.atr.append(sum(atr_state) / len(atr_state))
            pc = x.c
        self.or_hi, self.or_lo = max(x.h for x in b[:3]), min(x.l for x in b[:3])
        self.ib_hi, self.ib_lo = max(x.h for x in b[:12]), min(x.l for x in b[:12])
        k = max(range(min(6, len(b))), key=lambda j: b[j].v)
        self.ivb_i, self.ivb_hi, self.ivb_lo = k, b[k].h, b[k].l
        self.hi, self.lo, self.close = max(x.h for x in b), min(x.l for x in b), b[-1].c
        self.poc, self.vah, self.val = profile(b)
        self.structure()
        return self

    def structure(self):
        b = self.bars
        n = len(b)
        self.trend, self.prot, self.event = [0] * n, [None] * n, [None] * n
        trend, prot = 0, None
        sh = sl = None
        sh_used = sl_used = False
        for i in range(n):
            k = i - 2           # pivot at k is confirmed at bar i
            if k >= 2:
                if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
                    sh, sh_used = b[k].h, False
                if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
                    sl, sl_used = b[k].l, False
            c = b[i].c
            ev = None
            if trend == 1 and prot is not None and c < prot:
                trend, prot, ev = -1, (sh if sh is not None else max(x.h for x in b[:i + 1])), 'choch_dn'
            elif trend == -1 and prot is not None and c > prot:
                trend, prot, ev = 1, (sl if sl is not None else min(x.l for x in b[:i + 1])), 'choch_up'
            elif sh is not None and not sh_used and c > sh and trend >= 0:
                sh_used = True
                cand = sl if sl is not None else min(x.l for x in b[:i + 1])
                prot = max(prot, cand) if trend == 1 and prot is not None else cand
                trend, ev = 1, 'bos_up'
            elif sl is not None and not sl_used and c < sl and trend <= 0:
                sl_used = True
                cand = sh if sh is not None else max(x.h for x in b[:i + 1])
                prot = min(prot, cand) if trend == -1 and prot is not None else cand
                trend, ev = -1, 'bos_dn'
            self.trend[i], self.prot[i], self.event[i] = trend, prot, ev

    def slot_of(self, minutes):
        """Index of the last bar that started at or before `minutes` (ET)."""
        k = None
        for i, x in enumerate(self.bars):
            if x.m <= minutes:
                k = i
        return k


def profile(bars, bps=5.0):
    """(poc, vah, val) from bars, volume spread evenly over each bar's range."""
    px = st.median(x.c for x in bars)
    step = px * bps / 1e4
    vol = {}
    for x in bars:
        lo, hi = int(x.l // step), int(x.h // step)
        share = x.v / (hi - lo + 1)
        for k in range(lo, hi + 1):
            vol[k] = vol.get(k, 0) + share
    poc = max(vol, key=vol.get)
    total = sum(vol.values())
    lo = hi = poc
    acc = vol[poc]
    while acc < 0.7 * total:
        up, dn = vol.get(hi + 1, 0), vol.get(lo - 1, 0)
        if up == 0 and dn == 0:
            break
        if up >= dn:
            hi += 1; acc += up
        else:
            lo -= 1; acc += dn
    mid = lambda k: (k + 0.5) * step
    return mid(poc), mid(hi) + step / 2, mid(lo) - step / 2


def _days(rows):
    days = {}
    for t, o, h, l, c, v in rows:
        d = data.et(t)
        m = d.hour * 60 + d.minute
        if OPEN <= m < CLOSE:
            days.setdefault(d.date(), []).append(Bar(m, o, h, l, c, v))
    return days


def sessions(rows, sym):
    """Full regular sessions only. A partial or half day breaks the chain of
    prior-day levels, exactly as in the lab."""
    days = _days(rows)
    out, slot_hist, atr_state, prev = [], {}, [], None
    for day in sorted(days):
        b = days[day]
        if len(b) != FULL_SESSION or b[0].m != OPEN:
            prev = None
            continue
        s = Session(sym, day, b).build(slot_hist, prev.close if prev else None, atr_state)
        s.prior = prev
        out.append(s)
        prev = s
    return out


def live_session(rows, sym, full=None):
    """(today, full_sessions). `today` is the latest day's session, built
    from whatever bars it has so far (the last full session if the latest day
    is complete). None when the latest day has no 9:30 bar."""
    full = sessions(rows, sym) if full is None else full
    days = _days(rows)
    if not days:
        return None, full
    last = max(days)
    if full and full[-1].day == last:
        return full[-1], full
    b = days[last]
    if b[0].m != OPEN:
        return None, full
    slot_hist = {}
    for s in full[-20:]:
        for k, x in enumerate(s.bars):
            slot_hist.setdefault(k, []).append(x.v)
    prev = full[-1] if full else None
    atr_state = [x.h - x.l for x in prev.bars[-14:]] if prev else []
    s = Session(sym, last, b).build(slot_hist, prev.close if prev else None, atr_state)
    s.prior, s.partial = prev, True
    return s, full


def load_sessions(d, syms):
    """{symbol: [full sessions]} from a store."""
    out = {}
    for s in syms:
        rows = data.read(d, s, 'M5')
        if rows:
            out[s] = sessions(rows, s)
    return out


# ---- daily bars -----------------------------------------------------------
class Daily:
    """Daily series with the indicators the daily setups read."""

    def __init__(self, rows, sym):
        self.sym = sym
        self.day = [data.et(t).date() for t, *_ in rows]
        if rows:
            self.o, self.h, self.l, self.c, self.v = (list(x) for x in zip(*[r[1:] for r in rows]))
        else:
            self.o = self.h = self.l = self.c = self.v = []
        n = len(self.c)
        self.atr, trs = [], []
        for i in range(n):
            pc = self.c[i - 1] if i else self.c[i]
            trs.append(max(self.h[i] - self.l[i], abs(self.h[i] - pc), abs(self.l[i] - pc)))
            w = trs[-14:]
            self.atr.append(sum(w) / len(w))
        self.sma200 = sma(self.c, 200)
        self.sma50 = sma(self.c, 50)
        self.sma5 = sma(self.c, 5)
        self.rsi2 = rsi(self.c, 2)


def sma(x, n):
    out, acc = [], 0.0
    for i, v in enumerate(x):
        acc += v
        if i >= n:
            acc -= x[i - n]
        out.append(acc / n if i >= n - 1 else None)
    return out


def rsi(x, n):
    if not x:
        return []
    out, ag, al = [None], 0.0, 0.0
    for i in range(1, len(x)):
        ch = x[i] - x[i - 1]
        g, l = max(ch, 0), max(-ch, 0)
        if i <= n:
            ag += g / n; al += l / n
            out.append(None if i < n else (100 if al == 0 else 100 - 100 / (1 + ag / al)))
        else:
            ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + l) / n
            out.append(100 if al == 0 else 100 - 100 / (1 + ag / al))
    return out
