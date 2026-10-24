"""Render listing images for all six products.

Usage: python3 make_images.py <samples_dir>
<samples_dir> must hold the sample-filled spreadsheets printed to PDF:
  python3 build_debt.py <samples_dir>   (and build_freelancer / build_wedding)
  soffice --headless --convert-to pdf --outdir <samples_dir>/pdf <samples_dir>/*_SAMPLE.xlsx
"""
import os
import sys
import pymupdf
from PIL import Image
import listing_images as LI

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def pages(pdf, dpi=170):
    out = []
    for p in pymupdf.open(pdf):
        pm = p.get_pixmap(dpi=dpi)
        out.append(Image.frombytes("RGB", [pm.width, pm.height], pm.samples))
    return out


def sheet_pages(samples, name):
    return [LI.trim(p) for p in pages(os.path.join(samples, "pdf", name + "_SAMPLE.pdf"), dpi=200)]


SHEET_STEPS = [("Download", "Find the file under Purchases on Etsy right after you buy."),
               ("Open", "Open it in Microsoft Excel, or upload it to Google Drive and open it with Google Sheets."),
               ("Fill in", "Type in the cream cells. Totals, dates and charts update by themselves.")]
PDF_STEPS = [("Download", "Find the PDFs under Purchases on Etsy right after you buy."),
             ("Print or go digital", "Print at home on Letter or A4, or write on it in a PDF note-taking app."),
             ("Use it", "Fill in the pages you need. Print extra log pages any time.")]
SAMPLE_NOTE = "Shown with sample data. Your file comes blank."


