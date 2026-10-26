"""The time machine: replay the rest of the trading day thousands of times.

Given a trade (symbol, side, entry, stop, target, and the time it is taken),
it asks: on past days that looked like this one at this time of day, how did
the rest of the session unfold, and how often would this exact stop and
target have been hit?

Method
  1. Memory: every full past session in the store (pooled across symbols by
     default), strictly before the trade's date, so nothing from the future
     leaks in.
  2. Which days: by default every past day at the same clock time
     (`condition='none'`). `condition='knn'` keeps only the days most like
     today (move since the open, distance from VWAP, gap, volume so far,
     trend, range so far, in ATRs, oriented to the trade). In walk-forward
     tests on 12 US symbols (May-Oct 2026) the k-nearest filter added no
     skill and slightly more noise, so it is off by default.
     `setup=ID` switches to setup mode: the memory is that setup's own past
     signals (with its side and filter), each replayed from its signal bar,
     oriented to the trade's direction and rescaled to today's ATR. That
     is where an edge, if any, shows up.
  3. Paths: each simulated path stitches 30-minute blocks (6 five-minute
     bars) taken from random past days at the same clock times, so the
     time-of-day pattern of volatility and the short-term momentum inside a
     block are kept. Each block's moves are rescaled from its own day's ATR
     to today's ATR at entry.
  4. Each path is walked bar by bar against the stop and target (stop first
     if a bar touches both; gaps fill at the open; flat at the close).

What it reports, next to each other
  * odds from the simulated paths, with a 90% range from re-drawing the set
    of past days (the honest uncertainty: 10,000 paths come from a few
    hundred real days, so more paths make the numbers smoother, not truer);
  * the plain count on the real past days, replayed as they happened;
  * a coin-flip baseline: the same paths with each block's direction
    randomised, which keeps the volatility but removes any direction. With
    a 1-ATR stop and a 2-ATR target, even a coin flip reaches the target
    first about a third of the time; the gap to the baseline is the edge.
"""
import math, random, statistics as st
from . import data, session, sim, stats, DISCLAIMER

BLOCK = 6
WEIGHTS = (1.0, 1.0, 0.5, 0.7, 0.5, 0.7)
FEATURES = ('move_since_open_atr', 'vs_vwap_atr', 'gap_atr', 'log_volume_vs_normal', 'trend', 'range_so_far_atr')


def raw_moves(s):
    """Per bar j >= 1: (open, high, low, close) minus the previous close, in
    price units. Cached on the session."""
    r = getattr(s, '_raw', None)
    if r is None:
        b = s.bars
        r = [None] + [(b[j].o - b[j - 1].c, b[j].h - b[j - 1].c, b[j].l - b[j - 1].c, b[j].c - b[j - 1].c)
                      for j in range(1, len(b))]
        s._raw = r
    return r


def features(s, k, d):
    a = s.atr[k]
    c = s.bars[k].c
    gap = d * (s.open - s.prior.close) / a if s.prior is not None else 0.0
    rv = [x for x in s.rvol[:k + 1] if x]
    vol = math.log(sum(rv) / len(rv)) if rv else 0.0
    rng = (max(x.h for x in s.bars[:k + 1]) - min(x.l for x in s.bars[:k + 1])) / a
    return (d * (c - s.open) / a, d * (c - s.vwap[k]) / a, gap, vol, d * s.trend[k], rng)


class Prep:
    def __init__(self, pool, k, n_lib, today_f, near_f, condition):
        self.pool, self.k, self.n_lib = pool, k, n_lib
        self.today_f, self.near_f, self.condition = today_f, near_f, condition


def prepare(lib, today, k, d, condition='none', neighbors=None):
    """Pick the past days to learn from. `lib` is a list of full sessions."""
    cand = [s for s in lib if len(s.bars) == session.FULL_SESSION and s.atr[k] > 0]
    if not cand:
        raise ValueError('no past sessions in the store to learn from')
    f0 = features(today, k, d)
    if condition == 'none' or len(cand) <= 40:
        chosen = cand
    else:
        fs = [features(s, k, d) for s in cand]
        cols = list(zip(*fs))
        mu = [sum(c) / len(c) for c in cols]
        sd = [st.pstdev(c) or 1.0 for c in cols]
        z0 = [(f0[i] - mu[i]) / sd[i] for i in range(len(f0))]
        dist = []
        for s, f in zip(cand, fs):
            dist.append((math.sqrt(sum(WEIGHTS[i] * ((f[i] - mu[i]) / sd[i] - z0[i]) ** 2 for i in range(len(f)))), s))
        dist.sort(key=lambda x: x[0])
        kk = neighbors or max(40, round(0.25 * len(cand)))
        chosen = [s for _, s in dist[:min(kk, len(cand))]]
    near = [features(s, k, d) for s in chosen]
    near_mean = tuple(round(sum(c) / len(c), 2) for c in zip(*near))
    pool = [(raw_moves(s), s.atr[k], s) for s in chosen]
    return Prep(pool, k, len(cand), tuple(round(x, 2) for x in f0), near_mean, condition)


