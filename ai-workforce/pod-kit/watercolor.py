"""Procedural watercolor painting at print resolution.

Why procedural: the image generators reachable from here return small
thumbnails, far below the 4500 x 5400 px Printify wants for a shirt. This
engine paints real watercolor-looking shapes at any size, deterministically
(same seed, same picture), with no credits and no third-party image rights.

Technique (the "stacked deformed polygon" method used in generative art):
  1. A base shape (circle, petal, leaf, any polygon) is deformed by recursive
     midpoint displacement, so its edge becomes irregular like a wet wash.
  2. That base is deformed again ~40 times more; each copy is drawn at very
     low opacity. Where copies overlap, pigment builds up: soft, feathered
     edges and a denser body, just like a real wash.
  3. Edge darkening: pigment pools at the rim of a drying wash, so density is
     boosted where the wash falls off.
  4. Granulation: a noise texture modulates density, like pigment settling in
     the paper's tooth.
  5. Wet-in-wet: every wash can blend from one hue to a second across its body.
  6. Colors mix subtractively (multiply), so overlapping washes darken and
     shift the way transparent paint does.

Canvas works in density per pixel; `Canvas.rgba()` turns it into a
transparent PNG (for shirts) or `Canvas.on_paper()` onto a paper color.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


# ---------------------------------------------------------------- geometry
def ellipse(cx, cy, rx, ry, n=12, rot=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def petal(cx, cy, length, width, angle, n=14):
    """Teardrop petal from (cx,cy) pointing along angle."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        # outline from base, around the tip, and back
        a = math.pi * t
        r = math.sin(a)
        along = length * (1 - math.cos(a)) / 2
        side = width * r * (1 - 0.35 * t)
        pts.append((along, side))
    pts += [(x, -y) for x, y in reversed(pts[1:-1])]
    ca, sa = math.cos(angle), math.sin(angle)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def leaf(cx, cy, length, width, angle, n=12):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((length * t, width * math.sin(math.pi * t) * (1 - 0.2 * t)))
    pts += [(x, -y * 0.85) for x, y in reversed(pts[1:-1])]
    ca, sa = math.cos(angle), math.sin(angle)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def rect(x0, y0, x1, y1, n_side=3):
    pts = []
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        for k in range(n_side):
            t = k / n_side
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return pts


