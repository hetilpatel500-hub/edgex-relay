"""Small helpers every skill script uses: dependency check and friendly errors."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = PLUGIN_ROOT / "requirements.txt"


def require_deps() -> None:
    missing = []
    for mod in ("numpy", "pandas"):
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"error: missing Python packages: {', '.join(missing)}\n"
              f"install with: python3 -m pip install -r {REQUIREMENTS}", file=sys.stderr)
        sys.exit(3)


def home() -> Path:
    """Where journals and risk settings live (override with DAYTRADING_HOME)."""
    p = Path(os.environ.get("DAYTRADING_HOME", "~/.daytrading-skills")).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def run(main) -> None:
    require_deps()
    from .data import DataError  # noqa: PLC0415

    try:
        code = main()
    except (DataError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    except BrokenPipeError:  # output piped into head/less that closed early
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
    sys.exit(code or 0)


def parse_symbols(text: str | None) -> list[str]:
    if not text:
        return []
    out = []
    for part in text.replace("\n", ",").replace(" ", ",").split(","):
        p = part.strip().upper()
        if p and p not in out:
            out.append(p)
    return out
