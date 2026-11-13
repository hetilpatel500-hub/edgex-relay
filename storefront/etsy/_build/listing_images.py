"""Compose Etsy listing images (2700 x 2025, 4:3) from real product renders.

Inputs: page PNGs rendered from the actual product files (PDF pages, or the
sample-filled spreadsheet printed via LibreOffice). Every screen shown is the
real product; spreadsheet shots are labelled "shown with sample data".
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
W, H = 2700, 2025
CREAM = (248, 244, 237)
INK = (38, 49, 59)
MUTED = (107, 117, 128)


def font(name, size):
    files = {"serif": "Fraunces_600SemiBold.ttf", "serif_it": "Fraunces_400Regular_Italic.ttf",
             "sans": "DMSans_400Regular.ttf", "sans_med": "DMSans_500Medium.ttf", "sans_bold": "DMSans_700Bold.ttf"}
    return ImageFont.truetype(os.path.join(FD, files[name]), size)


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c, amount, base=(255, 255, 255)):
    return tuple(round(a + (b - a) * amount) for a, b in zip(c, base))


def trim(img, pad=24, thresh=246):
    g = img.convert("L")
    mask = g.point(lambda v: 255 if v < thresh else 0)
    box = mask.getbbox()
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))


def crop_frac(img, box):
    l, t, r, b = box
    return img.crop((int(img.width * l), int(img.height * t), int(img.width * r), int(img.height * b)))


def fit(img, w=None, h=None):
    if w and h:
        s = min(w / img.width, h / img.height)
    elif w:
        s = w / img.width
    else:
        s = h / img.height
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def shadow_paste(canvas, img, xy, radius=18, blur=28, offset=(0, 18), opacity=70, rotate=0):
    """Paste an image with a soft drop shadow (optionally rotated)."""
    img = img.convert("RGBA")
    if radius:
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
        img.putalpha(m)
    if rotate:
        img = img.rotate(rotate, expand=True, resample=Image.BICUBIC)
    pad = blur * 3
    sh = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * opacity // 255)
    shade = Image.new("RGBA", img.size, (20, 28, 36, 255))
    shade.putalpha(a)
    sh.paste(shade, (pad, pad), shade)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    x, y = xy
    canvas.alpha_composite(sh, (x - pad + offset[0], y - pad + offset[1]))
    canvas.alpha_composite(img, (x, y))
    return img.size


def window(shot, width, accent, title=""):
    """App-window frame around a spreadsheet screenshot."""
    shot = fit(shot, w=width - 24)
    bar = 58
    win = Image.new("RGB", (width, shot.height + bar + 12), (255, 255, 255))
    d = ImageDraw.Draw(win)
    d.rectangle((0, 0, width, bar), fill=(236, 239, 242))
    for i, col in enumerate(((236, 106, 94), (244, 190, 80), (98, 197, 84))):
        d.ellipse((24 + i * 34, 20, 44 + i * 34, 40), fill=col)
    if title:
        d.text((width // 2, bar // 2), title, font=font("sans_med", 26), fill=MUTED, anchor="mm")
    win.paste(shot, (12, bar + 6))
    return win


def paper(page, width, border=(222, 226, 230)):
    p = fit(page, w=width).convert("RGB")
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, p.width - 1, p.height - 1), outline=border, width=2)
    return p


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, maxw, lead=1.22):
    for ln in wrap(d, text, fnt, maxw):
        d.text((x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * lead)
    return y


def pill(d, x, y, text, fg, bg, size=40, padx=34, pady=18):
    f = font("sans_bold", size)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + tw + padx * 2, y + size + pady * 2), radius=(size + pady * 2) // 2, fill=bg)
    d.text((x + padx, y + pady - size * 0.12), text, font=f, fill=fg)
    return x + tw + padx * 2


def base(accent):
    c = Image.new("RGBA", (W, H), CREAM + (255,))
    return c


def footer_note(d, text):
    d.text((W - 90, H - 70), text, font=font("sans", 30), fill=MUTED, anchor="rs")


# ---------------- templates ----------------

def hero(spec, out):
    acc = hex2rgb(spec["accent"])
    c = base(acc)
    d = ImageDraw.Draw(c)
    # accent panel on the right
    d.rectangle((1180, 0, W, H), fill=mix(acc, 0.80))
    d.ellipse((2150, -380, 3050, 520), fill=mix(acc, 0.62))
    x = 120
    d.text((x, 190), spec["kicker"].upper(), font=font("sans_bold", 40), fill=acc)
    y = 270
    for ln in spec["title"]:
        d.text((x, y), ln, font=font("serif", 150), fill=INK)
        y += 168
    y += 20
    y = text_block(d, x, y, spec["subtitle"], font("serif_it", 58), MUTED, 980)
    y += 40
    for b in spec["bullets"]:
        d.ellipse((x, y + 20, x + 22, y + 42), fill=acc)
        y = text_block(d, x + 50, y, b, font("sans_med", 50), INK, 930, 1.18) + 22
    px = pill(d, x, H - 250, spec["badge"], (255, 255, 255), acc)
    pill(d, px + 24, H - 250, "Instant download", acc, mix(acc, 0.82))
    # mockups
    shots = spec["hero_shots"]
    if spec["kind"] == "sheet":
        back = window(shots[1], 1250, acc)
        shadow_paste(c, back, (1400, 260))
        front = window(shots[0], 1380, acc)
        shadow_paste(c, front, (1260, 700))
    else:
        p2 = paper(shots[1], 900)
        p1 = paper(shots[0], 900)
        shadow_paste(c, p2, (1720, 300), radius=0, rotate=-5)
        shadow_paste(c, p1, (1300, 240), radius=0, rotate=3)
    if spec.get("sample_note"):
        footer_note(d, spec["sample_note"])
    c.convert("RGB").save(out, optimize=True)


def inside(spec, out):
    acc = hex2rgb(spec["accent"])
    c = base(acc)
    d = ImageDraw.Draw(c)
    d.text((W // 2, 150), "What's inside", font=font("serif", 120), fill=INK, anchor="mm")
    d.text((W // 2, 262), spec["inside_sub"], font=font("sans_med", 50), fill=acc, anchor="mm")
    items = spec["inside"]
    n = len(items)
    cols = spec.get("inside_cols", 4)
    rows = (n + cols - 1) // cols
    top, bottom = 360, H - 110
    cw = (W - 200) // cols
    ch = (bottom - top) // rows
    for i, (img, label) in enumerate(items):
        r, col = divmod(i, cols)
        cx = 100 + col * cw + cw // 2
        cy = top + r * ch
        box_w, box_h = cw - 70, ch - 110
        im = fit(img, w=box_w, h=box_h).convert("RGB")
        dd = ImageDraw.Draw(im)
        dd.rectangle((0, 0, im.width - 1, im.height - 1), outline=(220, 224, 228), width=2)
        shadow_paste(c, im, (cx - im.width // 2, cy + (box_h - im.height) // 2), radius=6, blur=16, offset=(0, 10), opacity=55)
        d.text((cx, cy + box_h + 50), label, font=font("sans_med", 40), fill=INK, anchor="mm")
    if spec.get("sample_note"):
        footer_note(d, spec["sample_note"])
    c.convert("RGB").save(out, optimize=True)


def feature(spec, feat, out):
    acc = hex2rgb(spec["accent"])
    c = base(acc)
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1000, H), fill=mix(acc, 0.84))
    x = 110
    d.text((x, 200), feat["kicker"].upper(), font=font("sans_bold", 40), fill=acc)
    y = text_block(d, x, 270, feat["headline"], font("serif", 104), INK, 800, 1.12) + 50
    for p in feat["points"]:
        d.rectangle((x, y + 14, x + 8, y + 70), fill=acc)
        y = text_block(d, x + 40, y, p, font("sans", 48), INK, 760, 1.22) + 36
    shot = feat["shot"]
    if spec["kind"] == "sheet":
        s = fit(shot, w=1536, h=H - 340)
        win = window(s, s.width + 24, acc)
        shadow_paste(c, win, (1060 + (1580 - win.width) // 2, (H - win.height) // 2 - 20))
    else:
        p = paper(shot, 1300)
        if p.height > H - 200:
            p = paper(fit(shot, h=H - 220), fit(shot, h=H - 220).width)
        shadow_paste(c, p, (1060 + (1560 - p.width) // 2, (H - p.height) // 2), radius=0)
    if spec.get("sample_note"):
        footer_note(d, spec["sample_note"])
    c.convert("RGB").save(out, optimize=True)


def details(spec, out):
    acc = hex2rgb(spec["accent"])
    c = base(acc)
    d = ImageDraw.Draw(c)
    d.text((W // 2, 170), "How it works", font=font("serif", 120), fill=INK, anchor="mm")
    steps = spec["steps"]
    cw = (W - 240 - 2 * 60) // 3
    for i, (h, t) in enumerate(steps):
        x = 120 + i * (cw + 60)
        d.rounded_rectangle((x, 300, x + cw, 960), radius=36, fill=(255, 255, 255))
        d.ellipse((x + 60, 360, x + 190, 490), fill=acc)
        d.text((x + 125, 425), str(i + 1), font=font("serif", 80), fill=(255, 255, 255), anchor="mm")
        d.text((x + 60, 540), h, font=font("serif", 64), fill=INK)
        text_block(d, x + 60, 640, t, font("sans", 44), MUTED, cw - 120)
    # what you get
    d.rounded_rectangle((120, 1040, W - 120, H - 120), radius=36, fill=mix(acc, 0.84))
    d.text((200, 1110), "WHAT YOU GET", font=font("sans_bold", 42), fill=acc)
    y = 1190
    for g in spec["get"]:
        d.ellipse((200, y + 18, 222, y + 40), fill=acc)
        y = text_block(d, 250, y, g, font("sans_med", 48), INK, 1150) + 18
    x2 = 1500
    d.text((x2, 1110), "GOOD TO KNOW", font=font("sans_bold", 42), fill=acc)
    y = 1190
    for g in spec["know"]:
        d.ellipse((x2, y + 18, x2 + 22, y + 40), fill=acc)
        y = text_block(d, x2 + 50, y, g, font("sans_med", 48), INK, 1000) + 18
    c.convert("RGB").save(out, optimize=True)


def make_all(spec, outdir):
    os.makedirs(outdir, exist_ok=True)
    outs = []
    p = os.path.join(outdir, "01-main.png"); hero(spec, p); outs.append(p)
    p = os.path.join(outdir, "02-whats-inside.png"); inside(spec, p); outs.append(p)
    for i, f in enumerate(spec["features"]):
        p = os.path.join(outdir, "%02d-feature-%d.png" % (3 + i, i + 1)); feature(spec, f, p); outs.append(p)
    p = os.path.join(outdir, "%02d-how-it-works.png" % (3 + len(spec["features"]))); details(spec, p); outs.append(p)
    return outs
