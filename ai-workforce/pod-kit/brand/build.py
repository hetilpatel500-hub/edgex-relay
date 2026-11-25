"""Edgexhp brand files: shop icon (500/1000), wordmark (the painted E is the first letter of EDGEXHP), Etsy big banner 3360x840, mini banner. No product words in any logo.
usage (in a scratch folder): python3 <kit>/brand/emark.py e11 1600 11 && python3 <kit>/brand/build.py"""
import sys
sys.path.insert(0, '/home/user/edgex-relay/ai-workforce/pod-kit')
from watercolor import Canvas, ellipse
from PIL import Image, ImageDraw, ImageFont
def FT(size, w=500):
    f = ImageFont.truetype(FONT_PATH, size); f.set_variation_by_axes([w]); return f
FONT_PATH = FONT = '/home/user/edgex-relay/ai-workforce/pod-kit/fonts/JosefinSans.ttf'
PAPER = (251, 246, 239); INK = (61, 58, 58)
paper = Image.open('e11_paper.png').convert('RGB'); clear = Image.open('e11_clear.png').convert('RGBA')
W = paper.size[0]
# 1) shop icon: E fills ~75%
cx = int(W * 0.52); half = int(W * 0.4)
icon = paper.crop((cx - half, W // 2 - half, cx + half, W // 2 + half))
icon.resize((1000, 1000), Image.LANCZOS).save('Edgexhp_shop_icon_1000.png')
icon.resize((500, 500), Image.LANCZOS).save('Edgexhp_shop_icon_500.png')
# tight E (transparent) for lockups
bb = clear.getbbox(); e = clear.crop(bb)
def spaced(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + track
    return x
def text_w(d, text, font, track): return sum(d.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)
# 2) wordmark: the painted E is the first letter, then DGEXHP in type (one word, one E)
def wordmark(cap, track, gap_k=0.55, scale=1.25):
    """RGBA wordmark. cap = cap height of the typed letters in px; the painted E is `scale` x taller,
    sitting on the same baseline."""
    f = FT(10, 500); d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    bb = d0.textbbox((0, 0), 'D', font=f); size = int(10 * cap / (bb[3] - bb[1])); f = FT(size, 500)
    bb = d0.textbbox((0, 0), 'D', font=f); capH = bb[3] - bb[1]
    eh = int(capH * scale); ew = int(e.size[0] * eh / e.size[1]); em = e.resize((ew, eh), Image.LANCZOS)
    tw = text_w(d0, 'DGEXHP', f, track); gap = int(track * gap_k + capH * 0.08)
    pad = int(capH * 0.1); Wd = ew + gap + int(tw) + pad; H = eh + pad
    im = Image.new('RGBA', (Wd, H), (0, 0, 0, 0)); im.alpha_composite(em, (0, H - eh))
    d = ImageDraw.Draw(im)
    spaced(d, (ew + gap, H - capH - bb[1]), 'DGEXHP', f, INK + (255,), track)
    return im
def on(bg, img, padx, pady):
    out = Image.new('RGBA', (img.size[0] + 2 * padx, img.size[1] + 2 * pady), bg); out.alpha_composite(img, (padx, pady)); return out
wm = wordmark(260, 40)
on(PAPER + (255,), wm, 140, 140).convert('RGB').save('Edgexhp_logo_cream.png')
on((0, 0, 0, 0), wm, 60, 60).save('Edgexhp_logo_transparent.png')
# 3) Etsy big banner 3360x840: wordmark centred, soft washes at both ends, no tagline
BW, BH = 3360, 840
c = Canvas(BW, BH, seed=21)
for (x, y, r), col, col2 in [((3080, 300, 300), '#e98f86', '#f3b9a8'), ((3300, 640, 280), '#86b7a2', '#b8d8c6'), ((180, 620, 300), '#e9b65b', '#f3d39a'), ((60, 200, 240), '#7ea6c9', '#b3cde3')]:
    c.wash(ellipse(x, y, r, r, 22), col, col2, strength=0.38, layers=36, spread=0.03)
ban = c.on_paper('#fbf6ef').convert('RGBA')
bw = wordmark(250, 38); ban.alpha_composite(bw, ((BW - bw.size[0]) // 2, (BH - bw.size[1]) // 2))
ban.convert('RGB').save('Edgexhp_banner_3360x840.jpg', quality=92)
# 4) mini banner 1200x160
mini = Image.new('RGBA', (1200, 160), PAPER + (255,)); mw = wordmark(70, 12)
mini.alpha_composite(mw, (60, (160 - mw.size[1]) // 2)); mini.convert('RGB').save('Edgexhp_mini_banner_1200x160.png')
print('ok')
