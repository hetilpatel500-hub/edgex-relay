"""Synthetic market data for tests: driftless random walks, no real prices."""
import os, random, sys, tempfile
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from tskit import data  # noqa: E402

ET = ZoneInfo('America/New_York')


def weekdays(start, n):
    d, out = start, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def make_store(symbols=('AAA', 'BBB'), days=90, seed=1, start=date(2026, 3, 2), vol=0.0012, partial_last=0):
    """A temp store with full 78-bar sessions of a driftless random walk.
    partial_last=N adds a final day with only N bars (a live session)."""
    rnd = random.Random(seed)
    d = tempfile.mkdtemp(prefix='tskit-test-')
    for si, sym in enumerate(symbols):
        px = 100.0 + 50 * si
        m5, dly = [], []
        ds = weekdays(start, days + (1 if partial_last else 0))
        for di, day in enumerate(ds):
            nbars = partial_last if (partial_last and di == len(ds) - 1) else 78
            o_day = px * (1 + rnd.gauss(0, 0.004))
            p = o_day
            hi = lo = o_day
            vday = 0
            for k in range(nbars):
                t = datetime(day.year, day.month, day.day, 9, 30, tzinfo=ET) + timedelta(minutes=5 * k)
                o = p
                c = o * (1 + rnd.gauss(0, vol))
                h = max(o, c) * (1 + abs(rnd.gauss(0, vol / 2)))
                l = min(o, c) * (1 - abs(rnd.gauss(0, vol / 2)))
                v = int(1e5 * (1.5 if k < 6 or k > 70 else 1.0) * (0.6 + rnd.random()))
                m5.append((t.astimezone(timezone.utc).strftime(data.FMT), o, h, l, c, v))
                hi, lo, p, vday = max(hi, h), min(lo, l), c, vday + v
            if nbars == 78:
                t0 = datetime(day.year, day.month, day.day, tzinfo=ET).astimezone(timezone.utc).strftime(data.FMT)
                dly.append((t0, o_day, hi, lo, p, vday))
            px = p
        data.write(d, sym, 'M5', m5)
        data.write(d, sym, 'D', dly)
    return d
