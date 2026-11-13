#!/usr/bin/env python3
"""Turn out/results.json into Office DB documents (one JSON file per doc).

usage: publish.py [SUMMARY]

Writes out/db/chart_playbook/<setup id>.json for every setup and, when a
SUMMARY is given, out/db/chart_research/<timestamp>.json (the lab log entry).
Upload them with ArtifactData (batch, file_path per doc). The Studio Floor's
Chart Desk reads chart_playbook into every analyst's prompt and shows both
collections on its Lab tab.
"""
import json, os, sys
import core

SIDE = {'with': 'take the signal', 'fade': 'lean against the signal'}
FILT = {'none': 'no filter', 'vwap': 'only on the signal side of VWAP', 'rvol': 'only on 1.3x normal volume',
        'ppoc': "only beyond yesterday's POC", 'trend': 'only with the structure trend',
        'sma200': 'only on the signal side of the 200-day average'}


def filt_text(f):
    return ' and '.join(FILT[x] if i == 0 else FILT[x].replace('only ', '') for i, x in enumerate(f.split('+')))


def exit_text(e):
    parts = e.split('/')
    if parts[-1].startswith('hold'):
        days = parts[-1][4:]
        stop = parts[0].replace('atr', '')
        tgt = f", target {parts[1].replace('atr', '')} ATR" if len(parts) == 3 else ''
        return f"stop {stop} daily ATR{tgt}, out after {days} days"
    stop = parts[0].replace('atr', '')
    if parts[1] == 'close':
        return f"stop {stop} ATR (5-min), out at the close"
    return f"stop {stop} ATR (5-min), target {parts[1].replace('atr', '')} ATR"


def txt(s):
    if not s or not s.get('n'):
        return 'no trades yet'
    return (f"{s['n']} trades, {s['win_rate'] * 100:.0f}% winners, {s['avg_r']:+.2f}R average, "
            f"profit factor {s['profit_factor']}, t {s['t_stat']}")


def main():
    R = json.load(open(os.path.join(core.HERE, 'out', 'results.json')))
    meta = R['meta']
    root = os.path.join(core.HERE, 'out', 'db')
    os.makedirs(os.path.join(root, 'chart_playbook'), exist_ok=True)
    for r in R['results']:
        fz = r.get('frozen')
        v = fz or r
        doc = {
            'name': r['name'], 'family': r['family'], 'tf': r['tf'], 'rules': r['rules'], 'status': r['status'],
            'variant': (f"{SIDE[v['side']]}; {filt_text(v['filter'])}; {exit_text(v['exit'])}" if 'side' in v else None),
            'variant_code': (f"{v['side']} · {v['filter']} · {v['exit']}" if 'side' in v else None),
            'in_sample_text': txt(r.get('in_sample')), 'oos_text': txt(fz['oos_at_freeze'] if fz else r.get('out_of_sample')),
            'oos_avg_r': (r.get('out_of_sample') or {}).get('avg_r'), 'oos_n': (r.get('out_of_sample') or {}).get('n'),
            'edge_vs_random_oos': r.get('edge_vs_random_oos'), 'symbols_positive': r.get('symbols_positive'),
            'frozen_at': fz['frozen_at'] if fz else None, 'oos_at_freeze': fz.get('oos_at_freeze') if fz else None,
            'forward_text': (f"{txt(r['forward'])} since {fz['frozen_at']} ({r['forward']['verdict']})" if fz else 'not frozen'),
            'variants_tried': r['variants_tried'], 'file': r['file'],
            'lab_run': meta['generated_at'], 'updatedAt': meta['generated_at'],
        }
        json.dump(doc, open(os.path.join(root, 'chart_playbook', f"{r['id']}.json"), 'w'), indent=1)
    if len(sys.argv) > 1:
        os.makedirs(os.path.join(root, 'chart_research'), exist_ok=True)
        rid = meta['generated_at'].replace(':', '').replace('-', '')
        counts = {}
        for r in R['results']:
            counts[r['status']] = counts.get(r['status'], 0) + 1
        json.dump({'at': meta['generated_at'], 'summary': sys.argv[1], 'counts': counts,
                   'intraday_sessions': meta['intraday']['sessions'], 'variants_tried_total': meta['variants_tried_total']},
                  open(os.path.join(root, 'chart_research', f'{rid}.json'), 'w'), indent=1)
        print('research doc', rid)
    print('playbook docs', len(R['results']))


if __name__ == '__main__':
    main()