def _walk(segments, e, d, stop, tgt):
    """segments: iterable of (raw, f, j0, j1). Returns (outcome, exit, bars, mfe, mae)."""
    prev = e
    mfe = mae = 0.0
    n = 0
    for raw, f, j0, j1 in segments:
        for j in range(j0, j1):
            do, dh, dl, dc = raw[j]
            if f > 0:
                o, h, l = prev + do * f, prev + dh * f, prev + dl * f
            else:
                o, h, l = prev + do * f, prev + dl * f, prev + dh * f
            n += 1
            if d == 1:
                if o <= stop:
                    return 'stop', o, n, mfe, max(mae, e - o)
                if tgt is not None and o >= tgt:
                    return 'target', o, n, max(mfe, o - e), mae
                if l <= stop:
                    return 'stop', stop, n, max(mfe, h - e), max(mae, e - stop)
                if tgt is not None and h >= tgt:
                    return 'target', tgt, n, max(mfe, tgt - e), max(mae, e - l)
                mfe, mae = max(mfe, h - e), max(mae, e - l)
            else:
                if o >= stop:
                    return 'stop', o, n, mfe, max(mae, o - e)
                if tgt is not None and o <= tgt:
                    return 'target', o, n, max(mfe, e - o), mae
                if h >= stop:
                    return 'stop', stop, n, max(mfe, e - l), max(mae, stop - e)
                if tgt is not None and l <= tgt:
                    return 'target', tgt, n, max(mfe, e - tgt), max(mae, h - e)
                mfe, mae = max(mfe, e - l), max(mae, h - e)
            prev = prev + dc * f
    return 'close', prev, n, mfe, mae


def _stitched(pool, k, last, A, block, rnd, flip):
    j = k + 1
    while j < last:
        raw, a, _ = pool[rnd.randrange(len(pool))]
        f = A / a
        if flip and rnd.random() < 0.5:
            f = -f
        j1 = min(j + block, last)
        yield raw, f, j, j1
        j = j1


def simulate(pool, k, e, d, stop, tgt, A, paths, block=BLOCK, seed=7, flip=False, cost_bps=3.0):
    """Aggregate outcome counts and R-multiples over `paths` stitched paths."""
    rnd = random.Random(seed)
    last = session.FULL_SESSION
    risk = abs(e - stop)
    cnt = {'target': 0, 'stop': 0, 'close': 0}
    rs, t_tgt, t_stop, close_r, mfes, maes = [], [], [], [], [], []
    for _ in range(paths):
        out, x, n, mfe, mae = _walk(_stitched(pool, k, last, A, block, rnd, flip), e, d, stop, tgt)
        cnt[out] += 1
        r = sim.r_multiple(e, x, d, risk, cost_bps)
        rs.append(r)
        mfes.append(mfe / risk); maes.append(mae / risk)
        if out == 'target':
            t_tgt.append(n * 5)
        elif out == 'stop':
            t_stop.append(n * 5)
        else:
            close_r.append(r)
    return dict(cnt=cnt, rs=rs, t_tgt=t_tgt, t_stop=t_stop, close_r=close_r, mfe=mfes, mae=maes, n=paths)


def replay_days(pool, k, e, d, stop, tgt, A, cost_bps=3.0):
    """Each chosen past day replayed as it actually happened (no stitching)."""
    last = session.FULL_SESSION
    risk = abs(e - stop)
    cnt = {'target': 0, 'stop': 0, 'close': 0}
    rs = []
    for raw, a, s in pool:
        out, x, n, mfe, mae = _walk([(raw, A / a, k + 1, last)], e, d, stop, tgt)
        cnt[out] += 1
        rs.append(sim.r_multiple(e, x, d, risk, cost_bps))
    return cnt, rs


def _odds(cnt, n):
    return {'target_first': round(cnt['target'] / n, 4), 'stop_first': round(cnt['stop'] / n, 4),
            'neither_by_close': round(cnt['close'] / n, 4)}


