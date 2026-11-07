"""Shared layout kit for Edgex printable planners (reportlab).

Every planner is described as a list of page specs; `build()` renders the
same content at US Letter and A4 so buyers get both sizes.
"""
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
_FONTS = {
    "Sans": "DMSans_400Regular.ttf",
    "SansMed": "DMSans_500Medium.ttf",
    "SansBold": "DMSans_700Bold.ttf",
    "Serif": "Fraunces_400Regular.ttf",
    "SerifSemi": "Fraunces_600SemiBold.ttf",
    "SerifIt": "Fraunces_400Regular_Italic.ttf",
}
for name, f in _FONTS.items():
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, f)))

INK = HexColor("#26313B")
MUTED = HexColor("#6B7580")
LINE = HexColor("#C9D0D4")
PAPER = HexColor("#FBF9F5")


def tint(hex_color, amount):
    """Mix a hex colour with white; amount 0 = colour, 1 = white."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(c + (255 - c) * amount) for c in (r, g, b))
    return HexColor("#%02X%02X%02X" % (r, g, b))


class Planner:
    def __init__(self, path, pagesize, product, accent, footer_note):
        self.c = canvas.Canvas(path, pagesize=pagesize)
        self.W, self.H = pagesize
        self.M = 40
        self.product = product
        self.accent = HexColor(accent)
        self.accent_hex = accent
        self.light = tint(accent, 0.86)
        self.lighter = tint(accent, 0.94)
        self.footer_note = footer_note
        self.page_no = 0
        self.c.setTitle(product)
        self.c.setAuthor("Edgex Studio")
        self.c.setSubject(product + " - printable planner")

    # ---------- page frame ----------
    def new_page(self, title, subtitle=None):
        if self.page_no:
            self.c.showPage()
        self.page_no += 1
        c = self.c
        c.setFillColor(white)
        c.rect(0, 0, self.W, self.H, stroke=0, fill=1)
        top = self.H - self.M
        c.setFillColor(self.accent)
        c.setFont("SansMed", 7.5)
        c.drawString(self.M, top, self.product.upper())
        c.setFillColor(INK)
        c.setFont("SerifSemi", 22)
        c.drawString(self.M, top - 28, title)
        y = top - 38
        c.setStrokeColor(self.accent)
        c.setLineWidth(1.2)
        c.line(self.M, y, self.M + 46, y)
        y -= 16
        if subtitle:
            c.setFillColor(MUTED)
            c.setFont("Sans", 9)
            for ln in simpleSplit(subtitle, "Sans", 9, self.W - 2 * self.M):
                c.drawString(self.M, y, ln)
                y -= 12
            y -= 4
        self._footer()
        return y

    def _footer(self):
        c = self.c
        c.setFont("Sans", 7)
        c.setFillColor(MUTED)
        c.drawString(self.M, 22, self.footer_note)
        c.drawRightString(self.W - self.M, 22, str(self.page_no))

    # ---------- components ----------
    def section(self, y, text):
        c = self.c
        c.setFillColor(self.accent)
        c.setFont("SansBold", 8.5)
        c.drawString(self.M, y, text.upper())
        return y - 14

    def fields(self, y, labels, cols=2, gap=26, x0=None, width=None):
        """Label + write-on line blocks."""
        c = self.c
        x0 = self.M if x0 is None else x0
        width = (self.W - 2 * self.M) if width is None else width
        colw = (width - (cols - 1) * 16) / cols
        for i, lab in enumerate(labels):
            col = i % cols
            if col == 0 and i:
                y -= gap
            x = x0 + col * (colw + 16)
            c.setFillColor(MUTED)
            c.setFont("SansMed", 7)
            c.drawString(x, y, lab.upper())
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.line(x, y - 13, x + colw, y - 13)
        return y - gap - 4

    def table(self, y, columns, rows=None, row_h=21, bottom=None, prefill=None):
        """columns: list of (header, weight). Fills to bottom if rows None."""
        c = self.c
        bottom = 40 if bottom is None else bottom
        width = self.W - 2 * self.M
        tot = sum(w for _, w in columns)
        xs = [self.M]
        for _, w in columns:
            xs.append(xs[-1] + width * w / tot)
        hh = 20
        c.setFillColor(self.light)
        c.rect(self.M, y - hh, width, hh, stroke=0, fill=1)
        c.setFillColor(INK)
        for i, (h, _) in enumerate(columns):
            cw = xs[i + 1] - xs[i] - 8
            fs = 7.2
            lines = simpleSplit(h.upper(), "SansBold", fs, cw)
            if len(lines) > 1:
                fs = 6.2
                lines = simpleSplit(h.upper(), "SansBold", fs, cw)[:2]
                c.setFont("SansBold", fs)
                c.drawString(xs[i] + 5, y - 8.5, lines[0])
                if len(lines) > 1:
                    c.drawString(xs[i] + 5, y - 16, lines[1])
            else:
                c.setFont("SansBold", fs)
                c.drawString(xs[i] + 5, y - 13, lines[0])
        y -= hh
        if rows is None:
            rows = int((y - bottom) // row_h)
        c.setLineWidth(0.6)
        for r in range(rows):
            if r % 2 == 1:
                c.setFillColor(self.lighter)
                c.rect(self.M, y - row_h, width, row_h, stroke=0, fill=1)
            if prefill and r < len(prefill):
                c.setFillColor(INK)
                c.setFont("Sans", 8.2)
                for i, val in enumerate(prefill[r]):
                    if val:
                        cw = xs[i + 1] - xs[i] - 10
                        txt = simpleSplit(val, "Sans", 8.2, cw)
                        if len(txt) == 1:
                            c.drawString(xs[i] + 5, y - row_h / 2 - 3, txt[0])
                        else:
                            c.setFont("Sans", 7.2)
                            txt = simpleSplit(val, "Sans", 7.2, cw)[:2]
                            if len(txt) == 1:
                                c.drawString(xs[i] + 5, y - row_h / 2 - 2.5, txt[0])
                            else:
                                c.drawString(xs[i] + 5, y - row_h / 2 + 1.5, txt[0])
                                c.drawString(xs[i] + 5, y - row_h / 2 - 6.5, txt[1])
                            c.setFont("Sans", 8.2)
            y -= row_h
            c.setStrokeColor(LINE)
            c.line(self.M, y, self.M + width, y)
        c.setStrokeColor(LINE)
        for x in xs[1:-1]:
            c.line(x, y, x, y + rows * row_h)
        return y - 14

    def checklist(self, y, sections, cols=2, fs=8.6, bottom=40, heading_gap=15, x0=None, width=None):
        """sections: list of (heading, [items]). Flows into columns."""
        c = self.c
        x0 = self.M if x0 is None else x0
        width = (self.W - 2 * self.M) if width is None else width
        colw = (width - (cols - 1) * 20) / cols
        col = 0
        top = y
        x = x0
        self._col_low = y
        for heading, items in sections:
            need = heading_gap + 14
            if y - need < bottom:
                self._col_low = min(self._col_low, y)
                col += 1
                if col >= cols:
                    raise ValueError("checklist overflow on page %s" % self.page_no)
                x = x0 + col * (colw + 20)
                y = top
            if heading:
                c.setFillColor(self.accent)
                c.setFont("SansBold", 8)
                c.drawString(x, y, heading.upper())
                y -= heading_gap
            for it in items:
                blank = not it
                lines = [""] if blank else simpleSplit(it, "Sans", fs, colw - 16)
                h = 22 if blank else len(lines) * (fs + 2.4) + 5
                if y - h < bottom:
                    self._col_low = min(self._col_low, y)
                    col += 1
                    if col >= cols:
                        raise ValueError("checklist overflow on page %s" % self.page_no)
                    x = x0 + col * (colw + 20)
                    y = top
                c.setStrokeColor(self.accent)
                c.setLineWidth(0.8)
                c.roundRect(x, y - 2, 8.5, 8.5, 1.5, stroke=1, fill=0)
                if blank:
                    c.setStrokeColor(LINE)
                    c.setLineWidth(0.6)
                    c.line(x + 15, y - 2, x + colw, y - 2)
                c.setFillColor(INK)
                c.setFont("Sans", fs)
                yy = y
                for ln in lines:
                    c.drawString(x + 15, yy, ln)
                    yy -= fs + 2.4
                y -= h
            y -= 6
        return min(y, self._col_low) if col else y

    def two_col_checklist(self, y, left, right, fs=8.8, bottom=40):
        """Explicit two-column checklist: left/right are section lists."""
        w = (self.W - 2 * self.M - 24) / 2
        y1 = self.checklist(y, left, cols=1, fs=fs, bottom=bottom, width=w)
        y2 = self.checklist(y, right, cols=1, fs=fs, bottom=bottom, x0=self.M + w + 24, width=w)
        return min(y1, y2)

    def notes_fill(self, y, label="Notes", bottom=40):
        """Fill leftover space with a labelled lined notes area."""
        if y - bottom < 70:
            return y
        y = self.section(y - 4, label)
        return self.lined(y - 12, bottom=bottom)

    def lined(self, y, bottom=40, gap=22, dotted=False):
        c = self.c
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        if dotted:
            c.setDash(1, 3)
        while y > bottom:
            c.line(self.M, y, self.W - self.M, y)
            y -= gap
        c.setDash()
        return y

    def box(self, x, y, w, h, title=None, lines=0, fill=True):
        c = self.c
        if fill:
            c.setFillColor(self.lighter)
            c.roundRect(x, y - h, w, h, 6, stroke=0, fill=1)
        c.setStrokeColor(self.light)
        c.setLineWidth(0.8)
        c.roundRect(x, y - h, w, h, 6, stroke=1, fill=0)
        yy = y - 16
        if title:
            c.setFillColor(self.accent)
            c.setFont("SansBold", 7.8)
            c.drawString(x + 10, yy, title.upper())
            yy -= 16
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        for _ in range(lines):
            if yy < y - h + 8:
                break
            c.line(x + 10, yy, x + w - 10, yy)
            yy -= 19

    def paragraph(self, y, text, fs=9.4, font="Sans", color=None, width=None, lead=None, x=None):
        c = self.c
        x = self.M if x is None else x
        width = (self.W - 2 * self.M) if width is None else width
        lead = lead or fs * 1.45
        c.setFillColor(color or INK)
        c.setFont(font, fs)
        for ln in simpleSplit(text, font, fs, width):
            c.drawString(x, y, ln)
            y -= lead
        return y - 4

    def month_grid(self, y, row_labels, months=None, label_w=0.34, row_h=19, bottom=40, label_head="TASK"):
        """Rows of tasks x 12 month tick-boxes."""
        c = self.c
        months = months or ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
        width = self.W - 2 * self.M
        lw = width * label_w
        mw = (width - lw) / len(months)
        c.setFillColor(self.light)
        c.rect(self.M, y - 18, width, 18, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("SansBold", 7.2)
        c.drawString(self.M + 5, y - 12, label_head)
        for i, m in enumerate(months):
            c.drawCentredString(self.M + lw + mw * i + mw / 2, y - 12, m)
        y -= 18
        c.setLineWidth(0.6)
        for r, lab in enumerate(row_labels):
            if y - row_h < bottom:
                break
            if r % 2:
                c.setFillColor(self.lighter)
                c.rect(self.M, y - row_h, width, row_h, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("Sans", 7.8)
            txt = simpleSplit(lab, "Sans", 7.8, lw - 10)
            c.drawString(self.M + 5, y - row_h / 2 - 2.8, txt[0] if txt else "")
            for i in range(len(months)):
                cx = self.M + lw + mw * i + mw / 2
                c.setStrokeColor(self.accent)
                c.roundRect(cx - 4.5, y - row_h / 2 - 4.5, 9, 9, 1.5, stroke=1, fill=0)
            y -= row_h
            c.setStrokeColor(LINE)
            c.line(self.M, y, self.M + width, y)
        return y - 12

    def cover(self, title_lines, tagline, contents, badge):
        """Full-bleed cover page."""
        if self.page_no:
            self.c.showPage()
        self.page_no += 1
        c = self.c
        c.setFillColor(PAPER)
        c.rect(0, 0, self.W, self.H, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.rect(0, self.H * 0.58, self.W, self.H * 0.42, stroke=0, fill=1)
        # soft decorative circles
        c.setFillColor(tint(self.accent_hex, 0.18))
        c.circle(self.W - 70, self.H - 60, 120, stroke=0, fill=1)
        c.setFillColor(tint(self.accent_hex, 0.32))
        c.circle(self.W - 30, self.H * 0.62, 60, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("SansMed", 9)
        c.drawString(56, self.H - 70, badge.upper())
        y = self.H - 130
        for ln in title_lines:
            c.setFont("SerifSemi", 42)
            c.drawString(56, y, ln)
            y -= 48
        c.setFont("SerifIt", 14)
        c.drawString(56, y - 4, tagline)
        # contents list
        y = self.H * 0.58 - 50
        c.setFillColor(INK)
        c.setFont("SansBold", 8.5)
        c.drawString(56, y, "INSIDE")
        y -= 20
        colw = (self.W - 112 - 20) / 2
        half = (len(contents) + 1) // 2
        for i, item in enumerate(contents):
            col = 0 if i < half else 1
            row = i if i < half else i - half
            x = 56 + col * (colw + 20)
            yy = y - row * 19
            c.setFillColor(self.accent)
            c.circle(x + 3, yy + 3, 2.4, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("Sans", 9.5)
            c.drawString(x + 12, yy, item)
        c.setFont("Sans", 7.5)
        c.setFillColor(MUTED)
        c.drawString(56, 36, self.footer_note)

    def save(self):
        self.c.showPage()
        self.c.save()


def build(out_dir, basename, product, accent, pages_fn, footer_note):
    """pages_fn(planner) draws all pages. Renders Letter + A4."""
    outs = []
    for label, size in (("US-Letter", letter), ("A4", A4)):
        path = os.path.join(out_dir, "%s_%s.pdf" % (basename, label))
        p = Planner(path, size, product, accent, footer_note)
        pages_fn(p)
        p.save()
        outs.append(path)
    return outs