def specs(samples):
    fr = sheet_pages(samples, "Freelancer-Income-Tax-Tracker")
    wd = sheet_pages(samples, "Wedding-Budget-Planner")
    db = sheet_pages(samples, "Debt-Payoff-Planner")
    hm = pages(os.path.join(ROOT, "04-home-maintenance-planner", "Home-Maintenance-Planner_US-Letter.pdf"))
    pt = pages(os.path.join(ROOT, "05-pet-care-record", "Pet-Care-Health-Record_US-Letter.pdf"))
    mv = pages(os.path.join(ROOT, "06-moving-planner", "Moving-Planner_US-Letter.pdf"))
    return {
        "01-freelancer-income-tax-tracker": dict(
            kind="sheet", accent="#2F7D6D", kicker="Excel + Google Sheets template",
            title=["Freelancer", "Income & Tax", "Tracker"],
            subtitle="Track income and expenses, and know what to set aside for tax.",
            bullets=["Income, expenses and invoices in one file", "Monthly and quarterly tax set-aside",
                     "Dashboard with chart, updates by itself"],
            badge="Excel + Google Sheets", hero_shots=[fr[1], fr[6]], sample_note=SAMPLE_NOTE,
            inside_sub="8 tabs that work together", inside_cols=4,
            inside=[(fr[0], "Start here guide"), (fr[1], "Dashboard"), (fr[2], "Setup"), (fr[3], "Income log"),
                    (fr[4], "Expense log"), (fr[5], "Invoices"), (fr[6], "Monthly & tax"), (fr[7], "Breakdown")],
            features=[
                dict(kicker="Tax set-aside", headline="Know what to put aside, every month",
                     points=["Set-aside worked out each month from your income minus deductible expenses",
                             "Quarterly totals with editable due dates (US dates filled in)",
                             "Log what you paid and see what is left"],
                     shot=fr[6]),
                dict(kicker="Dashboard", headline="Your whole year at a glance",
                     points=["Income, all expenses, and income minus deductible expenses", "Tax set aside, tax paid and unpaid invoices",
                             "Monthly chart that updates itself"],
                     shot=fr[1]),
            ],
            steps=SHEET_STEPS,
            get=["1 Excel file (.xlsx), 8 tabs", "1 quick-start PDF guide", "Room for 500 income + 500 expense rows"],
            know=["Digital download. Nothing is shipped.", "Tracks savings for tax. Not tax advice.", "Excel or Google Sheets needed (not included)."]),

        "02-wedding-budget-planner": dict(
            kind="sheet", accent="#9A5B6F", kicker="Excel + Google Sheets template",
            title=["Wedding", "Budget", "Planner"],
            subtitle="Budget, payments, guests and to-dos in one calm place.",
            bullets=["Split your budget by category", "Track deposits and due dates",
                     "Guest list with RSVPs and meal choices", "Planning checklist by month"],
            badge="Excel + Google Sheets", hero_shots=[wd[1], wd[2]], sample_note=SAMPLE_NOTE,
            inside_sub="6 tabs that work together", inside_cols=3,
            inside=[(wd[0], "Start here guide"), (wd[1], "Dashboard"), (wd[2], "Budget plan"),
                    (wd[3], "Costs & payments"), (wd[4], "Guest list & RSVPs"), (wd[5], "Planning checklist")],
            features=[
                dict(kicker="Budget plan", headline="Stay on plan, category by category",
                     points=["Set your total and split it by %", "Committed, paid and still-to-pay add up for you",
                             "A category turns red if it goes over"],
                     shot=wd[2]),
                dict(kicker="Dashboard", headline="Your wedding at a glance",
                     points=["Days to go, money committed, paid and still to pay", "Overdue payments and cost per guest",
                             "RSVP counts and checklist progress"],
                     shot=wd[1]),
            ],
            steps=SHEET_STEPS,
            get=["1 Excel file (.xlsx), 6 tabs", "1 quick-start PDF guide", "Room for 300 invitations"],
            know=["Digital download. Nothing is shipped.", "Budget split is a starting point you can change.", "Excel or Google Sheets needed (not included)."]),

        "03-debt-payoff-planner": dict(
            kind="sheet", accent="#3F6E8C", kicker="Excel + Google Sheets template",
            title=["Debt Payoff", "Planner"],
            subtitle="Snowball or avalanche? See your debt-free date for both.",
            bullets=["Up to 10 debts", "Compare snowball, avalanche and minimums",
                     "Payoff order and interest for each debt", "Monthly progress log"],
            badge="Excel + Google Sheets", hero_shots=[db[2], db[1]], sample_note=SAMPLE_NOTE,
            inside_sub="7 tabs that work together", inside_cols=4,
            inside=[(db[0], "Start here guide"), (db[1], "My debts"), (db[2], "Compare methods"),
                    (db[3], "Snowball schedule"), (db[4], "Avalanche schedule"), (db[5], "Minimum-only schedule"),
                    (db[6], "Progress log")],
            features=[
                dict(kicker="Compare", headline="See which method works for you",
                     points=["Debt-free date and total interest for each method",
                             "Interest saved compared with paying minimums",
                             "Payoff order and date for every debt"],
                     shot=db[2]),
                dict(kicker="Your plan", headline="Type your debts once. That is it.",
                     points=["Balance, APR and minimum for up to 10 debts", "Pick snowball or avalanche from a dropdown",
                             "Month-by-month schedule for up to 25 years"],
                     shot=db[1]),
            ],
            steps=SHEET_STEPS,
            get=["1 Excel file (.xlsx), 7 tabs", "1 quick-start PDF guide", "Schedules for up to 25 years"],
            know=["Digital download. Nothing is shipped.", "Estimates for planning. Not financial advice.", "Excel or Google Sheets needed (not included)."]),

        "04-home-maintenance-planner": dict(
            kind="pdf", accent="#5F826C", kicker="Printable PDF planner",
            title=["Home", "Maintenance", "Planner"],
            subtitle="Keep your home in good shape, one season at a time.",
            bullets=["19 pages, US Letter + A4", "Monthly + 4 seasonal checklists",
                     "Appliance, warranty and repair logs", "Emergency shutoffs page"],
            badge="Letter + A4 PDF", hero_shots=[hm[0], hm[5]],
            inside_sub="19 printable pages", inside_cols=4,
            inside=[(hm[2], "Home at a glance"), (hm[3], "Emergency info"), (hm[4], "Monthly checklist"),
                    (hm[5], "Seasonal checklists"), (hm[9], "Year at a glance"), (hm[10], "Appliances & warranties"),
                    (hm[11], "Maintenance log"), (hm[14], "Project planner")],
            features=[
                dict(kicker="Seasonal checklists", headline="Know what to do each season",
                     points=["Spring, summer, fall and winter lists", "Split into outside and inside jobs",
                             "Blank lines for your own home's tasks"],
                     shot=hm[5]),
                dict(kicker="Year at a glance", headline="Plan the whole year on one page",
                     points=["15 common jobs plus blank rows", "Tick the month you plan to do each one",
                             "Pairs with the maintenance log"],
                     shot=hm[9]),
            ],
            steps=PDF_STEPS,
            get=["1 PDF, US Letter (8.5 x 11 in)", "1 PDF, A4", "19 pages in each"],
            know=["Digital download. Nothing is shipped.", "Print as many copies as you need.", "General reminders, not professional advice."]),

        "05-pet-care-record": dict(
            kind="pdf", accent="#B8704F", kicker="Printable PDF planner",
            title=["Pet Care", "& Health", "Record"],
            subtitle="Everything your vet, sitter and you need, in one place.",
            bullets=["17 pages, US Letter + A4", "Vaccines, meds and vet visits",
                     "Monthly prevention tracker", "Pet sitter info sheet"],
            badge="Letter + A4 PDF", hero_shots=[pt[0], pt[2]],
            inside_sub="17 printable pages", inside_cols=4,
            inside=[(pt[2], "Pet profile"), (pt[3], "Vet & emergency contacts"), (pt[4], "Vaccination record"),
                    (pt[5], "Medication log"), (pt[6], "Vet visit log"), (pt[8], "Prevention tracker"),
                    (pt[12], "Weekly care log"), (pt[14], "Pet sitter sheet")],
            features=[
                dict(kicker="Pet profile", headline="All their details on one page",
                     points=["Microchip, license and insurance numbers", "Allergies, quirks and ongoing conditions",
                             "A space for their photo"],
                     shot=pt[2]),
                dict(kicker="Monthly tracker", headline="Never lose track of a monthly dose",
                     points=["Tick flea, tick and heartworm doses by month", "Nails, baths, ears and teeth too",
                             "Blank rows for what your vet recommends"],
                     shot=pt[8]),
            ],
            steps=PDF_STEPS,
            get=["1 PDF, US Letter (8.5 x 11 in)", "1 PDF, A4", "17 pages in each"],
            know=["Digital download. Nothing is shipped.", "Print a set for each pet.", "A record-keeper, not veterinary advice."]),

        "06-moving-planner": dict(
            kind="pdf", accent="#50708F", kicker="Printable PDF planner",
            title=["Moving", "Planner"],
            subtitle="A calm, week-by-week plan for moving house.",
            bullets=["17 pages, US Letter + A4", "8-week countdown checklist",
                     "Budget, quotes and box inventory", "Change of address list"],
            badge="Letter + A4 PDF", hero_shots=[mv[0], mv[3]],
            inside_sub="17 printable pages", inside_cols=4,
            inside=[(mv[2], "Move overview"), (mv[3], "8-week countdown"), (mv[5], "Moving day"), (mv[6], "Moving budget"),
                    (mv[7], "Quote comparison"), (mv[8], "Change of address"), (mv[10], "Room-by-room packing"),
                    (mv[11], "Box inventory")],
            features=[
                dict(kicker="Countdown", headline="Week by week, nothing forgotten",
                     points=["Tasks from 8 weeks out to moving day", "Blank lines for your own jobs",
                             "Notes space on every page"],
                     shot=mv[3]),
                dict(kicker="Moving day", headline="Moving day and first night, sorted",
                     points=["Morning and new-home checklists", "First-night box packing list",
                             "Keep this page with you, not in a box"],
                     shot=mv[5]),
            ],
            steps=PDF_STEPS,
            get=["1 PDF, US Letter (8.5 x 11 in)", "1 PDF, A4", "17 pages in each"],
            know=["Digital download. Nothing is shipped.", "Print as many copies as you need.", "Works for renters and owners."]),
    }


if __name__ == "__main__":
    samples = sys.argv[1]
    only = sys.argv[2:] or None
    for folder, spec in specs(samples).items():
        if only and folder not in only:
            continue
        for p in LI.make_all(spec, os.path.join(ROOT, folder, "images")):
            print(p)