def _r(x):
    return None if x is None else round(x, 3)


def run(prep, e, d, stop, tgt, A, paths=10000, block=BLOCK, seed=7, boot=40, boot_paths=500, cost_bps=3.0):
    k, pool = prep.k, prep.pool
    main = simulate(pool, k, e, d, stop, tgt, A, paths, block, seed, False, cost_bps)
    base = simulate(pool, k, e, d, stop, tgt, A, paths, block, seed + 1, True, cost_bps)
    rnd = random.Random(seed + 2)
    bt, bs, bn, be = [], [], [], []
    for b in range(boot):
        rp = [pool[rnd.randrange(len(pool))] for _ in pool]
        x = simulate(rp, k, e, d, stop, tgt, A, boot_paths, block, seed + 10 + b, False, cost_bps)
        bt.append(x['cnt']['target'] / boot_paths); bs.append(x['cnt']['stop'] / boot_paths)
        bn.append(x['cnt']['close'] / boot_paths); be.append(sum(x['rs']) / boot_paths)
    real_cnt, real_rs = replay_days(pool, k, e, d, stop, tgt, A, cost_bps)
    nr = len(pool)
    rng90 = lambda xs: [round(stats.pct(xs, 5), 4), round(stats.pct(xs, 95), 4)]
    rs = main['rs']
    return {
        'paths': paths,
        'odds': _odds(main['cnt'], paths),
        'odds_range_90': {'target_first': rng90(bt), 'stop_first': rng90(bs), 'neither_by_close': rng90(bn)},
        'expected_r': _r(sum(rs) / paths),
        'expected_r_range_90': [_r(stats.pct(be, 5)), _r(stats.pct(be, 95))],
        'r_distribution': {f'p{q}': _r(stats.pct(rs, q)) for q in (5, 25, 50, 75, 95)},
        'minutes_to_target_median': _r(stats.pct(main['t_tgt'], 50)) if main['t_tgt'] else None,
        'minutes_to_stop_median': _r(stats.pct(main['t_stop'], 50)) if main['t_stop'] else None,
        'r_at_close_if_neither_median': _r(stats.pct(main['close_r'], 50)) if main['close_r'] else None,
        'best_open_profit_r_median': _r(stats.pct(main['mfe'], 50)),
        'worst_open_loss_r_median': _r(stats.pct(main['mae'], 50)),
        'coin_flip_baseline': {'odds': _odds(base['cnt'], paths), 'expected_r': _r(sum(base['rs']) / paths)},
        'real_days': {'n': nr, 'counts': real_cnt, 'odds': _odds(real_cnt, nr),
                      'target_first_90': [round(x, 4) for x in stats.wilson(real_cnt['target'], nr)],
                      'stop_first_90': [round(x, 4) for x in stats.wilson(real_cnt['stop'], nr)],
                      'avg_r': _r(sum(real_rs) / nr), 'win_rate': round(sum(r > 0 for r in real_rs) / nr, 3)},
    }


# ---- setup mode ----------------------------------------------------------------
def setup_signals(store, setup_id, before_day, syms, side=None, filt=None, setup_dirs=None, results=None):
    """Past signals of one setup, as (session, bar index, trade direction).
    side/filter default to the setup's validated variant in `results`
    (a backtest results dict), else 'with' and no filter."""
    from . import setups as setups_mod, backtest
    stps = setups_mod.load(setup_dirs, store, {setup_id})
    if not stps:
        raise ValueError(f'unknown setup {setup_id}')
    stp = stps[0]
    if stp['tf'] != 'M5':
        raise ValueError(f'{setup_id} is a daily setup; the time machine replays intraday sessions only')
    ev = None
    if results:
        ev = next((r for r in results.get('results', []) if r.get('id') == setup_id and r.get('side')), None)
    side = side or (ev['side'] if ev else 'with')
    filt = filt if filt is not None else (ev['filter'] if ev else 'none')
    sgn = 1 if side == 'with' else -1
    out = []
    for sym in syms:
        for s in session.sessions(data.read(store, sym, 'M5'), sym):
            if s.day >= before_day:
                continue
            for i, d in setups_mod.fires(stp, s):
                if i + 1 >= len(s.bars) or s.atr[i] <= 0:
                    continue
                if filt and filt != 'none' and not backtest.passes(filt, backtest.FILTERS, s, i, d):
                    continue
                out.append((s, i, d * sgn))
    return out, side, filt


