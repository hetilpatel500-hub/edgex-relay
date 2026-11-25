"""Shared styling for Edgex spreadsheet templates (openpyxl).

Fonts are Arial so the files look the same in Excel, Google Sheets and
LibreOffice. Cream cells = type here. White cells = formulas.
"""
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

INK = "26313B"
MUTED = "6B7580"
INPUT = "FFF8E8"
LINE = "D9DEE2"
WHITE = "FFFFFF"


def tint(hex6, amount):
    r, g, b = (int(hex6[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(c + (255 - c) * amount) for c in (r, g, b))
    return "%02X%02X%02X" % (r, g, b)


class Kit:
    def __init__(self, accent):
        self.accent = accent
        self.light = tint(accent, 0.82)
        self.lighter = tint(accent, 0.92)
        thin = Side(style="thin", color=LINE)
        self.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        self.bottom = Border(bottom=thin)

    def fill(self, color):
        return PatternFill("solid", start_color=color, end_color=color)

    def sheet_setup(self, ws, widths, tab=None, landscape=True, gridlines=False):
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.sheet_view.showGridLines = gridlines
        if tab:
            ws.sheet_properties.tabColor = tab
        ws.page_setup.orientation = "landscape" if landscape else "portrait"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_options.horizontalCentered = True
        ws.page_margins.left = ws.page_margins.right = 0.4
        ws.page_margins.top = ws.page_margins.bottom = 0.5

    def title(self, ws, text, sub=None, span=8):
        ws.row_dimensions[1].height = 10
        ws["B2"] = text
        ws["B2"].font = Font(name="Georgia", size=20, bold=True, color=INK)
        ws.row_dimensions[2].height = 32
        if sub:
            ws["B3"] = sub
            ws["B3"].font = Font(name="Arial", size=10, color=MUTED)
        for c in range(2, 2 + span):
            ws.cell(row=4, column=c).border = Border(top=Side(style="medium", color=self.accent))
        ws.row_dimensions[4].height = 8

    def label(self, cell, text, size=9, bold=True, color=None):
        cell.value = text
        cell.font = Font(name="Arial", size=size, bold=bold, color=color or MUTED)
        cell.alignment = Alignment(vertical="center")

    def section(self, cell, text):
        cell.value = text.upper()
        cell.font = Font(name="Arial", size=9, bold=True, color=self.accent)

    def header_row(self, ws, row, col, headers, height=30):
        for i, h in enumerate(headers):
            c = ws.cell(row=row, column=col + i, value=h)
            c.font = Font(name="Arial", size=9, bold=True, color=WHITE)
            c.fill = self.fill(self.accent)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border = self.border
        ws.row_dimensions[row].height = height

    def body(self, cell, fmt=None, inp=False, bold=False, align=None, color=None, band=False, size=10):
        cell.font = Font(name="Arial", size=size, bold=bold, color=color or INK)
        if inp:
            cell.fill = self.fill(INPUT)
        elif band:
            cell.fill = self.fill(self.lighter)
        cell.border = self.border
        if fmt:
            cell.number_format = fmt
        cell.alignment = Alignment(horizontal=align, vertical="center") if align else Alignment(vertical="center")

    def kpi(self, ws, row, col, label, formula, fmt, width_cols=2):
        top = ws.cell(row=row, column=col, value=label.upper())
        top.font = Font(name="Arial", size=8, bold=True, color=MUTED)
        top.fill = self.fill(self.lighter)
        top.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        val = ws.cell(row=row + 1, column=col, value=formula)
        val.font = Font(name="Georgia", size=18, bold=True, color=INK)
        val.fill = self.fill(self.lighter)
        val.number_format = fmt
        val.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        if width_cols > 1:
            ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + width_cols - 1)
            ws.merge_cells(start_row=row + 1, start_column=col, end_row=row + 1, end_column=col + width_cols - 1)
        ws.row_dimensions[row + 1].height = 34

    def list_validation(self, ws, rng, source, prompt=None):
        dv = DataValidation(type="list", formula1=source, allow_blank=True, showErrorMessage=False)
        if prompt:
            dv.promptTitle = "Pick from list"
            dv.prompt = prompt
            dv.showInputMessage = True
        ws.add_data_validation(dv)
        dv.add(rng)
        return dv

    def note(self, ws, cell, text, color=None, size=9, italic=False, wrap=False):
        ws[cell] = text
        ws[cell].font = Font(name="Arial", size=size, color=color or MUTED, italic=italic)
        if wrap:
            ws[cell].alignment = Alignment(wrap_text=True, vertical="top")

    def start_here(self, ws, title, intro, steps, notes, legend=True):
        """A friendly instruction tab."""
        self.sheet_setup(ws, [3, 4, 90, 3], tab=self.accent, landscape=False)
        ws.row_dimensions[1].height = 14
        ws["C2"] = title
        ws["C2"].font = Font(name="Georgia", size=24, bold=True, color=INK)
        ws.row_dimensions[2].height = 40
        ws["C3"] = intro
        ws["C3"].font = Font(name="Arial", size=11, color=MUTED)
        ws["C3"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[3].height = 48
        r = 5
        self.section(ws.cell(row=r, column=3), "How to use it")
        r += 1
        for i, s in enumerate(steps, start=1):
            ws.cell(row=r, column=2, value=i).font = Font(name="Georgia", size=12, bold=True, color=self.accent)
            ws.cell(row=r, column=2).alignment = Alignment(horizontal="center", vertical="top")
            c = ws.cell(row=r, column=3, value=s)
            c.font = Font(name="Arial", size=10.5, color=INK)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = 16 * max(1, (len(s) // 95) + 1) + 4
            r += 1
        if legend:
            r += 1
            self.section(ws.cell(row=r, column=3), "Cell colours")
            r += 1
            ws.cell(row=r, column=2).fill = self.fill(INPUT)
            ws.cell(row=r, column=2).border = self.border
            ws.cell(row=r, column=3, value="Cream cells are for typing. Everything else calculates on its own.").font = Font(name="Arial", size=10.5, color=INK)
            r += 1
        r += 1
        self.section(ws.cell(row=r, column=3), "Good to know")
        r += 1
        for n in notes:
            c = ws.cell(row=r, column=3, value=n)
            c.font = Font(name="Arial", size=10, color=MUTED)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = 15 * max(1, (len(n) // 100) + 1) + 4
            r += 1
        return r
