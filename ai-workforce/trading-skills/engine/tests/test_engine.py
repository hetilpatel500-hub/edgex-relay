import gzip, json, os, subprocess, sys, tempfile, unittest
from helpers import make_store, HERE
from tskit import (data, session, sim, stats, timemachine as tm, exits, backtest, scanner, risk, journal, news, events,
                   entry, context)

ENGINE = os.path.dirname(HERE)
PLUGIN = os.path.dirname(ENGINE)


class Bars:
    def __init__(self, rows):
        self.bars = [session.Bar(570 + 5 * i, *r) for i, r in enumerate(rows)]


class TestData(unittest.TestCase):
    def test_times(self):
        self.assertEqual(data.norm_time('2026-10-23T19:55:00.000+0000'), '2026-10-23T19:55:00Z')
        self.assertEqual(data.norm_time('2026-10-22'), '2026-10-22T04:00:00Z')
        self.assertEqual(data.norm_time('2026-01-15'), '2026-01-15T05:00:00Z')
        self.assertEqual(data.norm_time(1792784367853), '2026-10-23T19:39:27Z')
        self.assertEqual(data.norm_time('2026-10-23 15:55'), '2026-10-23T19:55:00Z')

    def test_webull_json_and_csv(self):
        d = tempfile.mkdtemp()
        bars = [{'time': f'2026-10-23T13:{30 + 5 * i:02d}:00.000+0000', 'open': '10', 'high': '11', 'low': '9',
                 'close': '10.5', 'volume': '100'} for i in range(5)]
        p = os.path.join(d, 'resp.json')
        json.dump({'result': [{'symbol': 'XYZ', 'result': bars[::-1]}]}, open(p, 'w'))
        rep = data.ingest([p], d)
        self.assertEqual(rep[0]['symbol'], 'XYZ'); self.assertEqual(rep[0]['tf'], 'M5'); self.assertEqual(rep[0]['after'], 5)
        c = os.path.join(d, 'QQQ_1m.csv')
        with open(c, 'w') as fh:
            fh.write('Date,Time,Open,High,Low,Close,Volume\n')
            for i in range(10):
                fh.write(f'2026-10-23,09:{30 + i:02d},{10 + i},{11 + i},{9 + i},{10.5 + i},10\n')
        rep = data.ingest([c], d)
        self.assertEqual(rep[0]['symbol'], 'QQQ'); self.assertEqual(rep[0]['after'], 2)   # 10 one-minute bars -> 2 five-minute bars
        rows = data.read(d, 'QQQ', 'M5')
        self.assertEqual(rows[0][1], 10.0); self.assertEqual(rows[0][4], 14.5); self.assertEqual(rows[0][5], 50.0)

    def test_refuses_coarse(self):
        rows = [(f'2026-10-23T{13 + i}:30:00Z', 1, 1, 1, 1, 1) for i in range(4)]
        with self.assertRaises(ValueError):
            data.classify(rows)


class TestSim(unittest.TestCase):
    def test_stop_first_and_gap(self):
        b = Bars([(100, 100.2, 99.9, 100.1, 1), (100.1, 101.5, 98.5, 100, 1)]).bars
        r = sim.replay(b, 1, 100.0, 1, 99.0, 101.0)
        self.assertEqual(r['outcome'], 'stop'); self.assertEqual(r['exit'], 99.0)
        b = Bars([(100, 100.2, 99.9, 100.1, 1), (98.0, 98.5, 97.5, 98.2, 1)]).bars
        r = sim.replay(b, 1, 100.0, 1, 99.0, 101.0)
        self.assertEqual(r['outcome'], 'stop'); self.assertEqual(r['exit'], 98.0)
        b = Bars([(100, 100.2, 99.9, 100.1, 1), (100.1, 100.3, 99.95, 100.2, 1)]).bars
        self.assertEqual(sim.replay(b, 1, 100.0, 1, 99.0, 101.0)['outcome'], 'close')

    def test_stats(self):
        lo, hi = stats.wilson(30, 100)
        self.assertTrue(0.22 < lo < 0.3 < hi < 0.38)
        self.assertEqual(stats.stats([1, -1, 2])['n'], 3)


class TestTimeMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = make_store(('AAA', 'BBB', 'CCC'), days=90, partial_last=20)

    def test_random_walk_matches_textbook(self):
        r = tm.time_machine(self.store, 'AAA', 'long', stop_atr=1, target_r=2, paths=4000, boot=10)
        self.assertEqual(r['bars_left'], 78 - 20)
        self.assertAlmostEqual(r['odds']['target_first'], 1 / 3, delta=0.06)
        self.assertAlmostEqual(r['odds']['target_first'], r['coin_flip_baseline']['odds']['target_first'], delta=0.04)
        self.assertLessEqual(r['odds_range_90']['target_first'][0], r['odds']['target_first'])
        self.assertIn('disclaimer', r)
        self.assertNotIn('what_actually_happened', r)          # live session: no hindsight

    def test_past_day_has_hindsight_and_no_lookahead(self):
        days = [s.day for s in session.sessions(data.read(self.store, 'BBB', 'M5'), 'BBB')]
        r = tm.time_machine(self.store, 'BBB', 'short', date=str(days[60]), time='11:00', stop_atr=1, target_r=1.5,
                            paths=2000, boot=5)
        self.assertIn('what_actually_happened', r)
        self.assertEqual(r['memory']['days_in_memory'], 60 * 3)   # only days strictly before

    def test_context_time_cutoff(self):
        store = make_store(('SPY', 'QQQ'), days=40, seed=4)
        day = str(session.sessions(data.read(store, 'SPY', 'M5'), 'SPY')[-1].day)
        before = context.context(store, date=day, time='10:20')
        self.assertEqual(before['as_of_et'], '10:20')
        rows = data.read(store, 'SPY', 'M5')
        cut = [i for i, r in enumerate(rows) if data.et(r[0]).strftime('%Y-%m-%d %H:%M') >= day + ' 10:20']
        for i in cut:                                            # rewrite every later bar: nothing may change
            t, o, h, l, c, v = rows[i]
            rows[i] = (t, o * 1.1, h * 1.1, l * 1.1, c * 1.1, v * 3)
        data.write(store, 'SPY', 'M5', rows)
        after = context.context(store, date=day, time='10:20')
        self.assertEqual([x for x in before['indexes'] if x['symbol'] == 'SPY'],
                         [x for x in after['indexes'] if x['symbol'] == 'SPY'])
        self.assertNotEqual(context.context(store, date=day)['as_of_et'], '10:20')

    def test_bad_levels(self):
        with self.assertRaises(ValueError):
            tm.time_machine(self.store, 'AAA', 'long', stop=10_000, paths=100, boot=2)

    def test_calibration_runs(self):
        r = tm.calibrate(self.store, points=40, paths=100, min_history=40)
        self.assertGreater(r['test_points'], 20)
        self.assertTrue(0 <= r['target_first']['actual_rate'] <= 1)

    def test_exits(self):
        r = exits.plan(self.store, 'AAA', 'long', paths=300, levels=False)
        self.assertEqual(r['plans_tested'], 25)
        self.assertIn(r['verdict'], ('positive', 'no_positive_plan'))


class TestBacktestScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = make_store(('AAA', 'BBB'), days=80, seed=4)

    def test_backtest_and_scan(self):
        out = backtest.run(self.store)
        ids = {r['id'] for r in out['results']}
        self.assertIn('round_number_bounce', ids)
        sc = scanner.scan(self.store, results=out, lookback=78)
        self.assertEqual(sc['symbols_scanned'], 2)
        for h in sc['hits']:
            self.assertIn(h['status'], scanner.ORDER)

    def test_entry_checklist(self):
        r = entry.check(self.store, 'AAA', 'long', level=1.0, trigger='break')
        self.assertIn(r['status'], ('WAIT', 'READY', 'CAUTION'))
        r = entry.check(self.store, 'AAA', 'long', stop=10_000)
        self.assertEqual(r['status'], 'INVALID')