def run_setup(sigs, k, e, d, stop, tgt, A, resamples=10000, seed=7, cost_bps=3.0, window=12):
    """Replay each past signal's rest of day, oriented to the trade and
    rescaled to today's ATR, for no longer than today has left."""
    left = session.FULL_SESSION - 1 - k
    near = [x for x in sigs if abs(x[1] - k) <= window]
    use = near if len(near) >= 30 else sigs
    risk = abs(e - stop)
    outs, rs, bt_, bs_, br_ = [], [], [], [], []
    for s, i, dd in use:
        raw = raw_moves(s)
        f = A / s.atr[i] * dd * d
        j1 = min(session.FULL_SESSION, i + 1 + left)
        out, x, n, mfe, mae = _walk([(raw, f, i + 1, j1)], e, d, stop, tgt)
        r1 = sim.r_multiple(e, x, d, risk, cost_bps)
        outs.append((out, n)); rs.append(r1)
        o2, x2, _, _, _ = _walk([(raw, -f, i + 1, j1)], e, d, stop, tgt)
        bt_.append(((out == 'target') + (o2 == 'target')) / 2)
        bs_.append(((out == 'stop') + (o2 == 'stop')) / 2)
        br_.append((r1 + sim.r_multiple(e, x2, d, risk, cost_bps)) / 2)
    n = len(use)
    cnt = {'target': 0, 'stop': 0, 'close': 0}
    for o, _ in outs:
        cnt[o] += 1
    rnd = random.Random(seed)
    bt, bs, be = [cnt['target'] / n], [cnt['stop'] / n], [sum(rs) / n]
    for _ in range(resamples):
        idx = [rnd.randrange(n) for _ in range(n)]
        bt.append(sum(outs[j][0] == 'target' for j in idx) / n)
        bs.append(sum(outs[j][0] == 'stop' for j in idx) / n)
        be.append(sum(rs[j] for j in idx) / n)
    rng90 = lambda xs: [round(stats.pct(xs, 5), 4), round(stats.pct(xs, 95), 4)]
    bt_n, bs_n = sum(bt_) / n, sum(bs_) / n
    return {
        'resamples': resamples, 'signals_used': n, 'signals_total': len(sigs),
        'same_time_of_day': use is near,
        'odds': _odds(cnt, n),
        'odds_range_90': {'target_first': rng90(bt), 'stop_first': rng90(bs)},
        'expected_r': _r(sum(rs) / n), 'expected_r_range_90': [_r(stats.pct(be, 5)), _r(stats.pct(be, 95))],
        'r_distribution': {f'p{q}': _r(stats.pct(rs, q)) for q in (5, 25, 50, 75, 95)},
        'minutes_to_target_median': _r(stats.pct([m * 5 for o, m in outs if o == 'target'], 50)) if cnt['target'] else None,
        'minutes_to_stop_median': _r(stats.pct([m * 5 for o, m in outs if o == 'stop'], 50)) if cnt['stop'] else None,
        'coin_flip_baseline': {'odds': {'target_first': round(bt_n, 4), 'stop_first': round(bs_n, 4),
                                        'neither_by_close': round(1 - bt_n - bs_n, 4)},
                               'expected_r': _r(sum(br_) / n)},
        'real_days': {'n': n, 'counts': cnt, 'odds': _odds(cnt, n),
                      'target_first_90': [round(x, 4) for x in stats.wilson(cnt['target'], n)],
                      'win_rate': round(sum(r > 0 for r in rs) / n, 3), 'avg_r': _r(sum(rs) / n)},
    }


# ---- the full report -------------------------------------------------------
def _pool_syms(store, symbol, pool):
    have = data.symbols(store, 'M5')
    if pool == 'same':
        return [symbol]
    if pool == 'etfs':
        return [s for s in have if s in session.ETF_LIKE] or [symbol]
    if pool == 'stocks':
        return [s for s in have if s not in session.ETF_LIKE] or [symbol]
    if isinstance(pool, (list, tuple)):
        return list(pool)
    return have


def resolve_levels(e, d, A, stop=None, target=None, stop_atr=None, target_r=None, target_atr=None):
    if stop is None:
        if stop_atr is None:
            raise ValueError('give a stop price (--stop) or a stop distance in ATRs (--stop-atr)')
        stop = e - d * stop_atr * A
    risk = (e - stop) * d
    if risk <= 0:
        raise ValueError('the stop must be below the entry for a long and above it for a short')
    if target is None:
        if target_r is not None:
            target = e + d * target_r * risk
        elif target_atr is not None:
            target = e + d * target_atr * A
    if target is not None and (target - e) * d <= 0:
        raise ValueError('the target must be above the entry for a long and below it for a short')
    return stop, target, risk