def deform(poly, depth, variance, vdiv=2.0, rnd=random):
    """Recursive midpoint displacement; each vertex carries its own variance."""
    if not poly:
        return poly
    pts = [(p[0], p[1], p[2] if len(p) > 2 else variance * rnd.uniform(0.5, 1.5)) for p in poly]
    for _ in range(depth):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out.append(a)
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            v = (a[2] + b[2]) / 2
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            out.append((mx + rnd.gauss(0, L * v), my + rnd.gauss(0, L * v), v / vdiv))
        pts = out
    return pts


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.rnd = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        # optical density per channel (absorption); 0 = white paper
        self.absorb = np.zeros((h, w, 3), dtype=np.float32)
        self.cover = np.zeros((h, w), dtype=np.float32)
        self.ink = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self._grain = self._make_grain()
        # shapes kept white under a background wash (like masking fluid)
        self.reserves = []
        # 0..1 per pixel: an object in front that later paint goes around
        self.occl = None

    def reserve(self, shape):
        self.reserves.append(shape)

    def snapshot(self):
        return self.cover.copy(), np.asarray(self.ink.getchannel('A'), dtype=np.float32)

    def paint_around(self, before):
        """Everything painted since `before` (a snapshot) becomes an object in
        front: later washes, gouache and pen lines go around it, the way a
        watercolorist paints a bough behind a mug instead of over it."""
        cov0, ink0 = before
        ink1 = np.asarray(self.ink.getchannel('A'), dtype=np.float32)
        m = np.clip(np.maximum((self.cover - cov0) * 4, (ink1 - ink0) / 64), 0, 1)
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
        m = np.asarray(im.filter(ImageFilter.GaussianBlur(max(1.0, self.w / 1500))), dtype=np.float32) / 255
        self.occl = m if self.occl is None else np.maximum(self.occl, m)

    def _around(self, x0, y0, x1, y1):
        """How much paint may land here (1 - occlusion), or None if nothing is in front."""
        if self.occl is None:
            return None
        return 1 - self.occl[y0:y1, x0:x1]

    # a tileable-ish grain texture: two octaves of smoothed noise
    def _make_grain(self):
        h, w = self.h, self.w
        out = np.zeros((h, w), dtype=np.float32)
        for scale, amp in ((max(4, w // 900), 0.6), (max(2, w // 2200), 0.4)):
            small = self.np_rng.random((h // scale + 2, w // scale + 2)).astype(np.float32)
            im = Image.fromarray((small * 255).astype(np.uint8)).resize((w + scale * 2, h + scale * 2), Image.BICUBIC)
            out += amp * (np.asarray(im, dtype=np.float32)[:h, :w] / 255)
        return out  # ~0..1, mean ~0.5

    def wash(self, shape, color, color2=None, strength=1.0, layers=40, spread=0.06, edge=0.55,
             granulate=0.35, blur=None, base_depth=3, layer_depth=3):
        """Paint one watercolor wash filling `shape` (list of (x, y))."""
        rnd = self.rnd
        base = deform(shape, base_depth, spread, rnd=rnd)
        xs = [p[0] for p in base]; ys = [p[1] for p in base]
        size = max(max(xs) - min(xs), max(ys) - min(ys), 1)
        pad = int(size * 0.25) + 8
        x0 = max(0, int(min(xs)) - pad); y0 = max(0, int(min(ys)) - pad)
        x1 = min(self.w, int(max(xs)) + pad); y1 = min(self.h, int(max(ys)) + pad)
        if x1 <= x0 or y1 <= y0:
            return
        bw, bh = x1 - x0, y1 - y0
        acc = np.zeros((bh, bw), dtype=np.float32)
        step = 255 / layers * 1.6
        for _ in range(layers):
            p = deform([(x - x0, y - y0, v * rnd.uniform(0.6, 1.4)) for x, y, v in base], layer_depth, spread, rnd=rnd)
            im = Image.new('L', (bw, bh), 0)
            ImageDraw.Draw(im).polygon([(x, y) for x, y, _ in p], fill=int(step))
            acc += np.asarray(im, dtype=np.float32)
        d = np.clip(acc / 255, 0, 1)
        # soften a touch (paper absorbs), then edge darkening
        r = blur if blur is not None else max(1.0, size * 0.004)
        dim = Image.fromarray((d * 255).astype(np.uint8))
        d = np.asarray(dim.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255
        wide = np.asarray(dim.filter(ImageFilter.GaussianBlur(max(2.0, size * 0.03))), dtype=np.float32) / 255
        rim = np.clip(d - wide, 0, 1)
        d = d + edge * rim * 2.2
        # granulation
        g = self._grain[y0:y1, x0:x1]
        d = d * (1 + granulate * (g - 0.5) * 2)
        d = np.clip(d * strength, 0, 1.4)
        keep = self._around(x0, y0, x1, y1)
        if keep is not None:
            d = d * keep
        # color: optional wet-in-wet gradient along a random direction
        c1 = hexrgb(color)
        if color2:
            c2 = hexrgb(color2)
            ang = rnd.uniform(0, 2 * math.pi)
            yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
            t = ((xx - bw / 2) * math.cos(ang) + (yy - bh / 2) * math.sin(ang)) / (max(bw, bh) / 2)
            t = np.clip((t + 1) / 2, 0, 1)[..., None]
            col = c1 * (1 - t) + c2 * t
        else:
            col = c1[None, None, :]
        # absorption of a transparent pigment: -ln(color) per unit density
        k = -np.log(np.clip(col, 0.03, 1.0))
        self.absorb[y0:y1, x0:x1] += d[..., None] * k
        self.cover[y0:y1, x0:x1] = np.maximum(self.cover[y0:y1, x0:x1], np.clip(d, 0, 1))

    def splatter(self, cx, cy, radius, color, n=40, size=(2, 9), strength=0.8):
        rnd = self.rnd
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi); r = radius * math.sqrt(rnd.random())
            s = rnd.uniform(*size) * self.w / 4500
            self.wash(ellipse(cx + r * math.cos(a), cy + r * math.sin(a), s * 4, s * 4, 8), color,
                      layers=8, spread=0.12, strength=strength * rnd.uniform(0.5, 1), edge=0.8, blur=1)

    def ink_line(self, pts, width=10, color=(52, 48, 52), closed=True, jitter=0.004, passes=2, alpha=225):
        """Loose pen line along a path: two slightly offset passes."""
        rnd = self.rnd
        target, off = self.ink, (0, 0)
        if self.occl is not None:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            pad = int(width * 2) + 4
            x0 = max(0, int(min(xs)) - pad); y0 = max(0, int(min(ys)) - pad)
            x1 = min(self.w, int(max(xs)) + pad); y1 = min(self.h, int(max(ys)) + pad)
            if x1 <= x0 or y1 <= y0:
                return
            target, off = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)), (x0, y0)
        d = ImageDraw.Draw(target)
        # wobble scales with the canvas but never more than the line is wide,
        # so small motifs keep a clean hand-drawn line instead of a scribble
        span = min(max(self.w, self.h) * jitter, width * 0.9)
        for k in range(passes):
            seq = [(x - off[0] + rnd.gauss(0, span * 0.35), y - off[1] + rnd.gauss(0, span * 0.35)) for x, y, *_ in pts]
            if closed:
                seq = seq + seq[:1]
            wd = max(1, int(width * (1 if k == 0 else 0.55)))
            d.line(seq, fill=color + (alpha if k == 0 else int(alpha * 0.6),), width=wd, joint='curve')
        if target is not self.ink:
            self.composite_around(target, off)

    def composite_around(self, layer, off):
        """Put an RGBA layer onto the ink layer, going around objects in front."""
        x0, y0 = off
        keep = self._around(x0, y0, x0 + layer.width, y0 + layer.height)
        if keep is not None:
            a = np.asarray(layer.getchannel('A'), dtype=np.float32) * keep
            layer.putalpha(Image.fromarray(a.astype(np.uint8)))
        self.ink.alpha_composite(layer, (x0, y0))

    def text(self, s, font_path, size, cx, cy, fill=(52, 48, 52), arc=None, tracking=0.0, stroke=0):
        """Lettering, straight or along an arc (arc = radius in px; positive
        bends like a smile's opposite: text on top of a circle)."""
        font = ImageFont.truetype(font_path, size)
        if not arc:
            d = ImageDraw.Draw(self.ink)
            box = d.textbbox((0, 0), s, font=font, stroke_width=stroke)
            w, h = box[2] - box[0], box[3] - box[1]
            d.text((cx - w / 2 - box[0], cy - h / 2 - box[1]), s, font=font, fill=fill + (255,),
                   stroke_width=stroke, stroke_fill=fill + (255,))
            return
        widths = [font.getlength(ch) * (1 + tracking) for ch in s]
        total = sum(widths)
        R = abs(arc)
        ang = -total / R / 2
        for ch, w in zip(s, widths):
            mid = ang + w / R / 2
            if arc > 0:   # text on the top of a circle whose center is below
                x = cx + R * math.sin(mid); y = cy + R - R * math.cos(mid); rot = -math.degrees(mid)
            else:         # text on the bottom of a circle whose center is above
                x = cx + R * math.sin(-mid); y = cy - R + R * math.cos(mid); rot = math.degrees(mid)
                x = cx - R * math.sin(mid)
            tile = Image.new('RGBA', (int(size * 2), int(size * 2)), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            b = td.textbbox((0, 0), ch, font=font)
            td.text((size - (b[2] - b[0]) / 2 - b[0], size - (b[3] + b[1]) / 2), ch, font=font, fill=fill + (255,))
            tile = tile.rotate(rot, resample=Image.BICUBIC)
            self.ink.alpha_composite(tile, (int(x - size), int(y - size)))
            ang += w / R

    # ------------------------------------------------------------ output
    def _paper_rgb(self):
        return np.exp(-self.absorb)  # transmitted light on white paper, 0..1

    def rgba(self):
        """Transparent PNG: pigment where painted, ink on top."""
        rgb = self._paper_rgb()
        # alpha from how much light the pigment removes; recover the color
        # that, laid over white at that alpha, gives the painted result
        a = np.clip(1 - rgb.min(axis=2), 0, 1)
        a = np.clip(np.maximum(a * 1.25, self.cover * 0.0), 0, 1)
        safe = np.where(a > 1e-3, a, 1)[..., None]
        col = np.clip((rgb - (1 - a[..., None])) / safe, 0, 1)
        out = np.dstack([col * 255, a * 255]).astype(np.uint8)
        im = Image.fromarray(out, 'RGBA')
        im.alpha_composite(self.ink)
        return im

    def on_paper(self, paper='#fbf8f2'):
        rgb = self._paper_rgb() * hexrgb(paper)[None, None, :]
        im = Image.fromarray((rgb * 255).astype(np.uint8), 'RGB').convert('RGBA')
        im.alpha_composite(self.ink)
        return im.convert('RGB')
