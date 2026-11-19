#!/usr/bin/env python3
"""Exit study: trailing stop on the protected level vs the frozen fixed-ATR exit.
Added 2026-09-28 by risk-manager: next open line of the research queue in
ai-workforce/chart-lab/README.md ("Exit study: trailing stop on the protected
level vs fixed ATR exits"). This is not a new setup: it asks whether a
different EXIT beats the exit the lab already chose, and lab.py's exit menu
(core.EXITS) is part of the fixed method -- never edited to chase a result,
same reasoning the risk-manager used for the time-of-day-filter study when
the filter engine had no time-of-day option. So this script sits outside
setups/ (lab.py's loader only globs setups/*.py; this file is never picked
up) and runs its own honest apples-to-apples comparison using the exact
signals, side, filter and initial risk of an already-frozen setup whose
whole thesis IS the protected level: protected_hold (frozen 2026-09-25,
fade . rvol . 1atr/close).

Two exits, same entries (next bar's open), same initial risk (1 ATR, so the
first bar of risk is identical), same cost model, same flat-at-close rule,
same stop-wins-on-a-tie rule as core.trade:
  frozen      the exact frozen exit: fixed stop at 1 ATR, no target, flat
              at the close (core.EXITS['1atr/close'], via core.trade).
  trail_prot  same initial 1 ATR stop, then on every later bar the stop is
              tightened (never loosened) to the session's own protected
              level (s.prot) if that level has moved further into profit
              than the current stop; still no target, flat at the close.
Same in-sample/out-of-sample date split as lab.py (first 70% / last 30%
of dates). Never rescored to make a result look better.
"""
import json, os, sys
import core
from setups import intraday

HERE = core.HERE


def trade_trail(s, i, td):
    """Same shape as core.trade, but the stop trails to s.prot after entry.
    A protected level is only a valid trailing stop on the side of price it
    actually sits: below price for a long, above price for a short (that is
    what "the swing that must hold for the trend to stay intact" means). A
    candidate that has crossed to the wrong side of the current bar's own
    close (e.g. a long's "protection" now above price) is stale structure
    and skipped rather than applied, so the stop can never be dragged to an
    already-triggered level."""
    b = s.bars
    if i + 1 >= len(b):
        return None
    e = b[i + 1].o
    risk = 1.0 * s.atr[i]
    if risk <= 0:
        return None
    stop = e - td * risk
    x = b[-1].c
    for k in range(i + 1, len(b)):
        y = b[k]
        p = s.prot[k]
        if p is not None and (td * (y.c - p) > 0):
            stop = max(stop, p) if td == 1 else min(stop, p)
        if (y.l <= stop) if td == 1 else (y.h >= stop):
            x = stop
            break
    cost = core.COST_BPS[s.sym] / 1e4 * e
    return ((x - e) * td - cost) / risk


def main():
    frozen = json.load(open(os.path.join(HERE, 'frozen.json')))
    fz = frozen['protected_hold']
    assert fz['filter'] == 'rvol', f'frozen filter changed: {fz}'  # reuse the frozen filter either way

    sess = {sym: core.sessions(sym) for sym in core.UNIVERSE}
    all_days = sorted({x.day for v in sess.values() for x in v})
    cut = all_days[int(len(all_days) * 0.7)]

    rows = {'with': [], 'fade': []}  # side -> [(day, sym, r_fixed, r_trail)]
    for sym in core.UNIVERSE:
        for s in sess[sym]:
            for i, d in intraday.protected_hold(s):
                if (s.rvol[i] or 0) < 1.3:      # the frozen filter: rvol
                    continue
                for side, td in (('with', d), ('fade', -d)):
                    r_fixed = core.trade(s, i, td, 1.0, None)   # the frozen exit: 1atr/close
                    r_trail = trade_trail(s, i, td)
                    if r_fixed is None or r_trail is None:
                        continue
                    rows[side].append((s.day, sym, r_fixed, r_trail))

    def summarize(rs, idx):
        return core.stats([r[idx] for r in rs])

    result = {'setup_reused': 'protected_hold', 'filter': 'rvol', 'frozen_side': fz['side'],
              'oos_from': str(cut), 'by_side': {}}
    for side, rs in rows.items():
        is_rows = [r for r in rs if r[0] < cut]
        oos_rows = [r for r in rs if r[0] >= cut]
        result['by_side'][side] = {
            'n_signals': len(rs),
            'in_sample': {'fixed_1atr_close': summarize(is_rows, 2), 'trail_protected': summarize(is_rows, 3)},
            'out_of_sample': {'fixed_1atr_close': summarize(oos_rows, 2), 'trail_protected': summarize(oos_rows, 3)},
        }
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(result, open(os.path.join(HERE, 'out', 'exit_study_protected_trail.json'), 'w'), indent=1, default=str)
    print(json.dumps(result, indent=1, default=str))


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    main()