def locate(store, symbol, date=None, time=None):
    """(today_session, k, library_sessions_by_symbol, full_sessions_of_symbol).
    k is the index of the last bar completed at `time` (ET 'HH:MM'), or the
    latest bar when no time is given."""
    rows = data.read(store, symbol, 'M5')
    if not rows:
        raise ValueError(f'no 5-minute bars for {symbol} in {store}; ingest some first')
    today, full = session.live_session(rows, symbol)
    if date:
        day = data.datetime.strptime(date, '%Y-%m-%d').date()
        if today is None or today.day != day:
            match = [s for s in full if s.day == day]
            if not match:
                raise ValueError(f'{symbol} has no full session on {date} in the store')
            today = match[0]
    if today is None:
        raise ValueError(f'{symbol}: the latest day has no 9:30 bar')
    if time:
        m = data.parse_et_clock(today.day, time)
        ks = [i for i, x in enumerate(today.bars) if x.m + 5 <= m]
        if not ks:
            raise ValueError(f'no 5-minute bar completed by {time} ET on {today.day}')
        k = ks[-1]
    else:
        k = len(today.bars) - 1
    if k >= session.FULL_SESSION - 1:
        raise ValueError('no time left in the session after this entry (it is the 15:55 bar)')
    return today, k, full


def time_machine(store, symbol, side, entry=None, stop=None, target=None, stop_atr=None, target_r=None,
                 target_atr=None, date=None, time=None, pool='all', condition='none', neighbors=None,
                 paths=10000, block=BLOCK, seed=7, cost=None, boot=40, setup=None, setup_side=None,
                 setup_filter=None, setup_dirs=None, results=None):
    symbol = symbol.upper()
    d = {'long': 1, 'buy': 1, 'short': -1, 'sell': -1}[side.lower()]
    today, k, full = locate(store, symbol, date, time)
    A = today.atr[k]
    e = float(entry) if entry is not None else today.bars[k].c
    stop, target, risk = resolve_levels(e, d, A, stop, target, stop_atr, target_r, target_atr)
    syms = _pool_syms(store, symbol, pool)
    cb = session.cost_bps(symbol, cost)
    bar = today.bars[k]
    rep = {
        'tool': 'time-machine', 'generated_at': data.now_utc(),
        'symbol': symbol, 'side': 'long' if d == 1 else 'short',
        'session': str(today.day), 'entry_time_et': session.clock(bar.m + 5), 'bars_left': session.FULL_SESSION - 1 - k,
        'entry': round(e, 4), 'stop': round(stop, 4), 'target': None if target is None else round(target, 4),
        'risk_per_share': round(risk, 4), 'atr_5m': round(A, 4), 'stop_in_atr': round(risk / A, 2),
        'target_in_r': None if target is None else round(abs(target - e) / risk, 2),
        'cost_bps_round_trip': cb,
    }
    if setup:
        sigs, sside, sfilt = setup_signals(store, setup, today.day, syms, setup_side, setup_filter, setup_dirs, results)
        if len(sigs) < 10:
            raise ValueError(f'{setup} has only {len(sigs)} past signals in the store; too few to replay')
        res = run_setup(sigs, k, e, d, stop, target, A, paths, seed, cb)
        rep['mode'] = 'setup'
        rep['memory'] = {'setup': setup, 'setup_side': sside, 'setup_filter': sfilt, 'symbols': syms,
                         'signals_used': res['signals_used'], 'signals_total': res['signals_total'],
                         'same_time_of_day': res['same_time_of_day']}
    else:
        lib = []
        for s in syms:
            ss = full if s == symbol else session.sessions(data.read(store, s, 'M5'), s)
            lib += [x for x in ss if x.day < today.day]
        prep = prepare(lib, today, k, d, condition, neighbors)
        res = run(prep, e, d, stop, target, A, paths, block, seed, boot, cost_bps=cb)
        rep['mode'] = 'days'
        rep['memory'] = {'days_in_memory': prep.n_lib, 'similar_days_used': len(prep.pool), 'symbols': syms,
                         'conditioning': prep.condition, 'block_minutes': block * 5}
        rep['today_vs_typical'] = dict(zip(FEATURES, zip(prep.today_f, prep.near_f)))
    rep.update(res)
    if target is not None:
        s_, t_ = risk, abs(target - e)
        rep['textbook_coin_flip_target_first'] = round(s_ / (s_ + t_), 4)
    rep['edge_vs_coin_flip'] = {
        'target_first_pts': round((res['odds']['target_first'] - res['coin_flip_baseline']['odds']['target_first']) * 100, 1),
        'expected_r': _r(res['expected_r'] - res['coin_flip_baseline']['expected_r'])}
    if not today.partial and k < len(today.bars) - 1:
        act = sim.replay(today.bars, k + 1, e, d, stop, target)
        rep['what_actually_happened'] = {
            'note': 'hindsight: this session is already complete in the data',
            'outcome': act['outcome'], 'exit': round(act['exit'], 4),
            'r': _r(sim.r_multiple(e, act['exit'], d, risk, cb)),
            'exit_time_et': session.clock(today.bars[act['k']].m + 5)}
    rep['notes'] = notes(rep)
    rep['disclaimer'] = DISCLAIMER
    return rep


