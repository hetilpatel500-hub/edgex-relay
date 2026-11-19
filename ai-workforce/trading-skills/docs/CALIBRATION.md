# Time machine calibration

Generated 2026-10-24T07:12:12Z by `engine/tools/calibration_report.py` on a store of 12 symbols, 107 sessions (2026-05-15 to 2026-10-23). Every test trade is predicted only from data before its date (walk-forward). Trade tested: 1 ATR stop, 2R target, entry at a 5-minute close, flat by the close, costs included.

## 1. Clock-time mode, random entries

- 600 test trades, 300 paths each.
- Target first: predicted 33.0% on average, actual 31.2% (90% range 28.1% to 34.4%). Coin-flip baseline 32.9%.
- Brier score 0.2173 vs 0.2154 for the coin flip (skill -0.009; above zero would mean better than the coin flip).
- Expected R: predicted -0.173, actual -0.215.

Reading: on average the odds match reality, but trade by trade this mode is no better than the coin flip. It knows the time of day and volatility, not direction. Random entries have no edge to find.

## 2. Setup mode, out-of-sample signals

| Setup | Variant | Test signals | Predicted target first | Actual (90% range) | Coin flip | Brier: time machine / coin flip | Expected R: predicted / actual |
|---|---|---|---|---|---|---|---|
| ebsw_cross | fade · rvol+trend | 50 | 34.0% | 26.0% (17%-37%) | 28.2% | 0.2048 / 0.1964 | +0.02 / -0.28 |
| gap_go_rvol | with · vwap+rvol | 31 | 39.9% | 35.5% (23%-50%) | 33.4% | 0.2391 / 0.2347 | +0.20 / +0.10 |
| prior_range_tag | with · ppoc | 60 | 33.1% | 46.7% (36%-57%) | 31.4% | 0.2705 / 0.2735 | -0.09 / +0.28 |
| round_number_bounce | with · vwap+rvol | 107 | 35.2% | 39.2% (32%-47%) | 31.3% | 0.2426 / 0.2463 | +0.05 / +0.18 |
| strat_212_reversal | fade · vwap+rvol | 46 | 33.6% | 34.8% (24%-47%) | 24.9% | 0.2322 / 0.2402 | -0.08 / -0.12 |
| tweezer_session_extreme | fade · rvol | 38 | 38.8% | 44.7% (32%-58%) | 27.6% | 0.2705 / 0.2836 | +0.24 / +0.34 |

Pooled over 332 test signals: Brier 0.2434 vs 0.2460 for the coin flip (skill +0.011). Better than the coin flip on 4 of 6 setups.

Reading: when a setup has a real edge, its own history moves the odds away from the coin flip in the right direction, but only modestly, and not for every setup. These setups were chosen because they passed testing on this same store, so their out-of-sample period is cleaner than their in-sample period, but the set itself is survivor-biased.

Educational only. Not financial advice. Historical odds are not a forecast.
