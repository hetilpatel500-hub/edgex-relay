from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from conftest import make_day

from tradekit import montecarlo as mc
from tradekit.session import Session


def bank_from(days_closes, interval=5, **kw):
    frames = [make_day(date(2026, 9, 1) + timedelta(days=i), c, interval, **kw) for i, c in enumerate(days_closes)]
    return mc.build_bank(pd.concat(frames), Session(), interval)


def flat_plus(step, n=78, start=100.0):
    return start * np.exp(np.arange(1, n + 1) * step)


def test_plan_validation():
    with pytest.raises(ValueError):
        mc.TradePlan("long", 100, 101, [])
    with pytest.raises(ValueError):
        mc.TradePlan("short", 100, 99, [])
    with pytest.raises(ValueError):
        mc.TradePlan("long", 100, 99, [mc.Target(99.5, 1.0)])
    with pytest.raises(ValueError):
        mc.TradePlan("long", 100, 99, [mc.Target(101, 0.7), mc.Target(102, 0.7)])
    p = mc.TradePlan("short", 100, 101, [mc.Target(98, 1.0)])
    assert p.r_of(98) == pytest.approx(2.0)


def test_build_bank_shapes_and_returns():
    bank = bank_from([flat_plus(0.001)] * 3)
    assert bank.ro.shape == (3, 78)
    assert bank.valid.all()
    assert np.allclose(bank.rc[:, 1:], 0.001)


def test_steady_uptrend_hits_long_target_and_short_stop():
    bank = bank_from([flat_plus(0.0005)] * 10)
    long_ = mc.TradePlan("long", 100, 99, [mc.Target(101, 1.0)])
    res = mc.simulate(bank, long_, 10, 77, n_sims=500, seed=1)
    s = mc.summarize(res)
    assert s["p_target"] == 1.0 and s["p_stop"] == 0.0
    assert s["expected_r"] == pytest.approx(1.0)
    short = mc.TradePlan("short", 100, 101, [mc.Target(99, 1.0)], slippage=0.0)
    s = mc.summarize(mc.simulate(bank, short, 10, 77, n_sims=500, seed=1))
    assert s["p_stop"] == 1.0
    assert s["expected_r"] == pytest.approx(-1.0)


def test_outcome_shares_sum_to_one_and_replay_uses_each_day():
    rng = np.random.default_rng(0)
    days = [100 * np.exp(np.cumsum(rng.normal(0, 0.002, 78))) for _ in range(30)]
    bank = bank_from(days)
    plan = mc.TradePlan("long", 100, 99.6, [mc.Target(100.4, 0.5), mc.Target(100.8, 0.5)], breakeven_after=0)
    s = mc.summarize(mc.simulate(bank, plan, 12, 77, n_sims=3000, seed=2))
    total = s["p_target"] + s["p_stop"] + s["p_partial_then_stop"] + s["p_time_exit"]
    assert total == pytest.approx(1.0)
    rep = mc.simulate(bank, plan, 12, 77, mode="replay")
    assert rep.n == 30


def test_gap_through_stop_fills_at_open():
    # every bar opens 3% lower than the prior close, far through a 1% stop
    n = 78
    closes = 100 * 0.97 ** np.arange(1, n + 1)
    opens = np.r_[100.0, closes[:-1]] * 0.0 + closes  # open equals the gapped-down close
    bank = bank_from([closes] * 5, opens=opens)
    plan = mc.TradePlan("long", 100, 99, [mc.Target(102, 1.0)])
    res = mc.simulate(bank, plan, 1, 77, n_sims=100, seed=3)
    assert (res.outcome == mc.STOP).all()
    assert res.r.max() < -2.5  # filled at the 97 open, not at 99


def test_ambiguous_bar_resolution():
    # bar 1 touches both 99 stop and 101 target
    base = np.full(78, 100.0)
    up_bar = dict(opens=base, highs=np.r_[100, 101.5, np.full(76, 100.05)], lows=np.r_[100, 98.5, np.full(76, 99.95)])
    closes_up = base.copy(); closes_up[1] = 100.5
    closes_dn = base.copy(); closes_dn[1] = 99.5
    plan = mc.TradePlan("long", 100, 99, [mc.Target(101, 1.0)])

    bank_up = bank_from([closes_up] * 3, **up_bar)
    res = mc.simulate(bank_up, plan, 1, 77, n_sims=50, seed=0)
    assert (res.outcome == mc.STOP).all()  # up bar: low came first
    bank_dn = bank_from([closes_dn] * 3, **up_bar)
    res = mc.simulate(bank_dn, plan, 1, 77, n_sims=50, seed=0)
    assert (res.outcome == mc.TARGET).all()  # down bar: high came first
    res = mc.simulate(bank_dn, plan, 1, 77, n_sims=50, seed=0, ambiguous="worst")
    assert (res.outcome == mc.STOP).all()
    assert res.ambiguous_bars == 50