def notes(r):
    out = []
    setup = r['mode'] == 'setup'
    n = r['memory']['signals_used'] if setup else r['memory']['similar_days_used']
    what = 'past signals' if setup else 'past days'
    if n < 30:
        out.append(f'Only {n} {what}: treat every number here as rough.')
    if setup:
        out.append("Part of this history was used to choose the setup's side and filter, which flatters these "
                   "odds; the backtest's out-of-sample result is the cleaner test.")
    if setup and not r['memory']['same_time_of_day']:
        out.append('Fewer than 30 past signals came within an hour of this clock time, so signals from any time '
                   'of day were used; their remaining time was capped at what today has left.')
    lo, hi = r['odds_range_90']['target_first']
    if hi - lo > 0.2:
        out.append('The 90% range on target-first odds is wide; the history is too thin to be precise.')
    if r['stop_in_atr'] < 0.5:
        out.append('The stop is under half a 5-minute ATR away; ordinary noise hits stops that tight most of the time.')
    e = r['edge_vs_coin_flip']['target_first_pts']
    if abs(e) < 3:
        out.append('Target-first odds are within 3 points of a coin flip with the same stop and target: '
                   + ('this setup shows no clear edge with this stop and target.' if setup else
                      'at this time of day and volatility, the history shows no edge in either direction. '
                      'Any edge has to come from the setup itself; try --setup.'))
    elif not setup:
        out.append(f"Past days at this clock time beat the coin flip by {e:+.0f} points, but days mode only knows the "
                   "time of day and volatility: in walk-forward tests its departures from the coin flip did not hold "
                   "up trade by trade. Treat this as noise unless a tested setup (--setup) agrees.")
    elif e > 0:
        out.append(f'The {what} reached the target first {e:.0f} points more often than a coin flip would.')
    else:
        out.append(f'The {what} reached the target first {-e:.0f} points LESS often than a coin flip would.')
    if r['expected_r'] is not None and r['expected_r'] < 0:
        out.append('Average result is negative after costs.')
    if r['bars_left'] < 6:
        out.append('Less than 30 minutes of session left: most outcomes are decided by the close, not the stop or target.')
    return out


