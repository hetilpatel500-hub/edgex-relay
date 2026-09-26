"""Chart Desk lab core: sessions, levels, exits and stats.

Analysis only. Nothing here places, stages or suggests orders; the lab measures
how chart setups behaved on past Webull bars so the desk's commentary can say
what the evidence is.

Levels computed for every regular session (9:30-16:00 ET, 5-minute bars):
  vwap / vwap_sd   session VWAP (typical price) and its volume-weighted stdev
  rvol             bar volume / mean volume of the same 5-minute slot over the
                   previous 20 sessions
  atr              ATR(14) of 5-minute true range, carried across sessions
  or15             opening range, first 15 minutes (bars 0-2)
  ib               initial balance, first 60 minutes (bars 0-11)
  ivb              initial volume bar: the highest-volume bar of the first 30
                   minutes; its high and low are the "initial volume" levels
  profile          volume profile (each bar's volume spread evenly over the
                   price bins between its low and high, bins of 5 bps):
                   poc, vah, val (70% value area)
  prior            previous session's high, low, close, poc, vah, val
  structure        swing pivots (2 bars each side, confirmed 2 bars later),
                   trend, protected level (the swing that must hold for the
                   trend to stay intact) and events bos_up / bos_dn /
                   choch_up / choch_dn
"""
import csv, gzip, math, os, statistics as st
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ET = ZoneInfo('America/New_York')
ETFS = ['SPY', 'QQQ', 'IWM', 'DIA']
STOCKS = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'AMD']
UNIVERSE = ETFS + STOCKS
# Round-trip cost charged to every simulated trade (spread + slippage), in bps.
COST_BPS = {s: 2.0 for s in ETFS} | {s: 3.0 for s in STOCKS}
OPEN, CLOSE = 570, 960          # minutes after midnight ET
FULL_SESSION = 78               # 5-minute bars in a full regular session


class Bar:
    __slots__ = ('m', 'o', 'h', 'l', 'c', 'v')

    def __init__(self, m, o, h, l, c, v):
        self.m, self.o, self.h, self.l, self.c, self.v = m, o, h, l, c, v


def read(sym, tf):
    p = os.path.join(HERE, 'data', f'{sym}_{tf}.csv.gz')
    with gzip.open(p, 'rt') as fh:
        for r in csv.DictReader(fh):
            yield r['t'], float(r['o']), float(r['h']), float(r['l']), float(r['c']), float(r['v'])


def et(t):
    return datetime.fromisoformat(t.replace('Z', '+00:00')).astimezone(ET)


class Session:
    """One regular session plus every level the setups read."""

    def __init__(self, sym, day, bars):
        self.sym, self.day, self.bars = sym, day, bars
        self.prior = None

    # ---- per-session levels -------------------------------------------------
    def build(self, slot_hist, prev_close, atr_state):
        b = self.bars
        n = len(b)
        self.open = b[0].o
        # VWAP and stdev
        self.vwap, self.vsd = [], []
        pv = vv = pv2 = 0.0
        for x in b:
            tp = (x.h + x.l + x.c) / 3
            pv += tp * x.v; vv += x.v; pv2 += tp * tp * x.v
            w = pv / vv if vv else tp
            self.vwap.append(w)
            self.vsd.append(math.sqrt(max(pv2 / vv - w * w, 0)) if vv else 0)
        # relative volume by slot
        self.rvol = []
        for k, x in enumerate(b):
            h = slot_hist.setdefault(k, [])
            avg = sum(h[-20:]) / len(h[-20:]) if len(h) >= 5 else None
            self.rvol.append(x.v / avg if avg else None)
        for k, x in enumerate(b):
            slot_hist[k].append(x.v)
        # ATR(14) of 5-minute bars, carried from the previous session
        self.atr = []
        pc = prev_close
        for x in b:
            tr = x.h - x.l if pc is None else max(x.h - x.l, abs(x.h - pc), abs(x.l - pc))
            atr_state.append(tr)
            del atr_state[:-14]
            self.atr.append(sum(atr_state) / len(atr_state))
            pc = x.c
        # opening range, initial balance, initial volume bar
        self.or_hi, self.or_lo = max(x.h for x in b[:3]), min(x.l for x in b[:3])
        self.ib_hi, self.ib_lo = max(x.h for x in b[:12]), min(x.l for x in b[:12])
        k = max(range(6), key=lambda j: b[j].v)
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


def sessions(sym):
    days = {}
    for t, o, h, l, c, v in read(sym, 'M5'):
        d = et(t)
        m = d.hour * 60 + d.minute
        if OPEN <= m < CLOSE:
            days.setdefault(d.date(), []).append(Bar(m, o, h, l, c, v))
    out, slot_hist, atr_state, prev = [], {}, [], None
    for day in sorted(days):
        b = days[day]
        if len(b) != FULL_SESSION or b[0].m != OPEN:
            prev = None      # partial or half day: skip it and don't chain levels
            continue
        s = Session(sym, day, b).build(slot_hist, prev.close if prev else None, atr_state)
        s.prior = prev
        out.append(s)
        prev = s
    return out


