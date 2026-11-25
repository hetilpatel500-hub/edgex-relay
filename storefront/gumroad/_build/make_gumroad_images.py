"""Gumroad images from the finished Etsy listing images.

Cover: 1280 x 720 (Gumroad's recommended cover size), the 4:3 hero padded to 16:9.
Thumbnail: 600 x 600 square, title card plus a slice of the real product hero.
Bundle: one cover and one thumbnail showing all six heroes.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ETSY = os.path.join(ROOT, 'etsy'); FD = os.path.join(ETSY, '_build', 'fonts')
OUT = os.path.join(ROOT, 'gumroad', 'images')
CREAM = (248, 244, 237); INK = (38, 49, 59); MUTED = (107, 117, 128)
P = [  # folder, short name, accent, kicker
    ('01-freelancer-income-tax-tracker', 'Freelancer Income & Tax Tracker', '#2F7D6D', 'EXCEL + GOOGLE SHEETS'),
    ('02-wedding-budget-planner', 'Wedding Budget Planner', '#9A5B6F', 'EXCEL + GOOGLE SHEETS'),
    ('03-debt-payoff-planner', 'Debt Payoff Planner', '#3F6E8C', 'EXCEL + GOOGLE SHEETS'),
    ('04-home-maintenance-planner', 'Home Maintenance Planner', '#5F826C', 'PRINTABLE PDF'),
    ('05-pet-care-record', 'Pet Care & Health Record', '#B8704F', 'PRINTABLE PDF'),
    ('06-moving-planner', 'Moving Planner', '#50708F', 'PRINTABLE PDF'),
]

def F(n, s):
    return ImageFont.truetype(os.path.join(FD, {'serif': 'Fraunces_600SemiBold.ttf', 'sans': 'DMSans_500Medium.ttf',
                                               'bold': 'DMSans_700Bold.ttf'}[n]), s)

def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def cover(hero):
    h = Image.open(hero).convert('RGB').resize((960, 720), Image.LANCZOS)
    c = Image.new('RGB', (1280, 720), h.getpixel((4, 360)))
    c.paste(Image.new('RGB', (640, 720), h.getpixel((955, 360))), (640, 0))
    c.paste(h, (160, 0)); return c

def thumb(hero, name, acc, kicker):
    S = 1200; c = Image.new('RGB', (S, S), CREAM); d = ImageDraw.Draw(c); a = rgb(acc)
    h = Image.open(hero).convert('RGB')
    shot = h.crop((int(h.width * 0.45), int(h.height * 0.08), h.width, int(h.height * 0.78)))
    shot = shot.resize((S, int(shot.height * S / shot.width)), Image.LANCZOS)
    c.paste(shot, (0, S - shot.height + 60))
    d.rectangle((0, 0, S, 560), fill=CREAM)
    d.text((80, 80), kicker, font=F('bold', 46), fill=a)
    y, fs = 150, 118
    while len(wrap(d, name, F('serif', fs), S - 160)) > 2: fs -= 6
    for ln in wrap(d, name, F('serif', fs), S - 160):
        d.text((80, y), ln, font=F('serif', fs), fill=INK); y += int(fs * 1.12)
    d.rectangle((0, 552, S, 560), fill=a)
    return c.resize((600, 600), Image.LANCZOS)

def bundle():
    heroes = [Image.open(os.path.join(ETSY, p[0], 'images', '01-main.png')).convert('RGB') for p in P]
    cv = Image.new('RGB', (1280, 720), CREAM); d = ImageDraw.Draw(cv)
    d.text((60, 44), 'THE EDGEX LIFE ADMIN BUNDLE', font=F('bold', 30), fill=rgb('#9A5B6F'))
    d.text((60, 84), 'All 6 templates. One download.', font=F('serif', 58), fill=INK)
    tw, th = 372, 279
    for i, h in enumerate(heroes):
        x = 60 + (i % 3) * (tw + 22); y = 190 + (i // 3) * (th + 22)
        cv.paste(h.resize((tw, th), Image.LANCZOS), (x, y))
    S = 1200; tb = Image.new('RGB', (S, S), CREAM); d = ImageDraw.Draw(tb)
    d.text((80, 80), 'BUNDLE · 6 TEMPLATES', font=F('bold', 46), fill=rgb('#9A5B6F'))
    d.text((80, 150), 'Life Admin', font=F('serif', 128), fill=INK)
    d.text((80, 290), 'Bundle', font=F('serif', 128), fill=INK)
    tw, th = 330, 248
    for i, h in enumerate(heroes):
        x = 80 + (i % 3) * (tw + 25); y = 500 + (i // 3) * (th + 25)
        tb.paste(h.resize((tw, th), Image.LANCZOS), (x, y))
    return cv, tb.resize((600, 600), Image.LANCZOS)

os.makedirs(OUT, exist_ok=True)
for folder, name, acc, kick in P:
    hero = os.path.join(ETSY, folder, 'images', '01-main.png')
    cover(hero).save(os.path.join(OUT, f'{folder}_cover.png'))
    thumb(hero, name, acc, kick).save(os.path.join(OUT, f'{folder}_thumb.png'))
cv, tb = bundle()
cv.save(os.path.join(OUT, '00-bundle_cover.png')); tb.save(os.path.join(OUT, '00-bundle_thumb.png'))
print('\n'.join(sorted(os.listdir(OUT))))
