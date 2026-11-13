#!/usr/bin/env python3
"""SPY 0DTE backtest with the owner's own trade (owner, 2026-09-29: "don't
try to fix my risk to reward ratio ... use this information and try again
with our backtesting"). Analysis only: nothing here places, stages or
suggests orders.

THE OWNER'S TRADE (kept exactly; from their example ticket)
  Same-day-expiry SPY option, 2 contracts, bought around $0.93 at the ask.
  Stop-loss when the option trades 27% below the fill (0.93 -> 0.68).
  Take-profit limit at 2.688x the fill (0.93 -> 2.50, +169%).
  If neither is hit, the option is held to the close and settles at
  intrinsic value (the order is GTC on a contract expiring that day).
  Account $1,100-1,300; results are shown per trade and on $1,200.

WHAT OUR RESEARCH DECIDES: only WHEN to enter and WHICH WAY (call for up,
put for down). The stop, target, size and premium never change.

OPTION PRICES ARE MODELLED, NOT REAL QUOTES. The Webull tools used here have
no historical option prices, so each 5-minute bar's option value is
Black-Scholes (r = 0) on SPY's price with the time left to the 16:00 close.
Volatility = 1.25 x SPY's intraday realised volatility over the previous 10
sessions. The 1.25 comes from the owner's ticket: SPY 765.61, 768 call
expiring that day at 0.93, which implies about 9.8% against 7.8% realised.
Results are re-run at 1.0x and 1.5x to show how much this assumption matters.

CONTRACT CHOICE  At entry, the out-of-the-money $1 strike whose modelled price
is closest to $0.93; skipped if that price is outside $0.60-$1.40 (not the
owner's usual contract) or after 15:30.

FILLS AND COSTS (conservative)  Buy at model + $0.01. Each bar, the option's
best and worst values come from SPY's high and low with the bar's closing time
left. If the worst touches the stop, sell at the stop - $0.01, or at the
bar-open value - $0.01 if it opened past the stop (a gap). If the best reaches
the target, sell at the target. If both happen in one bar, the stop is
assumed first. Fees $0.21 per side.

R = dollar P&L / planned risk (27% of the premium paid, about $50 on 2 x 0.93).

CANDIDATES (all fixed before this run)
  I*  every intraday setup from the hunt (54): side (with/fade) and filter
      picked on TRAIN, first qualifying signal of each session
  D*  every daily setup (11) and D2 (daily vote >= 2): the next session,
      buy at 9:35 (side picked on TRAIN)
  REF_CALL / REF_PUT  a call / put at 9:35 every day (no setup)
METHOD  as spy_hunt.py: sessions split 50/25/25 (TRAIN / VALIDATE / TEST);
TEST beaten against random entries with the same direction, filter and
bracket (300 runs); same A+/A/B/C grades on R; Bonferroni over candidates.

usage: python3 odte.py [--vol 1.25]    writes results[_volX].json
"""
import json, math, os, random, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'aplus_hunt'))
import hunt  # noqa: E402
import core, lab  # noqa: E402

core.HERE = os.path.join(hunt.LAB, 'studies', 'data_spy')
core.UNIVERSE = ['SPY']
VOL_MULT = float(sys.argv[sys.argv.index('--vol') + 1]) if '--vol' in sys.argv else 1.25
PREMIUM, CONTRACTS, STOP_PCT, TGT_MULT = 0.93, 2, 0.27, 2.50 / 0.93
SLIP, FEE = 0.01, 0.21
MIN_TRAIN = 40
ACCOUNT = 1200
YEAR_MIN = 390 * 252