class TestSizerJournalNewsEvents(unittest.TestCase):
    def test_size(self):
        r = risk.size(100000, 1, 50, 49, target=52, max_position_pct=100)
        self.assertEqual(r['shares'], 1000); self.assertEqual(r['risk_usd'], 1000.0); self.assertEqual(r['target_r'], 2.0)
        r = risk.size(10000, 1, 50, 49.9)
        self.assertEqual(r['shares'], 50)                      # capped at 25% of the account
        self.assertTrue(any('pattern-day-trader' in w for w in r['warnings']))
        r = risk.size(10000, 1, 50, 49, realized_today=-300, daily_loss_limit_pct=2)
        self.assertTrue(r['halted_by_daily_limit'])

    def test_journal(self):
        f = os.path.join(tempfile.mkdtemp(), 'j.jsonl')
        p = journal.plan(f, 'AAA', 'long', 100, 99, 102, date='2026-01-05', time='10:00')
        journal.close(f, p['id'], 102)
        rep = journal.report(f)
        self.assertEqual(rep['closed'], 1); self.assertEqual(rep['overall']['avg_r'], 2.0)

    def test_news_confirmation(self):
        d = tempfile.mkdtemp()
        wb = os.path.join(d, 'wb.json')
        json.dump({'symbol': 'XYZ', 'data': [
            {'title': 'Acme Robotics wins large defense contract worth $2 billion', 'source': 'WireA',
             'publish_time': '2026-10-20T12:00:00.000+0000', 'related_symbols': ['XYZ']},
            {'title': 'Acme Robotics shares jump on $2 billion defense contract win', 'source': 'WireA',
             'publish_time': '2026-10-20T12:30:00.000+0000', 'related_symbols': ['XYZ']}]}, open(wb, 'w'))
        web = [{'title': 'Defense contract worth $2 billion goes to Acme Robotics', 'url': 'https://www.newsb.example/x',
                'date': '2026-10-20T13:00:00Z'}]
        from datetime import datetime, timezone
        r = news.news('XYZ', [wb], web, days=14, now=datetime(2026, 10, 22, tzinfo=timezone.utc))
        self.assertEqual(len(r['confirmed']), 1)
        self.assertEqual(r['confirmed'][0]['outlets'], ['newsb.example', 'wirea'])
        r = news.news('XYZ', [wb], None, days=14, now=datetime(2026, 10, 22, tzinfo=timezone.utc))
        self.assertEqual(len(r['confirmed']), 0)               # one outlet twice is still one source

    def test_events(self):
        d = tempfile.mkdtemp()
        e = os.path.join(d, 'e.json')
        json.dump([{'fiscal_year': 2026, 'fiscal_period': 4, 'expected_publish_date': '2026-11-03', 'eps_est': '1.5'},
                   {'fiscal_year': 2026, 'fiscal_period': 3, 'expected_publish_date': '2026-08-01', 'eps_est': '1.0',
                    'eps_actual': '1.1'}], open(e, 'w'))
        m = os.path.join(d, 'm.json')
        json.dump({'data': [{'event_name': 'CPI MM', 'publish_time': '2026-11-02T13:30:00.000+0000'},
                            {'event_name': 'Gas Rig Count', 'publish_time': '2026-11-02T18:00:00.000+0000'}]}, open(m, 'w'))
        r = events.calendar({'XYZ': e}, [m], '2026-11-02', 5)
        sev = sorted(f['severity'] for f in r['flags'])
        self.assertEqual(sev, ['high', 'high'])                 # earnings tomorrow + CPI today
        self.assertEqual(r['earnings'][0]['last']['eps_surprise_pct'], 10.0)


class TestPluginSafety(unittest.TestCase):
    def test_hook_blocks_orders(self):
        hook = os.path.join(PLUGIN, 'hooks', 'block_orders.py')
        for name, code in [('mcp__Webull__place_stock_instruction', 2), ('mcp__broker__submit_order', 2),
                           ('mcp__Webull__get_stock_bars', 0), ('Bash', 0)]:
            p = subprocess.run([sys.executable, hook], input=json.dumps({'tool_name': name}), text=True,
                               capture_output=True)
            self.assertEqual(p.returncode, code, name)

    def test_skills_have_frontmatter(self):
        sk = os.path.join(PLUGIN, 'skills')
        names = sorted(os.listdir(sk))
        self.assertEqual(len(names), 12)
        for n in names:
            txt = open(os.path.join(sk, n, 'SKILL.md')).read()
            self.assertTrue(txt.startswith('---\n'), n)
            head = txt.split('---', 2)[1]
            self.assertIn(f'name: {n}', head)
            self.assertIn('description:', head)
            self.assertIn('Educational only', txt)


if __name__ == '__main__':
    unittest.main()
