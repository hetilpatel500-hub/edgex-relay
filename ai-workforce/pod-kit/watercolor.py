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
        # smooth noise fields for pigment variation, made on first use
        self._fields = {}
        # v2 designs: every deposit is also summed here, so an object painted
        # over an earlier wash still counts as "in front" (see paint_around)
        self.v2 = False
        self.paint = np.zeros((h, w), dtype=np.float32)

    def reserve(self, shape):
        self.reserves.append(shape)

    def snapshot(self):
        snap = (self.cover.copy(), np.asarray(self.ink.getchannel('A'), dtype=np.float32))
        return snap + (self.paint.copy(),) if self.v2 else snap

    def paint_around(self, before):
        """Everything painted since `before` (a snapshot) becomes an object in
        front: later washes, gouache and pen lines go around it, the way a
        watercolorist paints a bough behind a mug instead of over it."""
        cov0, ink0 = before[:2]
        ink1 = np.asarray(self.ink.getchannel('A'), dtype=np.float32)
        m = np.clip(np.maximum((self.cover - cov0) * 4, (ink1 - ink0) / 64), 0, 1)
        if len(before) > 2:
            m = np.maximum(m, np.clip((self.paint - before[2]) * 3, 0, 1))
        if self.v2:
            # v2: no dilation, so later washes meet the object's edge instead of
            # leaving a white cut-out halo round it
            im = Image.fromarray((m * 255).astype(np.uint8))
            m = np.asarray(im.filter(ImageFilter.GaussianBlur(max(0.8, self.w / 3500))), dtype=np.float32) / 255
        else:
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

    def field(self, which):
        """A smooth 0..1 noise field the size of the canvas: 'fine', 'mid' or
        'broad' blotches. Pigment never lies evenly in a real wash: it pools
        and thins in soft patches, and these fields say where."""
        f = self._fields.get(which)
        if f is None:
            cell = max(6, self.w // {'fine': 70, 'mid': 24, 'broad': 9}[which])
            acc = np.zeros((self.h, self.w), dtype=np.float32)
            for c2, amp in ((cell, 0.65), (max(3, cell // 3), 0.35)):
                small = self.np_rng.random((self.h // c2 + 3, self.w // c2 + 3)).astype(np.float32)
                im = Image.fromarray((small * 255).astype(np.uint8)).resize(
                    ((self.w // c2 + 3) * c2, (self.h // c2 + 3) * c2), Image.BICUBIC)
                acc += amp * np.asarray(im, dtype=np.float32)[:self.h, :self.w] / 255
            lo, hi = np.percentile(acc[::7, ::7], (2, 98))
            f = np.clip((acc - lo) / max(1e-6, hi - lo), 0, 1)
            self._fields[which] = f
        return f

    def _field_for(self, size):
        return 'fine' if size < self.w / 14 else ('mid' if size < self.w / 4 else 'broad')

    def _deposit(self, d, x0, y0, color, color2=None, vary=None, vary_amt=0.5, size=None, ang=None):
        """Lay density d (array at x0, y0) down as transparent pigment, with an
        optional wet-in-wet gradient (color2) and patchy variation (vary)."""
        bh, bw = d.shape
        keep = self._around(x0, y0, x0 + bw, y0 + bh)
        if keep is not None:
            d = d * keep
        c1 = hexrgb(color)
        if color2:
            c2 = hexrgb(color2)
            ang = self.rnd.uniform(0, 2 * math.pi) if ang is None else ang
            yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
            t = ((xx - bw / 2) * math.cos(ang) + (yy - bh / 2) * math.sin(ang)) / (max(bw, bh) / 2)
            t = np.clip((t + 1) / 2, 0, 1)[..., None]
            col = c1 * (1 - t) + c2 * t
        else:
            col = np.broadcast_to(c1[None, None, :], (bh, bw, 3))
        if vary:
            f = self.field(self._field_for(size or max(bw, bh)))[y0:y0 + bh, x0:x0 + bw]
            t = (np.clip(f, 0, 1) ** 1.3 * vary_amt)[..., None]
            col = col * (1 - t) + hexrgb(vary)[None, None, :] * t
        k = -np.log(np.clip(col, 0.03, 1.0))
        self.absorb[y0:y0 + bh, x0:x0 + bw] += d[..., None] * k
        self.cover[y0:y0 + bh, x0:x0 + bw] = np.maximum(self.cover[y0:y0 + bh, x0:x0 + bw], np.clip(d, 0, 1))
        self.paint[y0:y0 + bh, x0:x0 + bw] += np.clip(d, 0, 1)

    def _box(self, pts, pad_frac=0.25, pad_min=8):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        size = max(max(xs) - min(xs), max(ys) - min(ys), 1)
        pad = int(size * pad_frac) + pad_min
        x0 = max(0, int(min(xs)) - pad); y0 = max(0, int(min(ys)) - pad)
        x1 = min(self.w, int(max(xs)) + pad); y1 = min(self.h, int(max(ys)) + pad)
        return x0, y0, x1, y1, size

    def _mask(self, pts, x0, y0, x1, y1, blur=0.0):
        m = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(p[0] - x0, p[1] - y0) for p in pts], fill=255)
        if blur > 0:
            m = m.filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(m, dtype=np.float32) / 255

    def lift(self, shape, amount=0.6, soft=0.06, clip=None):
        """Lift pigment with a damp brush: the paper shows through again. Used
        for the soft highlight on glossy paint, glass and the top of a form."""
        x0, y0, x1, y1, size = self._box(shape, 0.2)
        if x1 <= x0 or y1 <= y0:
            return
        m = self._mask(deform(shape, 2, 0.02, rnd=self.rnd), x0, y0, x1, y1, max(1.0, size * soft))
        if clip is not None:
            m = m * self._mask(clip, x0, y0, x1, y1, 1.0)
        keep = self._around(x0, y0, x1, y1)
        if keep is not None:
            m = m * keep
        self.absorb[y0:y1, x0:x1] *= (1 - amount * m)[..., None]

    def glow(self, cx, cy, r, color, strength=0.35):
        """A soft round bloom of color with no edge (light around a bulb or a star)."""
        x0, y0 = max(0, int(cx - r * 1.6)), max(0, int(cy - r * 1.6))
        x1, y1 = min(self.w, int(cx + r * 1.6)), min(self.h, int(cy + r * 1.6))
        if x1 <= x0 or y1 <= y0:
            return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = strength * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r) * 2.2)
        self._deposit(d.astype(np.float32), x0, y0, color)

    def dry_brush(self, path, width, color, strength=0.8, bristles=7, gap=0.45, taper=True, color2=None, alpha_jitter=0.35):
        """A dry-brush stroke along `path`: separate bristle marks that skip
        over the paper's tooth (bark, wood grain, fur, a scratchy twig)."""
        rnd = self.rnd
        x0, y0, x1, y1, size = self._box(path, 0.0, int(width * 2) + 6)
        if x1 <= x0 or y1 <= y0:
            return
        acc = Image.new('L', (x1 - x0, y1 - y0), 0)
        dr = ImageDraw.Draw(acc)
        n = len(path)
        for b in range(bristles):
            o = (b / max(1, bristles - 1) - 0.5) * width
            pts = []
            for i, (px, py) in enumerate(path):
                qx, qy = path[min(i + 1, n - 1)]; rx, ry = path[max(i - 1, 0)]
                dx, dy = qx - rx, qy - ry; L = math.hypot(dx, dy) or 1
                tf = math.sin(math.pi * (0.08 + 0.84 * i / max(1, n - 1))) ** 0.6 if taper else 1.0
                pts.append((px - dy / L * o * tf - x0 + rnd.gauss(0, width * 0.03), py + dx / L * o * tf - y0 + rnd.gauss(0, width * 0.03)))
            a = int(255 * rnd.uniform(1 - alpha_jitter, 1.0))
            dr.line(pts, fill=a, width=max(1, int(width / bristles * 1.5)), joint='curve')
        d = np.asarray(acc, dtype=np.float32) / 255
        tooth = self._grain[y0:y1, x0:x1]
        d = d * np.clip((tooth - gap * 0.9) * 3.0, 0, 1)
        self._deposit(np.clip(d * strength, 0, 1.3), x0, y0, color, color2)

    def paint_text(self, s, font_path, size, cx, cy, color, color2=None, vary=None, vary_amt=0.55, arc=None,
                   tracking=0.0, strength=1.05, edge=0.9, outline=None, angle=0.0):
        """Lettering painted in watercolor: the letter shapes are filled with a
        wash (patchy pigment, darker where it pooled at the edges), instead of
        flat ink. outline = (rgb, px, alpha) adds a thin pen edge for crispness.
        arc > 0 bends the line over a circle below it; arc < 0 along a smile."""
        font = ImageFont.truetype(font_path, size)
        pad = int(size * 0.6)
        if not arc:
            box = font.getbbox(s)
            tw = int(font.getlength(s) * (1 + tracking)) + 2 * pad; th = box[3] - box[1] + 2 * pad
            tile = Image.new('L', (tw, th), 0)
            dr = ImageDraw.Draw(tile)
            xx = pad
            for ch in s:
                dr.text((xx, pad - box[1]), ch, font=font, fill=255)
                xx += font.getlength(ch) * (1 + tracking)
            real = tile.getbbox() or (0, 0, tw, th)
            if angle:
                tile = tile.rotate(-math.degrees(angle), resample=Image.BICUBIC, expand=True)
                real = tile.getbbox() or (0, 0, tile.width, tile.height)
            ox = int(cx - (real[0] + real[2]) / 2); oy = int(cy - (real[1] + real[3]) / 2)
        else:
            R = abs(arc)
            widths = [font.getlength(ch) * (1 + tracking) for ch in s]
            span = sum(widths) / R
            ext = int(R * 2 + size * 2.5)
            tile = Image.new('L', (ext, ext), 0)
            ccx = ext / 2; ccy = ext / 2
            ang = -span / 2
            for ch, w in zip(s, widths):
                mid = ang + w / R / 2
                if arc > 0:
                    px = ccx + R * math.sin(mid); py = ccy - R * math.cos(mid); rot = -math.degrees(mid)
                else:
                    px = ccx + R * math.sin(mid); py = ccy + R * math.cos(mid); rot = math.degrees(mid)
                g = Image.new('L', (int(size * 2), int(size * 2)), 0)
                b = ImageDraw.Draw(g).textbbox((0, 0), ch, font=font)
                ImageDraw.Draw(g).text((size - (b[2] - b[0]) / 2 - b[0], size - (b[3] + b[1]) / 2), ch, font=font, fill=255)
                g = g.rotate(rot, resample=Image.BICUBIC)
                tile.paste(255, (int(px - size), int(py - size)), g)
                ang += w / R
            # (cx, cy) is the middle of the arc's apex, like Canvas.text
            ox = int(cx - ccx); oy = int(cy - (ccy - R if arc > 0 else ccy + R))
        # clip the tile to the canvas
        x0, y0 = max(0, ox), max(0, oy)
        x1, y1 = min(self.w, ox + tile.width), min(self.h, oy + tile.height)
        if x1 <= x0 or y1 <= y0:
            return
        tile = tile.crop((x0 - ox, y0 - oy, x1 - ox, y1 - oy))
        m = np.asarray(tile, dtype=np.float32) / 255
        soft = np.asarray(tile.filter(ImageFilter.GaussianBlur(max(1.0, size * 0.012))), dtype=np.float32) / 255
        wide = np.asarray(tile.filter(ImageFilter.GaussianBlur(max(2.0, size * 0.05))), dtype=np.float32) / 255
        rim = np.clip(soft - wide, 0, 1)
        d = soft * 0.72 + edge * rim * 1.8
        f = self.field('fine')[y0:y1, x0:x1]
        g = self._grain[y0:y1, x0:x1]
        d = d * (0.78 + 0.32 * f) * (1 + 0.35 * (g - 0.5) * 2)
        self._deposit(np.clip(d * strength, 0, 1.5), x0, y0, color, color2, vary, vary_amt, size=size * 3, ang=math.pi / 2)
        if outline:
            rgb, px, alpha = outline
            ring = tile.filter(ImageFilter.MaxFilter(max(3, int(px) * 2 + 1)))
            o = np.clip(np.asarray(ring, dtype=np.float32) - m * 255, 0, 255) * (alpha / 255)
            layer = Image.new('RGBA', tile.size, tuple(rgb) + (0,))
            layer.putalpha(Image.fromarray(o.astype(np.uint8)))
            self.composite_around(layer, (x0, y0))

    def wash(self, shape, color, color2=None, strength=1.0, layers=40, spread=0.06, edge=0.55,
             granulate=0.35, blur=None, base_depth=3, layer_depth=3, vary=None, vary_amt=0.5, blooms=0,
             bloom_size=0.2, ang=None, clip=None):
        """Paint one watercolor wash filling `shape` (list of (x, y)).
        vary = a third color that the pigment drifts toward in soft patches;
        blooms = how many backruns (cauliflower blooms: a pale patch with a
        dark rim where wet paint crept back into a drying wash)."""
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
        # backruns: a pale patch inside, pigment pushed to a dark ragged rim
        if blooms:
            ys_, xs_ = np.nonzero(d[::4, ::4] > 0.45)
            for _ in range(blooms if len(xs_) else 0):
                i = rnd.randrange(len(xs_)); bx, by = xs_[i] * 4, ys_[i] * 4
                r = size * bloom_size * rnd.uniform(0.6, 1.3)
                bl = deform(ellipse(bx, by, r, r * rnd.uniform(0.6, 1.0), 12, rnd.uniform(0, 3.2)), 4, 0.09, rnd=rnd)
                m = self._mask(bl, 0, 0, bw, bh, max(1.0, r * 0.03))
                inner = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(2.0, r * 0.14))),
                                   dtype=np.float32) / 255
                d = d * (1 - 0.42 * m + 2.0 * np.clip(m - inner, 0, 1))
        if clip is not None:   # keep the wash inside another shape (e.g. shadow inside a glass ball)
            d = d * self._mask(clip, x0, y0, x1, y1, max(1.0, size * 0.004))
        # pigment settles unevenly in soft patches, then granulation
        if vary:
            d = d * (0.82 + 0.36 * self.field(self._field_for(size))[y0:y1, x0:x1])
        g = self._grain[y0:y1, x0:x1]
        d = d * (1 + granulate * (g - 0.5) * 2)
        d = np.clip(d * strength, 0, 1.4)
        # color: optional wet-in-wet gradient along a random direction (absorption
        # of a transparent pigment: -ln(color) per unit density)
        self._deposit(d, x0, y0, color, color2, vary, vary_amt, size, ang)

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
            else:         # text on the bottom of a circle whose center is above (reads left to right, a smile)
                x = cx + R * math.sin(mid); y = cy - R + R * math.cos(mid); rot = math.degrees(mid)
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