# ---- simulated exits ------------------------------------------------------
EXITS = {
    '1atr/1.5atr': (1.0, 1.5),
    '1atr/2atr': (1.0, 2.0),
    '1.5atr/3atr': (1.5, 3.0),
    '1atr/close': (1.0, None),
    '2atr/close': (2.0, None),
    '2atr/4atr': (2.0, 4.0),
    '3atr/close': (3.0, None),
}


def trade(s, i, d, stop_m, tgt_m):
    """Enter at the open of bar i+1 in direction d; return R after costs.
    Stop and target are ATR multiples; anything open is closed at the last bar
    of the session. If one bar touches both, the stop is assumed first."""
    b = s.bars
    if i + 1 >= len(b):
        return None
    e = b[i + 1].o
    risk = stop_m * s.atr[i]
    if risk <= 0:
        return None
    stop = e - d * risk
    tgt = e + d * tgt_m * s.atr[i] if tgt_m else None
    x = b[-1].c
    for k in range(i + 1, len(b)):
        y = b[k]
        if (y.l <= stop) if d == 1 else (y.h >= stop):
            x = stop; break
        if tgt is not None and ((y.h >= tgt) if d == 1 else (y.l <= tgt)):
            x = tgt; break
    cost = COST_BPS[s.sym] / 1e4 * e
    return ((x - e) * d - cost) / risk


def stats(rs):
    n = len(rs)
    if n == 0:
        return {'n': 0}
    wins = [r for r in rs if r > 0]
    losses = [-r for r in rs if r <= 0]
    mean = sum(rs) / n
    sd = st.pstdev(rs) if n > 1 else 0
    eq = peak = dd = 0
    for r in rs:
        eq += r; peak = max(peak, eq); dd = max(dd, peak - eq)
    return {
        'n': n,
        'win_rate': round(len(wins) / n, 3),
        'avg_r': round(mean, 3),
        'total_r': round(sum(rs), 2),
        'profit_factor': round(sum(wins) / sum(losses), 2) if losses and sum(losses) > 0 else None,
        't_stat': round(mean / sd * math.sqrt(n), 2) if sd > 0 else None,
        'max_drawdown_r': round(dd, 2),
    }


# ---- daily bars -----------------------------------------------------------
class Daily:
    """Daily series with the indicators the daily setups read."""

    def __init__(self, sym):
        self.sym = sym
        rows = list(read(sym, 'D'))
        self.day = [et(t).date() if not t.endswith('T04:00:00Z') and not t.endswith('T05:00:00Z')
                    else datetime.fromisoformat(t[:10]).date() for t, *_ in rows]
        self.o, self.h, self.l, self.c, self.v = (list(x) for x in zip(*[r[1:] for r in rows]))
        n = len(self.c)
        self.atr, trs = [], []
        for i in range(n):
            pc = self.c[i - 1] if i else self.c[i]
            trs.append(max(self.h[i] - self.l[i], abs(self.h[i] - pc), abs(self.l[i] - pc)))
            w = trs[-14:]
            self.atr.append(sum(w) / len(w))
        self.sma200 = sma(self.c, 200)
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


EXITS_D = {
    '2atr/hold5': (2.0, None, 5),
    '2atr/hold10': (2.0, None, 10),
    '1.5atr/3atr/hold10': (1.5, 3.0, 10),
    '1atr/2atr/hold5': (1.0, 2.0, 5),
}


def trade_d(ser, i, d, stop_m, tgt_m, hold):
    """Enter at the next day's open; stop/target in daily ATRs; exit at the
    close of the hold-th day. Gaps through the stop fill at the open."""
    if i + 1 >= len(ser.c):
        return None
    e = ser.o[i + 1]
    risk = stop_m * ser.atr[i]
    stop = e - d * risk
    tgt = e + d * tgt_m * ser.atr[i] if tgt_m else None
    last = min(i + hold, len(ser.c) - 1)
    x = ser.c[last]
    for k in range(i + 1, last + 1):
        if d == 1 and ser.l[k] <= stop:
            x = min(stop, ser.o[k]) if k > i + 1 else stop; break
        if d == -1 and ser.h[k] >= stop:
            x = max(stop, ser.o[k]) if k > i + 1 else stop; break
        if tgt is not None and ((ser.h[k] >= tgt) if d == 1 else (ser.l[k] <= tgt)):
            x = tgt; break
    cost = COST_BPS[ser.sym] / 1e4 * e
    return ((x - e) * d - cost) / risk
