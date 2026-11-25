"""Trade statistics, intervals and calibration scores."""
import math, random, statistics as st


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


def wilson(k, n, z=1.645):
    """Wilson score interval for k successes in n trials (90% by default)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def pct(xs, q):
    """Linear-interpolated percentile, q in [0, 100]."""
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * q / 100
    f = math.floor(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def brier(preds, outs):
    return sum((p - o) ** 2 for p, o in zip(preds, outs)) / len(preds) if preds else None


def reliability(preds, outs, bins=(0, .2, .3, .4, .5, .6, .7, 1.0001)):
    """Rows of (bin, n, mean predicted, observed frequency, Wilson interval)."""
    rows = []
    for lo, hi in zip(bins, bins[1:]):
        idx = [i for i, p in enumerate(preds) if lo <= p < hi]
        if not idx:
            continue
        k = sum(outs[i] for i in idx)
        rows.append({'bin': f'{lo:.0%}-{min(hi, 1):.0%}', 'n': len(idx),
                     'predicted': round(sum(preds[i] for i in idx) / len(idx), 3),
                     'observed': round(k / len(idx), 3),
                     'observed_90': [round(x, 3) for x in wilson(k, len(idx))]})
    return rows


def equity_mc(rs, runs=2000, seed=11):
    """Shuffle the order of trades: spread of max drawdown and worst running
    loss. The total is fixed; the path (and the pain) is not."""
    if not rs:
        return None
    rnd = random.Random(seed)
    dds, lows = [], []
    xs = list(rs)
    for _ in range(runs):
        rnd.shuffle(xs)
        eq = peak = dd = low = 0.0
        for r in xs:
            eq += r; peak = max(peak, eq); dd = max(dd, peak - eq); low = min(low, eq)
        dds.append(dd); lows.append(low)
    return {'runs': runs, 'max_drawdown_r': {'p50': round(pct(dds, 50), 2), 'p90': round(pct(dds, 90), 2),
                                             'p99': round(pct(dds, 99), 2)},
            'worst_running_r': {'p50': round(pct(lows, 50), 2), 'p10': round(pct(lows, 10), 2)}}


def luck_check(observed_avg, n, pool, draws=4000, seed=5):
    """Share of random-entry samples of size n (drawn from `pool`, the R of
    random entries with the same exit) whose average is at least the
    observed average: how often pure luck looks this good."""
    if not pool or n == 0:
        return None
    rnd = random.Random(seed)
    hit = 0
    for _ in range(draws):
        s = sum(rnd.choice(pool) for _ in range(n)) / n
        hit += s >= observed_avg
    return round(hit / draws, 4)