def render(r):
    o, b, rd = r['odds'], r['coin_flip_baseline'], r['real_days']
    pc = lambda x: '-' if x is None else f'{x * 100:.0f}%'
    m = r['memory']
    L = [f"TIME MACHINE  {r['symbol']} {r['side']} at {r['entry']} ({r['entry_time_et']} ET, {r['session']})",
         f"stop {r['stop']} ({r['stop_in_atr']} ATR)   "
         + (f"target {r['target']} ({r['target_in_r']}R)   " if r['target'] is not None else 'no target (held to the close)   ')
         + f"{r['bars_left'] * 5} minutes left"]
    if r['mode'] == 'setup':
        L.append(f"memory: {m['signals_used']} past signals of {m['setup']} ({m['setup_side']}, filter {m['setup_filter']}), "
                 f"{r['resamples']:,} resamples for the ranges")
    else:
        L.append(f"{r['paths']:,} paths from {m['similar_days_used']} past days at this clock time "
                 f"({len(m['symbols'])} symbols{', k-nearest filter' if m['conditioning'] == 'knn' else ''})")
    L += ['', '                 target first   stop first   neither by close']
    if r['mode'] == 'days':
        L.append(f"simulated        {pc(o['target_first']):>12}   {pc(o['stop_first']):>10}   {pc(o['neither_by_close']):>16}")
    L += [f"  90% range      {pc(r['odds_range_90']['target_first'][0])}-{pc(r['odds_range_90']['target_first'][1]):<9}"
          f"   {pc(r['odds_range_90']['stop_first'][0])}-{pc(r['odds_range_90']['stop_first'][1])}",
          f"real ({rd['n']:>4})      {pc(rd['odds']['target_first']):>12}   {pc(rd['odds']['stop_first']):>10}   "
          f"{pc(rd['odds']['neither_by_close']):>16}",
          f"coin flip        {pc(b['odds']['target_first']):>12}   {pc(b['odds'].get('stop_first')):>10}   "
          f"{pc(b['odds'].get('neither_by_close')):>16}", '',
          f"expected result {r['expected_r']:+.2f}R (90% range {r['expected_r_range_90'][0]:+.2f} to "
          f"{r['expected_r_range_90'][1]:+.2f}); coin flip {b['expected_r']:+.2f}R",
          f"R spread: 5% {r['r_distribution']['p5']:+.2f}  25% {r['r_distribution']['p25']:+.2f}  "
          f"median {r['r_distribution']['p50']:+.2f}  75% {r['r_distribution']['p75']:+.2f}  95% {r['r_distribution']['p95']:+.2f}"]
    if r['minutes_to_target_median'] or r['minutes_to_stop_median']:
        L.append(f"median time to target {r['minutes_to_target_median']} min, to stop {r['minutes_to_stop_median']} min")
    if r.get('what_actually_happened'):
        a = r['what_actually_happened']
        L.append(f"hindsight: that day actually ended at the {a['outcome']} ({a['r']:+.2f}R, {a['exit_time_et']} ET)")
    L += [''] + [f'- {n}' for n in r['notes']] + ['', r['disclaimer']]
    return '\n'.join(L)


# ---- calibration -----------------------------------------------------------
def calibrate(store, symbols=None, points=300, paths=400, stop_atr=1.0, target_r=2.0, condition='none',
              seed=3, min_history=40, block=BLOCK, entries=None):
    """Walk-forward check that the odds mean what they say. At each test
    point the memory holds only days before that point's date. `entries`
    (optional) is a list of (symbol, day, k, d) to test, e.g. a setup's past
    signals; otherwise random times and directions are drawn."""
    syms = symbols or data.symbols(store, 'M5')
    by = {s: session.sessions(data.read(store, s, 'M5'), s) for s in syms}
    by = {s: v for s, v in by.items() if v}
    days = sorted({x.day for v in by.values() for x in v})
    if len(days) <= min_history + 5:
        raise ValueError(f'need more than {min_history + 5} sessions of history to calibrate')
    allsess = [x for v in by.values() for x in v]
    rnd = random.Random(seed)
    if entries is None:
        late = [x for x in allsess if x.day >= days[min_history]]
        entries = []
        for _ in range(points):
            s = rnd.choice(late)
            entries.append((s.sym, s.day, rnd.randrange(6, 66), rnd.choice((1, -1))))
    lookup = {(x.sym, x.day): x for x in allsess}
    pred_t, pred_b, pred_er, out_t, real_r, base_rate = [], [], [], [], [], []
    for sym, day, k, d in entries:
        s = lookup.get((sym, day))
        if s is None or day < days[min_history] or k >= session.FULL_SESSION - 1:
            continue
        lib = [x for x in allsess if x.day < day]
        A = s.atr[k]
        e = s.bars[k].c
        stop, tgt, risk = resolve_levels(e, d, A, stop_atr=stop_atr, target_r=target_r)
        prep = prepare(lib, s, k, d, condition)
        cb = session.cost_bps(sym)
        m = simulate(prep.pool, k, e, d, stop, tgt, A, paths, block, rnd.randrange(10**9), False, cb)
        bl = simulate(prep.pool, k, e, d, stop, tgt, A, paths, block, rnd.randrange(10**9), True, cb)
        act = sim.replay(s.bars, k + 1, e, d, stop, tgt)
        pred_t.append(m['cnt']['target'] / paths)
        pred_b.append(bl['cnt']['target'] / paths)
        pred_er.append(sum(m['rs']) / paths)
        out_t.append(1 if act['outcome'] == 'target' else 0)
        real_r.append(sim.r_multiple(e, act['exit'], d, risk, cb))
    n = len(out_t)
    clim = sum(pred_b) / n
    bri = stats.brier(pred_t, out_t)
    return {
        'tool': 'time-machine-calibration', 'generated_at': data.now_utc(),
        'test_points': n, 'paths_per_point': paths, 'conditioning': condition,
        'trade': f'{stop_atr} ATR stop, {target_r}R target, entry at a 5-minute close, flat by the close',
        'symbols': sorted(by), 'sessions': len(days), 'first_test_day': str(days[min_history]),
        'target_first': {'predicted_avg': round(sum(pred_t) / n, 4), 'actual_rate': round(sum(out_t) / n, 4),
                         'actual_90': [round(x, 4) for x in stats.wilson(sum(out_t), n)],
                         'coin_flip_predicted_avg': round(clim, 4)},
        'brier': {'time_machine': round(bri, 4), 'coin_flip': round(stats.brier(pred_b, out_t), 4),
                  'skill_vs_coin_flip': round(1 - bri / stats.brier(pred_b, out_t), 4)},
        'reliability': stats.reliability(pred_t, out_t),
        'expected_r': {'predicted_avg': _r(sum(pred_er) / n), 'actual_avg': _r(sum(real_r) / n),
                       'correlation': _r(_corr(pred_er, real_r))},
        'disclaimer': DISCLAIMER,
    }


