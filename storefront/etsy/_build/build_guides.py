"""Quick-start PDF guides shipped with each spreadsheet, plus a ZIP bundle."""
import os
import zipfile
from reportlab.lib.pagesizes import letter
from planner import Planner

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FOOT = "Edgex Studio  ·  Questions? Message us on Etsy"

COMMON_OPEN = [
    ("Microsoft Excel (Windows or Mac)", "Double-click the .xlsx file. If you see a yellow 'Protected View' or 'Enable Editing' bar, click Enable Editing."),
    ("Google Sheets (free)", "Go to drive.google.com, click New > File upload and pick the .xlsx file. Then right-click it > Open with > Google Sheets. "
                             "In Sheets, use File > Save as Google Sheets so you edit a Google copy."),
    ("Apple Numbers / LibreOffice", "The file opens in both, but it was designed for Excel and Google Sheets, so some colours or charts may look different."),
    ("Phone or tablet", "Works in the Excel and Google Sheets apps, but a computer is much easier for setting it up."),
]

GUIDES = {
    "01-freelancer-income-tax-tracker": dict(
        name="Freelancer Income & Tax Tracker", file="Freelancer-Income-Tax-Tracker", accent="#2F7D6D",
        tabs=[("Start Here", "The same steps as this guide, inside the file."),
              ("Dashboard", "Income, expenses, profit, tax set aside and unpaid invoices for the year, plus a monthly chart."),
              ("Setup", "Tax year, business name, set-aside %, income goal, your clients and expense categories."),
              ("Income", "One row per payment you receive. 500 rows."),
              ("Expenses", "One row per business cost. The deductible part fills in from your category. 500 rows."),
              ("Invoices", "What you billed, when it is due, and whether it is paid. Overdue ones turn red. 200 rows."),
              ("Monthly & Tax", "Profit and set-aside by month and by quarter. Record the tax payments you make here."),
              ("Breakdown", "Totals by expense category and by client.")],
        tips=["Start a fresh copy of the file for each tax year.",
              "Cream cells are for typing. White cells calculate, so please leave them alone.",
              "The quarter dates are the US federal estimated-tax dates. Type your own if you are elsewhere.",
              "This file helps you save for tax. It does not work out the tax you owe and is not tax advice."]),
    "02-wedding-budget-planner": dict(
        name="Wedding Budget Planner", file="Wedding-Budget-Planner", accent="#9A5B6F",
        tabs=[("Start Here", "The same steps as this guide, inside the file."),
              ("Dashboard", "Wedding date, days to go, money committed and paid, overdue payments, RSVPs and checklist progress."),
              ("Budget", "Your total budget and the % split by category. Shows planned vs committed vs paid."),
              ("Costs", "Each vendor or purchase with cost, paid so far and next due date. 150 rows."),
              ("Guests", "Each invitation, party size, RSVP, meal, table, gift and thank-you. 300 rows."),
              ("Checklist", "A month-by-month planning timeline. Mark tasks Done or Skip.")],
        tips=["Change the % split on Budget until the check says 'Adds up to 100%'.",
              "Party size counts people, so a couple on one invitation is a party of 2.",
              "Cream cells are for typing. White cells calculate, so please leave them alone.",
              "Share the Google Sheets copy with your partner so you both see the same numbers."]),
    "03-debt-payoff-planner": dict(
        name="Debt Payoff Planner", file="Debt-Payoff-Planner", accent="#3F6E8C",
        tabs=[("Start Here", "The same steps as this guide, inside the file."),
              ("My Debts", "Type up to 10 debts, your start month and extra payment, and pick your method."),
              ("Compare", "Debt-free date, months, total interest and interest saved for snowball, avalanche and minimums only. Payoff order for each."),
              ("Snowball / Avalanche / Minimum Only", "Month-by-month schedules for up to 25 years."),
              ("Progress Log", "Write down what you really owe each month and watch the progress bar grow.")],
        tips=["Type APR as a plain number: 22.99 means 22.99%.",
              "Snowball pays the smallest balance first. Avalanche pays the highest APR first.",
              "Interest is estimated monthly (balance x APR / 12). Lenders often charge daily, so their figures will differ a little.",
              "This is a planning tool, not financial advice. Check payoff amounts with your lender."]),
}


def guide(folder, g):
    path = os.path.join(ROOT, folder, g["file"] + "_Quick-Start-Guide.pdf")
    p = Planner(path, letter, g["name"], g["accent"], FOOT)
    y = p.new_page("Quick start", "Thank you for your purchase. Here is how to get going in five minutes.")
    y = p.section(y, "1. Open the file")
    for h, t in COMMON_OPEN:
        y = p.paragraph(y, h, fs=10.5, font="SansBold", color=p.accent)
        y = p.paragraph(y + 3, t, fs=9.4)
    y -= 6
    y = p.section(y, "2. What each tab does")
    for h, t in g["tabs"]:
        y = p.paragraph(y, h, fs=10.5, font="SansBold", color=p.accent)
        y = p.paragraph(y + 3, t, fs=9.4)
    y = p.new_page("Good to know")
    for t in g["tips"]:
        y = p.paragraph(y, "·  " + t, fs=10)
    y -= 10
    p.box(p.M, y, p.W - 2 * p.M, 96, "Something not working?")
    p.paragraph(y - 34, "Re-download the original file any time from Etsy: You > Purchases > Download files. "
                        "Still stuck? Send us a message through Etsy and we will help.",
                fs=9.6, color=p.accent, width=p.W - 2 * p.M - 24, x=p.M + 10)
    p.save()
    return path


if __name__ == "__main__":
    for folder, g in GUIDES.items():
        pdf = guide(folder, g)
        xlsx = os.path.join(ROOT, folder, g["file"] + ".xlsx")
        z = os.path.join(ROOT, folder, g["file"] + ".zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(xlsx, os.path.basename(xlsx))
            zf.write(pdf, os.path.basename(pdf))
        print(pdf, z)