def test_breakeven_after_first_target_then_reversal():
    # rally to 101 then fall back to 99.5: half sells at +1R, rest stops at breakeven
    closes = np.r_[np.linspace(100.2, 101.2, 10), np.linspace(101.0, 99.5, 20), np.full(48, 99.5)]
    bank = bank_from([closes] * 4, spread=0.01)
    plan = mc.TradePlan("long", 100, 99, [mc.Target(101, 0.5), mc.Target(103, 0.5)], breakeven_after=0,
                        slippage=0.0)
    res = mc.simulate(bank, plan, 0, 77, n_sims=200, seed=0)
    assert (res.outcome == mc.PARTIAL_STOP).all()
    assert res.r == pytest.approx(np.full(200, 0.5), abs=1e-6)


def test_runner_with_all_targets_counts_as_target():
    bank = bank_from([flat_plus(0.0004)] * 6)
    plan = mc.TradePlan("long", 100, 99, [mc.Target(100.5, 0.5), mc.Target(101, 0.25)], breakeven_after=0,
                        trail_r=1.0)
    res = mc.simulate(bank, plan, 0, 77, n_sims=100, seed=0)
    assert (res.outcome == mc.TARGET).all()
    assert (res.t_all_targets >= 0).all()


def test_time_exit_when_nothing_happens():
    bank = bank_from([np.full(78, 100.0)] * 5, spread=0.01)
    plan = mc.TradePlan("long", 100, 99, [mc.Target(101, 1.0)], slippage=0.0)
    s = mc.summarize(mc.simulate(bank, plan, 5, 77, n_sims=100, seed=0))
    assert s["p_time_exit"] == 1.0
    assert s["expected_r"] == pytest.approx(0.0, abs=1e-9)


def test_vol_scale_and_demean():
    rng = np.random.default_rng(5)
    days = [100 * np.exp(np.cumsum(rng.normal(0.0003, 0.002, 78))) for _ in range(20)]
    bank = bank_from(days, spread=0.0)
    plan = mc.TradePlan("long", 100, 99.5, [mc.Target(100.5, 1.0)])
    calm = mc.summarize(mc.simulate(bank, plan, 10, 77, n_sims=4000, seed=1, vol_scale=0.5))
    wild = mc.summarize(mc.simulate(bank, plan, 10, 77, n_sims=4000, seed=1, vol_scale=2.0))
    assert wild["p_time_exit"] < calm["p_time_exit"]
    drift = mc.summarize(mc.simulate(bank, plan, 10, 77, n_sims=4000, seed=1))
    neutral = mc.summarize(mc.simulate(bank, plan, 10, 77, n_sims=4000, seed=1, demean=True))
    assert neutral["p_target"] < drift["p_target"]


def test_auto_vol_scale_reads_today():
    rng = np.random.default_rng(1)
    hist = [make_day(date(2026, 9, 1) + timedelta(days=i), 100 + np.cumsum(rng.normal(0, 0.05, 78)), spread=0.1)
            for i in range(10)]
    bank = mc.build_bank(pd.concat(hist), Session(), 5)
    today_df = make_day(date(2026, 10, 1), 100 + np.cumsum(rng.normal(0, 0.05, 12)), spread=0.2)
    today = mc.build_bank(today_df, Session(), 5, min_coverage=0)
    scale, note = mc.auto_vol_scale(bank, today, 12)
    assert 1.6 < scale < 2.4
    assert "volatility" in note


def test_short_side_mirrors_long():
    rng = np.random.default_rng(9)
    days = [100 * np.exp(np.cumsum(rng.normal(0, 0.002, 78))) for _ in range(25)]
    bank = bank_from(days)
    mirrored = mc.build_bank(pd.concat([make_day(date(2026, 9, 1) + timedelta(days=i), 1e4 / d) for i, d in
                                        enumerate(days)]), Session(), 5)
    long_ = mc.summarize(mc.simulate(bank, mc.TradePlan("long", 100, 99.5, [mc.Target(101, 1)], slippage=0),
                                     5, 77, mode="replay"))
    short = mc.summarize(mc.simulate(mirrored, mc.TradePlan("short", 100, 1e4 / 99.5, [mc.Target(1e4 / 101, 1)],
                                                            slippage=0), 5, 77, mode="replay"))
    assert long_["p_target"] == pytest.approx(short["p_target"], abs=0.05)
    assert long_["p_stop"] == pytest.approx(short["p_stop"], abs=0.05)
