"""Edgexhp brand files: shop icon (500/1000), logo lockups, Etsy big banner 3360x840, mini banner.
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
# 2) horizontal logo: E + EDGEXHP
def lockup(bg):
    H = 800; eh = 560; ew = int(e.size[0] * eh / e.size[1]); em = e.resize((ew, eh), Image.LANCZOS)
    f = FT(230, 500); tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    tw = text_w(tmp, 'EDGEXHP', f, 34); Wd = int(120 + ew + 90 + tw + 120)
    im = Image.new("RGBA", (Wd, H), bg); im.alpha_composite(em, (120, (H - eh) // 2))
    d = ImageDraw.Draw(im); bbx = d.textbbox((0, 0), 'E', font=f)
    spaced(d, (120 + ew + 90, (H - (bbx[3] - bbx[1])) // 2 - bbx[1]), 'EDGEXHP', f, INK + (255,), 34)
    return im
lockup(PAPER + (255,)).convert('RGB').save('Edgexhp_logo_cream.png')
lockup((0, 0, 0, 0)).save('Edgexhp_logo_transparent.png')
# 3) Etsy big banner 3360x840: soft washes on the right, E + name + tagline on the left
BW, BH = 3360, 840
c = Canvas(BW, BH, seed=21)
for (x, y, r), col, col2 in [((3080, 300, 300), '#e98f86', '#f3b9a8'), ((3300, 640, 280), '#86b7a2', '#b8d8c6'), ((180, 620, 300), '#e9b65b', '#f3d39a'), ((60, 200, 240), '#7ea6c9', '#b3cde3')]:
    c.wash(ellipse(x, y, r, r, 22), col, col2, strength=0.38, layers=36, spread=0.03)
ban = c.on_paper('#fbf6ef').convert('RGBA')
eh = 460; ew = int(e.size[0] * eh / e.size[1])
d = ImageDraw.Draw(ban); f1 = FT(190, 500); f2 = FT(74, 400)
blk = ew + 110 + max(text_w(d, 'EDGEXHP', f1, 30), text_w(d, 'Watercolor mugs, tees & prints', f2, 3))
bx = int((BW - blk) // 2); ban.alpha_composite(e.resize((ew, eh), Image.LANCZOS), (bx, (BH - eh) // 2))
tx = bx + ew + 110
spaced(d, (tx, 205), 'EDGEXHP', f1, INK, 30)
spaced(d, (tx + 6, 470), 'Watercolor mugs, tees & prints', f2, (110, 104, 100), 3)
ban.convert('RGB').save('Edgexhp_banner_3360x840.jpg', quality=92)
# 4) mini banner 1200x160
mini = Image.new('RGB', (1200, 160), PAPER); m = e.resize((int(e.size[0] * 110 / e.size[1]), 110), Image.LANCZOS)
mini.paste(m, (60, 25), m); d = ImageDraw.Draw(mini)
spaced(d, (60 + m.size[0] + 40, 34), 'EDGEXHP', FT(66, 500), INK, 10)
spaced(d, (60 + m.size[0] + 44, 108), 'Watercolor mugs, tees & prints', FT(28, 400), (110, 104, 100), 1)
mini.save('Edgexhp_mini_banner_1200x160.png')
print('ok')
