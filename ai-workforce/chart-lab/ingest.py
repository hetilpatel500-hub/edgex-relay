#!/usr/bin/env python3
"""Merge saved Webull bar responses into the lab's data store.

usage: ingest.py TIMEFRAME FILE [FILE ...]      (TIMEFRAME: D or M5)

Accepts both shapes the Webull connector returns: get_stock_bars
({"result": [{"symbol", "result": [bars]}]}) and get_stock_bars_single
([bars]). Bars are stored exactly as returned (prices as strings are only
parsed to floats), one gzip CSV per symbol and timeframe:
data/<SYMBOL>_<TF>.csv.gz with columns t,o,h,l,c,v (t in UTC, ISO 8601).
Duplicate timestamps keep the newest copy; nothing else is changed.
"""
import csv, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rows_of(obj):
    if isinstance(obj, dict) and isinstance(obj.get('result'), list):
        for g in obj['result']:
            for b in g.get('result', []):
                yield g['symbol'], b
    elif isinstance(obj, list):
        for b in obj:
            yield b['symbol'], b


def path(sym, tf):
    return os.path.join(HERE, 'data', f'{sym}_{tf}.csv.gz')


def load(sym, tf):
    p = path(sym, tf)
    if not os.path.exists(p):
        return {}
    with gzip.open(p, 'rt') as fh:
        return {r['t']: r for r in csv.DictReader(fh)}


def main():
    tf, files = sys.argv[1], sys.argv[2:]
    new = {}
    for f in files:
        for sym, b in rows_of(json.load(open(f))):
            t = b['time'].replace('.000+0000', 'Z')
            new.setdefault(sym, {})[t] = {'t': t, 'o': b['open'], 'h': b['high'], 'l': b['low'], 'c': b['close'], 'v': b['volume']}
    for sym, bars in sorted(new.items()):
        cur = load(sym, tf); before = len(cur); cur.update(bars)
        rows = [cur[k] for k in sorted(cur)]
        with gzip.open(path(sym, tf), 'wt', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['t', 'o', 'h', 'l', 'c', 'v']); w.writeheader(); w.writerows(rows)
        print(f'{sym} {tf}: {before} -> {len(rows)} bars, {rows[0]["t"]} .. {rows[-1]["t"]}')


if __name__ == '__main__':
    main()
