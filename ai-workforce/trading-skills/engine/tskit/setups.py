"""Setup loading.

A setup file is a Python module with a list SETUPS of dicts:
  id      unique id (snake_case)
  name    plain-English name
  family  e.g. 'pattern', 'session/gaps'
  tf      'M5' (default) or 'D'
  rules   the rules in one or two sentences, written before any testing
  detect  detect(s) -> yields (i, d): bar index i (the signal is known at that
          bar's close) and direction d (1 = leans up, -1 = leans down).
          M5 setups receive a Session, D setups a Daily series.

Files written for the Edgex chart lab import a module called `core`; a
compatible `core` is installed on the fly, bound to the active data store.
"""
import functools, glob, importlib.util, os, sys, types
from . import data, session

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILTIN = os.path.join(HERE, 'setups')


def install_core_shim(store):
    m = types.ModuleType('core')
    for name in ('profile', 'rsi', 'sma', 'Session', 'Bar', 'ETFS', 'STOCKS', 'UNIVERSE', 'OPEN', 'CLOSE',
                 'FULL_SESSION'):
        setattr(m, name, getattr(session, name))
    m.HERE = store
    m.sessions = functools.lru_cache(maxsize=None)(lambda sym: session.sessions(data.read(store, sym, 'M5'), sym))
    m.Daily = lambda sym: session.Daily(data.read(store, sym, 'D'), sym)
    m.read = lambda sym, tf: iter(data.read(store, sym, tf))
    sys.modules['core'] = m
    return m


def load(dirs=None, store=None, only=None):
    """All setups from the built-in folder plus any extra folders."""
    if store is not None:
        install_core_shim(store)
    out, seen = [], set()
    for d in [BUILTIN] + list(dirs or []):
        for f in sorted(glob.glob(os.path.join(d, '*.py'))):
            name = 'tskit_setup_' + os.path.basename(f)[:-3].replace('-', '_')
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for s in getattr(mod, 'SETUPS', []):
                s = dict(s)
                s.setdefault('tf', 'M5')
                s['file'] = os.path.relpath(f, d)
                if s['id'] in seen or (only and s['id'] not in only):
                    continue
                seen.add(s['id'])
                out.append(s)
    return out


def fires(setup, sess, lookback=None):
    """[(i, d)] for one session or daily series, ignoring detectors that run
    off the end of a partial session."""
    try:
        ev = [(i, d) for i, d in setup['detect'](sess)]
    except (IndexError, ZeroDivisionError, TypeError, ValueError):
        return []
    n = len(sess.bars) if setup['tf'] == 'M5' else len(sess.c)
    ev = [(i, d) for i, d in ev if 0 <= i < n]
    if lookback is not None:
        ev = [(i, d) for i, d in ev if i >= n - lookback]
    return ev