def _corr(a, b):
    if len(a) < 3:
        return None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def calibrate_setup(store, setup_id, results, stop_atr=1.0, target_r=2.0, min_past=20, setup_dirs=None):
    """Walk-forward check of setup mode on the setup's OUT-OF-SAMPLE signals:
    each test signal is predicted from the setup's signals before its date
    only, with the side and filter the backtest chose on in-sample data."""
    from . import setups as setups_mod, backtest
    ev = next((r for r in results.get('results', []) if r.get('id') == setup_id), None)
    if not ev or not ev.get('side'):
        raise ValueError(f'{setup_id} has no tested variant in the results')
    cut = results['meta']['intraday']['oos_from']
    stp = setups_mod.load(setup_dirs, store, {setup_id})[0]
    sgn = 1 if ev['side'] == 'with' else -1
    allsig = []
    for sym in session.ordered(data.symbols(store, 'M5')):
        for s in session.sessions(data.read(store, sym, 'M5'), sym):
            for i, d in setups_mod.fires(stp, s):
                if i + 1 < len(s.bars) and s.atr[i] > 0 and (
                        ev['filter'] == 'none' or backtest.passes(ev['filter'], backtest.FILTERS, s, i, d)):
                    allsig.append((s, i, d * sgn))
    P, B, O, ER, AR = [], [], [], [], []
    for s, i, dd in allsig:
        if str(s.day) < cut:
            continue
        past = [x for x in allsig if x[0].day < s.day]
        if len(past) < min_past:
            continue
        A, e = s.atr[i], s.bars[i].c
        stop, tgt, risk = resolve_levels(e, dd, A, stop_atr=stop_atr, target_r=target_r)
        cb = session.cost_bps(s.sym)
        r = run_setup(past, i, e, dd, stop, tgt, A, 0, 7, cb)
        act = sim.replay(s.bars, i + 1, e, dd, stop, tgt)
        P.append(r['odds']['target_first']); B.append(r['coin_flip_baseline']['odds']['target_first'])
        O.append(1 if act['outcome'] == 'target' else 0); ER.append(r['expected_r'])
        AR.append(sim.r_multiple(e, act['exit'], dd, risk, cb))
    n = len(O)
    if not n:
        raise ValueError(f'{setup_id}: no out-of-sample signals with enough history before them')
    bt, bc = stats.brier(P, O), stats.brier(B, O)
    return {
        'tool': 'time-machine-calibration', 'mode': 'setup', 'generated_at': data.now_utc(), 'setup': setup_id,
        'variant': f"{ev['side']} · {ev['filter']}", 'test_points': n, 'oos_from': cut,
        'trade': f'{stop_atr} ATR stop, {target_r}R target, entry at the signal close, flat by the close',
        'target_first': {'predicted_avg': round(sum(P) / n, 4), 'actual_rate': round(sum(O) / n, 4),
                         'actual_90': [round(x, 4) for x in stats.wilson(sum(O), n)],
                         'coin_flip_predicted_avg': round(sum(B) / n, 4)},
        'brier': {'time_machine': round(bt, 4), 'coin_flip': round(bc, 4), 'skill_vs_coin_flip': round(1 - bt / bc, 4)},
        'reliability': stats.reliability(P, O),
        'expected_r': {'predicted_avg': _r(sum(ER) / n), 'actual_avg': _r(sum(AR) / n), 'correlation': _r(_corr(ER, AR))},
        'sessions': len({x[0].day for x in allsig}), 'disclaimer': DISCLAIMER,
    }