def N(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def bs(S, K, mins, sg, cp):
    if mins <= 0:
        return max(0.0, (S - K) if cp > 0 else (K - S))
    T = mins / YEAR_MIN
    v = sg * math.sqrt(T)
    d1 = (math.log(S / K) + 0.5 * v * v) / v
    if cp > 0:
        return S * N(d1) - K * N(d1 - v)
    return K * N(v - d1) - S * N(-d1)


def attach_vol(sess):
    rets = []
    for s in sess:
        tail = rets[-780:]
        rv = math.sqrt(sum(r * r for r in tail) / len(tail)) * math.sqrt(78 * 252) if len(tail) >= 390 else None
        s.iv = max(0.06, rv * VOL_MULT) if rv else None
        rets.extend(math.log(b.c / a.c) for a, b in zip(s.bars, s.bars[1:]))


def sim(s, j, cp):
    """Buy the owner's contract at the open of bar j (direction cp = +1 call,
    -1 put). Returns dict(pnl, R, premium, strike, exit, why) or None."""
    if s.iv is None or j >= len(s.bars):
        return None
    b = s.bars
    m0 = b[j].m
    if m0 > 930:
        return None
    S0, left = b[j].o, 960 - m0
    base = math.floor(S0) + 1 if cp > 0 else math.ceil(S0) - 1
    best = None
    for k in range(0, 40):
        K = base + k if cp > 0 else base - k
        p = bs(S0, K, left, s.iv, cp)
        if best is None or abs(p - PREMIUM) < abs(best[1] - PREMIUM):
            best = (K, p)
        if p < PREMIUM * 0.5:
            break
    K, p = best
    if not 0.60 <= p <= 1.40:
        return None
    fill = p + SLIP
    stop, tgt = fill * (1 - STOP_PCT), fill * TGT_MULT
    exit_px, why = None, 'expiry'
    for k in range(j, len(b)):
        x = b[k]
        t_end = 960 - (x.m + 5)
        hi_v = bs(x.h if cp > 0 else x.l, K, t_end, s.iv, cp)
        lo_v = bs(x.l if cp > 0 else x.h, K, t_end, s.iv, cp)
        open_v = bs(x.o, K, 960 - x.m, s.iv, cp) if k > j else fill
        if lo_v <= stop:
            exit_px, why = (min(stop, open_v) if k > j else stop) - SLIP, 'stop'
            break
        if hi_v >= tgt:
            exit_px, why = (max(tgt, open_v) if k > j and open_v >= tgt else tgt), 'target'
            break
    if exit_px is None:
        exit_px = max(0.0, bs(b[-1].c, K, 0, s.iv, cp) - (SLIP if (b[-1].c - K) * cp > 0 else 0))
    exit_px = max(0.0, exit_px)
    pnl = (exit_px - fill) * 100 * CONTRACTS - 2 * FEE
    risk = fill * STOP_PCT * 100 * CONTRACTS
    return dict(pnl=pnl, R=pnl / risk, premium=round(fill, 2), strike=K, exit=round(exit_px, 2), why=why)


def stats(tr):
    s = core.stats([t['R'] for t in tr])
    if tr:
        pn = [t['pnl'] for t in tr]
        cum = peak = dd = 0.0
        for p in pn:
            cum += p; peak = max(peak, cum); dd = max(dd, peak - cum)
        streak = mx = 0
        for p in pn:
            streak = streak + 1 if p < 0 else 0; mx = max(mx, streak)
        s.update(total_usd=round(sum(pn), 2), avg_usd=round(sum(pn) / len(pn), 2), max_dd_usd=round(dd, 2),
                 longest_losing_streak=mx,
                 targets=sum(1 for t in tr if t['why'] == 'target'), stops=sum(1 for t in tr if t['why'] == 'stop'),
                 expiries=sum(1 for t in tr if t['why'] == 'expiry'),
                 avg_premium=round(sum(t['premium'] for t in tr) / len(tr), 3))
    return s


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def main():
    t0 = time.time()
    rng = random.Random(29)
    D = core.Daily('SPY')
    sess = core.sessions('SPY')
    hunt.attach_d200({'SPY': sess}, {'SPY': D})
    attach_vol(sess)
    sess = [s for s in sess if s.iv is not None]
    days = [s.day for s in sess]
    c1, c2 = days[int(len(days) * .5)], days[int(len(days) * .75)]
    by_day = {s.day: s for s in sess}
    sides = lab.SIDES

    # random pool for matched baselines: every test session, bars 1..66, both directions
    pool = {}
    for s in sess:
        if s.day < c2:
            continue
        for i in range(1, 66):
            for d in (1, -1):
                r = sim(s, i + 1, d)
                if r:
                    pool.setdefault(d, []).append((s, i, r))

    open_pool = {d: [r for r in (sim(s, 1, d) for s in sess if s.day >= c2) if r] for d in (1, -1)}
    cands = []
    # intraday setups
    for st in [x for x in hunt.SETUPS if x['tf'] == 'M5']:
        raw = []
        for s in sess:
            for i, d in st['detect'](s):
                ok = [c for c in lab.COMBOS if lab.passes(c, lab.FILTERS, s, i, d)]
                res = {sd: sim(s, i + 1, d * m) for sd, m in sides}
                raw.append(dict(day=s.day, i=i, d=d, ok=ok, res=res, s=s))
        cands.append(('I', st['id'], st['name'], st['rules'], raw, lab.COMBOS))
    # daily setups and D2 -> next session at 9:35
    votes = {}
    dsetups = [x for x in hunt.SETUPS if x['tf'] == 'D']
    pos_next = {}
    for k, dy in enumerate(D.day):
        nxt = next((s for s in [by_day.get(d) for d in D.day[k + 1:k + 2]] if s), None)
        if nxt:
            pos_next[k] = nxt
    for st in dsetups:
        raw = []
        for i, d in st['detect'](D):
            votes.setdefault(i, {})[st['id']] = d
            s = pos_next.get(i)
            if s:
                raw.append(dict(day=s.day, i=0, d=d, ok=['none'], res={sd: sim(s, 1, d * m) for sd, m in sides}, s=s))
        cands.append(('D', st['id'], st['name'], st['rules'], raw, ['none']))
    raw = []
    for i, v in votes.items():
        net = sum(v.values())
        s = pos_next.get(i)
        if s and abs(net) >= 2:
            d = 1 if net > 0 else -1
            raw.append(dict(day=s.day, i=0, d=d, ok=['none'], res={sd: sim(s, 1, d * m) for sd, m in sides}, s=s))
    cands.append(('D', 'D2', 'Daily vote >= 2 (D2)', 'Two or more daily setups agree (net vote >= 2): next session at 9:35.', raw, ['none']))
    for name, d in (('REF_CALL', 1), ('REF_PUT', -1)):
        raw = [dict(day=s.day, i=0, d=d, ok=['none'], res={'with': sim(s, 1, d), 'fade': sim(s, 1, -d)}, s=s) for s in sess]
        cands.append(('R', name, f'{"Call" if d > 0 else "Put"} at 9:35 every day', 'No setup: reference.', raw, ['none']))

    rows = []
    for kind, cid, name, rules, raw, combos in cands:
        best = None
        for c in combos:
            for sd, _ in sides:
                seen, tr = set(), []
                for x in sorted(raw, key=lambda x: (x['day'], x['i'])):
                    if c not in x['ok'] or x['day'] in seen or x['res'][sd] is None:
                        continue
                    seen.add(x['day']); tr.append(x)
                trn = [x['res'][sd]['R'] for x in tr if x['day'] < c1]
                if len(trn) >= MIN_TRAIN:
                    a = sum(trn) / len(trn)
                    if best is None or a > best[0]:
                        best = (a, c, sd, tr)
        row = dict(kind=kind, id=cid, name=name, rules=rules, signals=len(raw))
        if best is None:
            row.update(grade='C', note=f'fewer than {MIN_TRAIN} training trades'); rows.append(row); continue
        _, c, sd, tr = best
        T = [dict(x['res'][sd], day=str(x['day'])) for x in tr]
        TR = stats([t for t, x in zip(T, tr) if x['day'] < c1])
        VA = stats([t for t, x in zip(T, tr) if c1 <= x['day'] < c2])
        test = [(t, x) for t, x in zip(T, tr) if x['day'] >= c2]
        TE = stats([t for t, _ in test])
        sgn = 1 if sd == 'with' else -1
        means = []
        for _ in range(300):
            rs = []
            for t, x in test:
                dd = x['d'] * sgn
                if kind != 'I':
                    rs.append(rng.choice(open_pool[dd])['R']); continue
                cand = pool.get(dd, [])
                for _t in range(30):
                    s, i, r = rng.choice(cand)
                    if lab.passes(c, lab.FILTERS, s, i, x['d']):
                        rs.append(r['R']); break
            if rs:
                means.append(sum(rs) / len(rs))
        mb = sum(means) / len(means) if means else None
        row.update(side=sd, filter=c, train=TR, validate=VA, test=TE,
                   matched_baseline=round(mb, 3) if mb is not None else None,
                   edge_vs_matched=round(TE['avg_r'] - mb, 3) if mb is not None and TE.get('n') else None,
                   p_vs_matched=(sum(1 for m in means if m >= TE.get('avg_r', 0)) / len(means)) if means and TE.get('n') else None,
                   full=stats(T), trades=T)
        rows.append(row)
    K = sum(1 for r in rows if r.get('test', {}).get('n', 0) >= 30)
    for r in rows:
        if 'test' not in r:
            continue
        TR, VA, TE = r['train'], r['validate'], r['test']
        t = TE.get('t_stat') or 0
        padj = min(1.0, (1 - phi(t) if TE.get('n', 0) >= 2 else 1.0) * max(K, 1))
        r['p_bonferroni'] = round(padj, 5)
        ok_n = TR.get('n', 0) >= MIN_TRAIN and VA.get('n', 0) >= 30 and TE.get('n', 0) >= 30
        beats = r['edge_vs_matched'] is not None and r['edge_vs_matched'] >= 0.10 and (r['p_vs_matched'] or 1) < 0.05
        if (ok_n and TR['avg_r'] >= 0.05 and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.10
                and (TE.get('profit_factor') or 0) >= 1.3 and t >= 2.0 and beats and padj < 0.05):
            g = 'A+'
        elif (ok_n and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.05 and t >= 1.5 and (TE.get('profit_factor') or 0) >= 1.15
              and (r['edge_vs_matched'] or 0) > 0):
            g = 'A'
        elif VA.get('n', 0) and TE.get('n', 0) and VA['avg_r'] > 0 and TE['avg_r'] > 0:
            g = 'B'
        else:
            g = 'C'
        r['grade'] = g
    order = {'A+': 0, 'A': 1, 'B': 2, 'C': 3}
    rows.sort(key=lambda r: (order[r['grade']], -(r.get('test', {}).get('avg_r') or -9)))
    pool_all = [r for v in pool.values() for _, _, r in v]
    meta = {'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'vol_mult': VOL_MULT,
            'sessions': len(sess), 'first': str(days[0]), 'last': str(days[-1]), 'validate_from': str(c1), 'test_from': str(c2),
            'bracket': {'premium': PREMIUM, 'contracts': CONTRACTS, 'stop_pct': STOP_PCT, 'target_mult': round(TGT_MULT, 3)},
            'candidates': len(rows), 'graded': K, 'grade_counts': {g: sum(1 for r in rows if r['grade'] == g) for g in order},
            'random_entry_test': stats(pool_all), 'runtime_s': round(time.time() - t0, 1)}
    out = 'results.json' if VOL_MULT == 1.25 else f'results_vol{VOL_MULT}.json'
    json.dump({'meta': meta, 'results': rows}, open(os.path.join(HERE, out), 'w'), indent=1, default=str)
    for r in rows:
        if 'test' not in r:
            continue
        T = r['test']
        print(f"{r['grade']:2s} {r['id']:26s} {r['kind']} [{r['side']}|{r['filter']}] TR {r['train']['n']:4d} {r['train']['avg_r']:+.3f} "
              f"VA {r['validate'].get('n', 0):3d} {r['validate'].get('avg_r', 0):+.3f} TE {T.get('n', 0):3d} {T.get('avg_r', 0):+.3f} "
              f"win {T.get('win_rate')} ${T.get('avg_usd')}/tr tot ${T.get('total_usd')} dd ${T.get('max_dd_usd')} "
              f"t {T.get('t_stat')} vsM {r['edge_vs_matched']} p {r['p_vs_matched']}")
    print(json.dumps(meta, indent=1, default=str))


if __name__ == '__main__':
    main()
