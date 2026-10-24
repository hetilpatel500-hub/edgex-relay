import sys
from datetime import date, time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from tradekit.session import Session  # noqa: E402

TZ = "America/New_York"


def make_day(d: date, closes, interval=5, start=time(9, 30), spread=0.05, volume=1000.0, opens=None,
             highs=None, lows=None) -> pd.DataFrame:
    """Bars for one session from a list of closes (open = previous close unless given)."""
    closes = np.asarray(closes, dtype=float)
    o = np.asarray(opens, dtype=float) if opens is not None else np.r_[closes[0], closes[:-1]]
    h = np.asarray(highs, dtype=float) if highs is not None else np.maximum(o, closes) + spread
    lo = np.asarray(lows, dtype=float) if lows is not None else np.minimum(o, closes) - spread
    idx = pd.date_range(pd.Timestamp.combine(d, start).tz_localize(TZ), periods=len(closes),
                        freq=f"{interval}min")
    return pd.DataFrame({"open": o, "high": h, "low": lo, "close": closes, "volume": volume}, index=idx)


@pytest.fixture
def session():
    return Session()


@pytest.fixture
def run_script():
    import subprocess

    def _run(rel, *args, env=None):
        import os

        e = dict(os.environ)
        e.update(env or {})
        return subprocess.run([sys.executable, str(ROOT / rel), *args], capture_output=True, text=True, env=e,
                              timeout=120)

    return _run
