"""tradekit: the shared engine behind the daytrading-skills Claude plugin.

Every skill in ../../skills/ is a thin CLI over these modules, so the math lives
in one tested place. Nothing in this package places orders; it only reads market
data and does arithmetic on it.
"""

__version__ = "0.1.0"
