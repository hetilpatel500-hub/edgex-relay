"""Edgexhp 'E' mark: a spine and three brush strokes, painted with the kit's watercolor engine.
usage: emark.py OUT_PREFIX SIZE SEED  -> OUT_PREFIX_paper.png and OUT_PREFIX_clear.png"""
import sys
sys.path.insert(0, '/home/user/edgex-relay/ai-workforce/pod-kit')
from watercolor import Canvas, rect
pre, W, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
c = Canvas(W, W, seed=seed); C = W / 2
x0 = C - W * 0.19
c.wash(rect(x0, C - W * 0.3, x0 + W * 0.085, C + W * 0.3), '#86b7a2', '#b8d8c6', strength=0.78, layers=34, spread=0.012)
for dy, ln, col, col2 in [(-0.3, 0.42, '#e98f86', '#f3b9a8'), (-0.042, 0.32, '#e9b65b', '#f3d39a'), (0.215, 0.42, '#7ea6c9', '#b3cde3')]:
    c.wash(rect(x0 + W * 0.025, C + W * dy, x0 + W * ln, C + W * (dy + 0.085)), col, col2, strength=0.72, layers=34, spread=0.015)
c.on_paper('#fbf6ef').save(pre + '_paper.png')
c.rgba().save(pre + '_clear.png')
