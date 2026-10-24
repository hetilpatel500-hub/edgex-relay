#!/usr/bin/env python3
"""Edgex trading skills: one command line for every skill.

  python3 ts.py <command> [options]        (add --json for machine output)

Data: --data DIR (or $TSKIT_DATA, default ./market-data) holding
SYMBOL_M5.csv.gz / SYMBOL_D.csv.gz; fill it with `ingest`.

Analysis only. Nothing here places, stages or routes orders.
Educational only. Not financial advice.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tskit import (data, timemachine, exits, backtest, scanner, entry, context, events, news, risk, journal,
                   review, plan, DISCLAIMER)


def emit(args, obj, text):
    if args.save:
        os.makedirs(os.path.dirname(os.path.abspath(args.save)), exist_ok=True)
        json.dump(obj, open(args.save, 'w'), indent=1, default=str)
    print(json.dumps(obj, indent=1, default=str) if args.json else text)


def load_results(args, only=None):
    if getattr(args, 'results', None):
        return json.load(open(args.results))
    return backtest.run(args.data, args.setups_dir, only=only)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='ts.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data', default=None, help='bar store directory')
    ap.add_argument('--setups-dir', action='append', default=[], help='extra folder of setup files (repeatable)')
    ap.add_argument('--json', action='store_true', help='print JSON instead of text')
    ap.add_argument('--save', help='also write the JSON result to this file')
    sp = ap.add_subparsers(dest='cmd', required=True)

    p = sp.add_parser('ingest', help='merge saved bar files (Webull JSON or CSV) into the store')
    p.add_argument('files', nargs='+'); p.add_argument('--symbol')

    sp.add_parser('symbols', help='list what is in the store')

    p = sp.add_parser('universe', help='watchlist from saved gainers/losers/most-active responses')
    p.add_argument('files', nargs='+'); p.add_argument('--min-price', type=float, default=5.0)
    p.add_argument('--min-volume', type=float, default=1_000_000); p.add_argument('--max', type=int, default=40)

    p = sp.add_parser('scan', help='run every setup over the latest session of each symbol')
    p.add_argument('--symbols', nargs='*'); p.add_argument('--results'); p.add_argument('--lookback', type=int, default=3)
    p.add_argument('--date')

    p = sp.add_parser('backtest', help='in-sample/out-of-sample test of setups, with luck checks')
    p.add_argument('--only', nargs='*'); p.add_argument('--symbols', nargs='*'); p.add_argument('--frozen')
    p.add_argument('--out')

    def trade_args(p, levels=True):
        p.add_argument('--symbol', required=True); p.add_argument('--side', required=True, choices=['long', 'short'])
        p.add_argument('--entry', type=float); p.add_argument('--date'); p.add_argument('--time', help="ET 'HH:MM'")
        if levels:
            p.add_argument('--stop', type=float); p.add_argument('--stop-atr', type=float)
            p.add_argument('--target', type=float); p.add_argument('--target-r', type=float)
            p.add_argument('--target-atr', type=float)

    p = sp.add_parser('time-machine', help='replay the rest of the day thousands of times for one trade')
    trade_args(p)
    p.add_argument('--paths', type=int, default=10000); p.add_argument('--pool', default='all',
                                                                       help='all | same | etfs | stocks')
    p.add_argument('--condition', default='none', choices=['none', 'knn']); p.add_argument('--seed', type=int, default=7)
    p.add_argument('--setup'); p.add_argument('--setup-side', choices=['with', 'fade'])
    p.add_argument('--setup-filter'); p.add_argument('--results'); p.add_argument('--cost-bps', type=float)

    p = sp.add_parser('calibrate', help='walk-forward check that the time machine odds mean what they say')
    p.add_argument('--points', type=int, default=300); p.add_argument('--paths', type=int, default=400)
    p.add_argument('--stop-atr', type=float, default=1.0); p.add_argument('--target-r', type=float, default=2.0)
    p.add_argument('--condition', default='none', choices=['none', 'knn']); p.add_argument('--setup')
    p.add_argument('--mode', default='days', choices=['days', 'setup'],
                   help="days: predict from past days at the clock time; setup: from the setup's past signals")
    p.add_argument('--results'); p.add_argument('--seed', type=int, default=3)

    p = sp.add_parser('exits', help='test many stop/target pairs for one entry')
    trade_args(p, levels=False)
    p.add_argument('--paths', type=int, default=2000); p.add_argument('--setup'); p.add_argument('--results')
    p.add_argument('--no-levels', action='store_true')

    p = sp.add_parser('entry', help='is the trigger in, and does the rest of the picture agree?')
    trade_args(p, levels=False)
    p.add_argument('--setup'); p.add_argument('--level', type=float)
    p.add_argument('--trigger', default='break', choices=['break', 'reclaim', 'bounce'])
    p.add_argument('--stop', type=float); p.add_argument('--results')
    p.add_argument('--ticks'); p.add_argument('--book'); p.add_argument('--flow'); p.add_argument('--events')
    p.add_argument('--min-rvol', type=float, default=1.2)

    p = sp.add_parser('context', help='market regime from the index ETFs, breadth and sectors')
    p.add_argument('--sectors'); p.add_argument('--date')

    p = sp.add_parser('events', help='earnings and economic releases that can move a stock')
    p.add_argument('--earnings', nargs='*', default=[], help='SYMBOL=FILE pairs')
    p.add_argument('--macro', nargs='*', default=[]); p.add_argument('--today'); p.add_argument('--days', type=int, default=5)

    p = sp.add_parser('news', help='group headlines into stories, confirm with 2+ outlets')
    p.add_argument('--symbol'); p.add_argument('--webull', nargs='*', default=[]); p.add_argument('--web')
    p.add_argument('--days', type=int, default=14); p.add_argument('--alias', nargs='*', default=[])

    p = sp.add_parser('size', help='shares from account size and risk %')
    p.add_argument('--account', type=float, required=True); p.add_argument('--risk-pct', type=float, default=1.0)
    p.add_argument('--entry', type=float, required=True); p.add_argument('--stop', type=float, required=True)
    p.add_argument('--target', type=float); p.add_argument('--atr', type=float)
    p.add_argument('--max-position-pct', type=float, default=25.0); p.add_argument('--buying-power', type=float)
    p.add_argument('--lot', type=int, default=1); p.add_argument('--realized-today', type=float, default=0.0)
    p.add_argument('--daily-loss-limit-pct', type=float); p.add_argument('--expected-r', type=float)

    p = sp.add_parser('journal', help='plans, outcomes and the odds check')
    p.add_argument('action', choices=['plan', 'close', 'settle', 'report', 'list'])
    p.add_argument('--file'); p.add_argument('--id'); p.add_argument('--symbol'); p.add_argument('--side')
    p.add_argument('--entry', type=float); p.add_argument('--stop', type=float); p.add_argument('--target', type=float)
    p.add_argument('--exit', type=float); p.add_argument('--exit-time'); p.add_argument('--setup')
    p.add_argument('--date'); p.add_argument('--time'); p.add_argument('--mode', default='paper', choices=['paper', 'real'])
    p.add_argument('--tm', help='time-machine JSON saved with --save, to record its odds'); p.add_argument('--note')
    p.add_argument('--shares', type=int); p.add_argument('--since')

    p = sp.add_parser('review', help='what happened today, measured')
    p.add_argument('--date'); p.add_argument('--journal'); p.add_argument('--scans', nargs='*', default=[])
    p.add_argument('--results'); p.add_argument('--previous'); p.add_argument('--sectors')

    p = sp.add_parser('plan', help='every skill on one trade idea')
    trade_args(p)
    p.add_argument('--account', type=float); p.add_argument('--risk-pct', type=float, default=1.0)
    p.add_argument('--setup'); p.add_argument('--results'); p.add_argument('--level', type=float)
    p.add_argument('--trigger', default='break', choices=['break', 'reclaim', 'bounce'])
    p.add_argument('--events'); p.add_argument('--ticks'); p.add_argument('--book'); p.add_argument('--flow')
    p.add_argument('--journal'); p.add_argument('--paths', type=int, default=10000)

    args = ap.parse_args(argv)
    args.data = data.data_dir(args.data)
    try:
        run(args)
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f'error: {e}', file=sys.stderr)
        sys.exit(2)


def run(a):
    c = a.cmd
    if c == 'ingest':
        rep = data.ingest(a.files, a.data, a.symbol)
        emit(a, rep, '\n'.join(f"{r['symbol']} {r['tf']}: {r['before']} -> {r['after']} bars, {r['first']} .. {r['last']}"
                               for r in rep) or 'nothing ingested')
    elif c == 'symbols':
        out = {tf: data.symbols(a.data, tf) for tf in ('M5', 'D')}
        last = {s: str(data.last_session_date(a.data, s)) for s in out['M5']}
        emit(a, {'store': a.data, **out, 'last_session': last},
             f"store {a.data}\n5-minute: " + ', '.join(f'{s} (to {last[s]})' for s in out['M5']) +
             f"\ndaily: {', '.join(out['D'])}")
    elif c == 'universe':
        r = scanner.universe(a.files, a.min_price, a.min_volume, a.max)
        emit(a, r, '\n'.join([f"WATCHLIST  {r['count']} symbols"] +
                             [f"  {x['symbol']:6s} {x['price']:>9.2f}  {x['change_pct']:+7.2f}%  vol {x['volume']:,.0f}"
                              + (f"  rvol10d {x['relative_volume_10d']:.1f}" if x['relative_volume_10d'] else '')
                              for x in r['symbols']] + ['', r['next']]))
    elif c == 'scan':
        res = json.load(open(a.results)) if a.results else None
        r = scanner.scan(a.data, a.symbols, a.setups_dir, res, a.lookback, date=a.date)
        emit(a, r, scanner.render(r))
    elif c == 'backtest':
        r = backtest.run(a.data, a.setups_dir, a.only, a.symbols, a.frozen, a.out)
        emit(a, r, backtest.render(r))
    elif c == 'time-machine':
        res = load_results(a, [a.setup]) if a.setup else None
        r = timemachine.time_machine(a.data, a.symbol, a.side, a.entry, a.stop, a.target, a.stop_atr, a.target_r,
                                     a.target_atr, a.date, a.time, a.pool, a.condition, None, a.paths,
                                     seed=a.seed, cost=a.cost_bps, setup=a.setup, setup_side=a.setup_side,
                                     setup_filter=a.setup_filter, setup_dirs=a.setups_dir, results=res)
        emit(a, r, timemachine.render(r))
    elif c == 'calibrate':
        ent = None
        if a.mode == 'setup':
            if not a.setup:
                raise ValueError('--mode setup needs --setup ID')
            r = timemachine.calibrate_setup(a.data, a.setup, load_results(a, [a.setup]), a.stop_atr, a.target_r,
                                            setup_dirs=a.setups_dir)
        elif a.setup:
            from tskit import setups as sm, session
            res = load_results(a, [a.setup])
            ev = next((x for x in res['results'] if x['id'] == a.setup), {})
            sgn = -1 if ev.get('side') == 'fade' else 1
            stp = sm.load(a.setups_dir, a.data, {a.setup})[0]
            ent = []
            for sym in session.ordered(data.symbols(a.data)):
                for s in session.sessions(data.read(a.data, sym, 'M5'), sym):
                    for i, d in sm.fires(stp, s):
                        if ev.get('filter', 'none') == 'none' or backtest.passes(ev['filter'], backtest.FILTERS, s, i, d):
                            ent.append((sym, s.day, i, d * sgn))
        if a.mode == 'days':
            r = timemachine.calibrate(a.data, points=a.points, paths=a.paths, stop_atr=a.stop_atr, target_r=a.target_r,
                                      condition=a.condition, seed=a.seed, entries=ent)
        t = r['target_first']
        txt = [f"CALIBRATION ({r.get('mode', 'days')} mode{', ' + r['setup'] if r.get('setup') else ''})  "
               f"{r['test_points']} walk-forward test trades ({r['trade']}), {r['sessions']} sessions",
               f"target first: predicted {t['predicted_avg']:.1%} on average, actual {t['actual_rate']:.1%} "
               f"(90% {t['actual_90'][0]:.1%}-{t['actual_90'][1]:.1%}); coin flip {t['coin_flip_predicted_avg']:.1%}",
               f"Brier score: time machine {r['brier']['time_machine']}, coin flip {r['brier']['coin_flip']} "
               f"(skill {r['brier']['skill_vs_coin_flip']:+.3f}; above 0 means better than the coin flip)",
               f"expected R: predicted {r['expected_r']['predicted_avg']:+.3f}, actual {r['expected_r']['actual_avg']:+.3f}, "
               f"correlation {r['expected_r']['correlation']}", 'reliability:'] + \
              [f"  predicted {x['bin']:>8}: n {x['n']:4d}, predicted {x['predicted']:.0%}, actual {x['observed']:.0%} "
               f"(90% {x['observed_90'][0]:.0%}-{x['observed_90'][1]:.0%})" for x in r['reliability']] + ['', r['disclaimer']]
        emit(a, r, '\n'.join(txt))
    elif c == 'exits':
        res = load_results(a, [a.setup]) if a.setup else None
        r = exits.plan(a.data, a.symbol, a.side, a.entry, a.date, a.time, paths=a.paths, levels=not a.no_levels,
                       setup=a.setup, setup_dirs=a.setups_dir, results=res)
        emit(a, r, exits.render(r))
    elif c == 'entry':
        res = load_results(a, [a.setup]) if a.setup else None
        r = entry.check(a.data, a.symbol, a.side, a.setup, a.level, a.trigger, a.stop, res, a.setups_dir, a.ticks, a.book,
                        a.flow, a.events, a.min_rvol, date=a.date, time=a.time)
        emit(a, r, entry.render(r))
    elif c == 'context':
        r = context.context(a.data, a.sectors, a.date)
        emit(a, r, context.render(r))
    elif c == 'events':
        ern = dict(x.split('=', 1) for x in a.earnings)
        r = events.calendar(ern, a.macro, a.today, a.days)
        emit(a, r, events.render(r))
    elif c == 'news':
        r = news.news(a.symbol, a.webull, a.web, a.days, a.data, aliases=a.alias)
        emit(a, r, news.render(r))
    elif c == 'size':
        r = risk.size(a.account, a.risk_pct, a.entry, a.stop, a.target, a.atr, a.max_position_pct, a.buying_power, a.lot,
                      a.realized_today, a.daily_loss_limit_pct, a.expected_r)
        emit(a, r, risk.render(r))
    elif c == 'journal':
        f = journal.path(a.file)
        if a.action == 'plan':
            tmj = json.load(open(a.tm)) if a.tm else None
            r = journal.plan(f, a.symbol, a.side, a.entry, a.stop, a.target, a.setup, a.date, a.time, tmj, a.note,
                             a.mode, a.shares)
            emit(a, r, f"recorded {r['id']} ({r['mode']}) in {f}")
        elif a.action == 'close':
            r = journal.close(f, a.id, a.exit, a.exit_time, a.note)
            emit(a, r, f"closed {r['id']}: {r['outcome']}, {r['r']:+.2f}R")
        elif a.action == 'settle':
            r = journal.settle(f, a.data)
            emit(a, r, journal.render(r))
        elif a.action == 'list':
            recs = journal.records(f)
            emit(a, recs, '\n'.join(f"{r['id']:24s} {r['status']:6s} {r['side']:5s} {r['symbol']:6s} entry {r['entry']} "
                                    f"stop {r['stop']} target {r['target']}" +
                                    (f" -> {r.get('outcome')} {r.get('r'):+.2f}R" if r['status'] == 'closed' else '')
                                    for r in recs) or 'journal is empty')
        else:
            r = journal.report(f, a.since)
            emit(a, r, journal.render(r))
    elif c == 'review':
        res = json.load(open(a.results)) if a.results else None
        prev = json.load(open(a.previous)) if a.previous else None
        r = review.review(a.data, a.date, a.journal, a.scans, res, prev, a.sectors)
        emit(a, r, review.render(r))
    elif c == 'plan':
        res = load_results(a, [a.setup]) if a.setup else None
        r = plan.trade_plan(a.data, a.symbol, a.side, a.entry, a.stop, a.target, a.stop_atr, a.target_r, a.account,
                            a.risk_pct, a.setup, res, a.level, a.trigger, a.events, a.ticks, a.book, a.flow, a.date,
                            a.time, a.journal, a.setups_dir, a.paths, a.target_atr)
        emit(a, r, plan.render(r))


if __name__ == '__main__':
    main()
