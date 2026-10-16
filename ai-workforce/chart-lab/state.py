#!/usr/bin/env python3
"""Carry the lab's state between sessions through the Office DB.

Hourly lab runs happen in fresh sessions that can't push to git, so the
frozen variants and the day's tape rows live in the DB collection
`chart_lab_state` until the daily after-close run commits them.

usage:
  state.py pull FROZEN_DOC.json      DB doc chart_lab_state/frozen -> frozen.json
                                     (keeps any setup the DB doesn't have)
  state.py push                      frozen.json -> out/db/chart_lab_state/frozen.json
  state.py tape TAPE_DOC.json        DB doc chart_lab_state/tape-YYYY-MM-DD -> tape/YYYY-MM-DD.jsonl.gz
"""
import gzip, json, os, sys
import core

FROZEN = os.path.join(core.HERE, 'frozen.json')


def unwrap(p):
    d = json.load(open(p))
    return d.get('data', d) if isinstance(d, dict) else d


def main():
    cmd = sys.argv[1]
    if cmd == 'pull':
        doc = unwrap(sys.argv[2])
        cur = json.load(open(FROZEN)) if os.path.exists(FROZEN) else {}
        cur.update(doc.get('frozen', {}))
        json.dump(cur, open(FROZEN, 'w'), indent=1)
        print('frozen setups:', len(cur))
    elif cmd == 'push':
        os.makedirs(os.path.join(core.HERE, 'out', 'db', 'chart_lab_state'), exist_ok=True)
        fz = json.load(open(FROZEN))
        from datetime import datetime, timezone
        json.dump({'frozen': fz, 'updatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')},
                  open(os.path.join(core.HERE, 'out', 'db', 'chart_lab_state', 'frozen.json'), 'w'), indent=1)
        print('wrote out/db/chart_lab_state/frozen.json with', len(fz), 'setups')
    elif cmd == 'tape':
        doc = unwrap(sys.argv[2])
        day = doc['day']
        os.makedirs(os.path.join(core.HERE, 'tape'), exist_ok=True)
        p = os.path.join(core.HERE, 'tape', f'{day}.jsonl.gz')
        old = []
        if os.path.exists(p):
            old = [json.loads(l) for l in gzip.open(p, 'rt')]
        seen = {(r['symbol'], r['at']) for r in old}
        rows = old + [r for r in doc.get('rows', []) if (r['symbol'], r['at']) not in seen]
        with gzip.open(p, 'wt') as fh:
            for r in sorted(rows, key=lambda r: (r['at'], r['symbol'])):
                fh.write(json.dumps(r) + '\n')
        print(p, len(rows), 'rows')


if __name__ == '__main__':
    main()
