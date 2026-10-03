import os
from planner import build

OUT = os.path.join(os.path.dirname(__file__), "..", "04-home-maintenance-planner")
PRODUCT = "Home Maintenance Planner"
FOOT = "Edgex Studio  ·  For personal use  ·  Print as many copies as you need"

MONTHLY = [
    ("Every month", [
        "Test smoke and carbon monoxide alarms",
        "Check the HVAC filter; replace if dirty (often every 1-3 months, per the filter maker)",
        "Look under sinks and around toilets for drips or damp spots",
        "Clean the range hood filter",
        "Clean the garbage disposal and slow drains",
        "Check the fire extinguisher gauge is in the green",
        "Run water in unused sinks, tubs and toilets",
        "Top up water softener salt (if you have one)",
        "Walk the outside: look for pests, damage or standing water",
    ]),
    ("Notes for this month", ["", "", ""]),
]

SEASONS = {
    "Spring": ("Wake the house up after winter. Outside first, then in.", [
        ("Outside", [
            "Look over the roof from the ground for missing or damaged shingles",
            "Clean gutters and downspouts; make sure water drains away from the house",
            "Check exterior paint and caulk around windows and doors",
            "Inspect deck, porch and steps for loose boards or rot",
            "Turn on outdoor faucets and check hoses for leaks",
            "Check that soil slopes away from the foundation",
            "Clean window screens; patch any tears",
        ]),
        ("Inside", [
            "Book an AC service before the hot months",
            "Vacuum refrigerator coils",
            "Test the sump pump (if you have one)",
            "Clean the dryer vent and lint trap housing",
            "Wash windows inside and out",
            "Check attic for signs of leaks or pests",
        ]),
    ]),
    "Summer": ("Keep things cool, dry and pest-free.", [
        ("Outside", [
            "Trim trees and shrubs back from the roof and siding",
            "Check sprinklers and irrigation for leaks or misaligned heads",
            "Clean and, if needed, reseal the deck",
            "Clean the grill and check gas connections",
            "Look for signs of termites or wood damage",
            "Clean trash and recycling bins",
        ]),
        ("Inside", [
            "Set ceiling fans to spin counterclockwise",
            "Test the garage door auto-reverse safety feature",
            "Check attic ventilation and look for moisture",
            "Inspect washing machine hoses for bulges or cracks",
            "Clean the dishwasher filter",
            "Check for leaks at the water heater",
        ]),
    ]),
    "Fall": ("Get ready for cold weather before it arrives.", [
        ("Outside", [
            "Clean gutters again once most leaves have fallen",
            "Disconnect hoses and shut off / drain outdoor faucets",
            "Winterize the irrigation system",
            "Rake leaves and clear storm drains near the house",
            "Store patio furniture and cushions",
            "Stock winter supplies: ice melt, shovel, scraper",
        ]),
        ("Inside", [
            "Book a furnace or heating service",
            "Set ceiling fans to clockwise on low",
            "Seal drafts: weatherstripping and caulk at doors and windows",
            "Have the chimney inspected before using the fireplace",
            "Flush the water heater (per the manufacturer's guide)",
            "Test the backup generator (if you have one)",
        ]),
    ]),
    "Winter": ("Protect the pipes and keep an eye on the roof.", [
        ("Outside", [
            "Watch for ice dams and large icicles along the roof edge",
            "Keep dryer, furnace and other exhaust vents clear of snow",
            "Clear snow away from gas meter and foundation",
            "Check trees for heavy or broken limbs",
        ]),
        ("Inside", [
            "Insulate pipes in unheated spaces; know your main shutoff",
            "Check basement and attic for leaks or condensation",
            "Replace alarm batteries (unless they are sealed 10-year units)",
            "Re-caulk around tubs, showers and sinks where needed",
            "Tighten loose handles, knobs, hinges and railings",
            "Clean the washer gasket and run a cleaning cycle",
            "Review your emergency kit and flashlights",
            "Plan and price spring projects",
        ]),
    ]),
}

ANNUAL = [
    "Replace HVAC filter", "Test smoke & CO alarms", "Clean gutters", "AC service",
    "Furnace / heat service", "Flush water heater", "Clean dryer vent",
    "Vacuum fridge coils", "Chimney inspection", "Roof check",
    "Pest inspection", "Septic service (if any)", "Caulk & weatherstrip",
    "Seal deck / fence", "Winterize outdoor water", "", "", "", "",
]


def pages(p):
    p.cover(["Home", "Maintenance", "Planner"], "Keep your home in good shape, one season at a time.",
            ["Home at a glance", "Emergency shutoffs", "Monthly checklist", "4 seasonal checklists",
             "Year-at-a-glance schedule", "Appliance & warranty record", "Maintenance log",
             "Service provider directory", "Project planner", "Repair budget tracker",
             "Paint & finishes record", "Home inventory", "Notes"],
            "Printable planner  ·  Letter + A4")

    y = p.new_page("How to use this planner")
    y = p.paragraph(y, "This planner keeps everything about your home in one place: what needs doing, when you last did it, "
                       "who you called and what it cost. Print it, punch it and keep it in a binder, or write on it in any "
                       "note-taking app that lets you mark up a PDF.")
    tips = [
        ("1. Fill in the basics", "Start with Home at a glance and Emergency shutoffs. These are the pages you will want in a hurry."),
        ("2. Pick your rhythm", "Use the Monthly checklist every month and the matching Seasonal checklist four times a year. Add your own tasks in the blank lines."),
        ("3. Plan the year", "Tick the months you plan to do each job on the Year-at-a-glance page. Blank rows are for your home's extras."),
        ("4. Log as you go", "Every repair, service call and purchase goes in the Maintenance log. It makes warranty claims, insurance and selling the house much easier."),
        ("5. Print what you need", "Print extra copies of any log page. Most pages work for renters too."),
    ]
    for h, t in tips:
        y -= 6
        y = p.paragraph(y, h, fs=11, font="SerifSemi", color=p.accent)
        y = p.paragraph(y + 2, t)
    y -= 10
    p.box(p.M, y, p.W - 2 * p.M, 70, "A friendly note")
    p.paragraph(y - 34, "Checklists are general reminders, not professional advice. Always follow your manufacturer's instructions, "
                        "and call a licensed pro for gas, electrical and roof work.", fs=8.6, color=p.accent, width=p.W - 2 * p.M - 24, x=p.M + 10)

    y = p.new_page("Home at a glance", "The facts you keep looking up, all on one page.")
    y = p.section(y, "The house")
    y = p.fields(y, ["Home nickname", "Move-in date", "Year built", "Square footage", "Lot size", "Bedrooms / baths",
                     "Roof type & year", "Siding / exterior", "Heating type", "Cooling type",
                     "Water heater (type & year)", "Water source (city / well)", "Sewer / septic", "HOA contact"], cols=2)
    y = p.section(y, "Sizes & parts")
    y = p.table(y, [("Item", 3), ("Size / part number", 3), ("Where to buy", 3), ("How often", 2)],
                prefill=[["HVAC filter"], ["Fridge water filter"], ["Furnace humidifier pad"], ["Light bulbs (main)"],
                         ["Faucet aerators"], ["Smoke alarm batteries"], [""], [""]], rows=8, row_h=20)

    y = p.new_page("Emergency info", "Know where these are before you need them. Show everyone in the house.")
    y = p.section(y, "Shutoffs & key locations")
    y = p.table(y, [("What", 3), ("Where it is", 5), ("How to shut off / notes", 5)],
                prefill=[["Main water shutoff"], ["Gas shutoff"], ["Electrical panel"], ["Water heater shutoff"],
                         ["Sprinkler / irrigation valve"], ["Sump pump"], ["Fire extinguishers"], ["First aid kit"],
                         ["Spare keys"], [""]], rows=10, row_h=22)
    y = p.section(y, "Emergency & utility contacts")
    p.table(y, [("Who", 3), ("Company", 4), ("Phone", 3), ("Account #", 3)],
            prefill=[["Electric utility"], ["Gas utility"], ["Water utility"], ["Plumber"], ["Electrician"],
                     ["HVAC company"], ["Insurance agent"], ["Neighbor"], [""]])

    y = p.new_page("Monthly checklist", "Ten minutes a month keeps small problems small. Print one for each month.")
    y = p.fields(y, ["Month", "Done by"], cols=2)
    y = p.checklist(y, MONTHLY[:1], cols=1, fs=10)
    p.notes_fill(y, "Notes, repairs spotted, things to buy")

    for season, (sub, secs) in SEASONS.items():
        y = p.new_page(season + " checklist", sub)
        y = p.fields(y, ["Year", "Started on"], cols=2)
        y = p.two_col_checklist(y, [secs[0]], [secs[1]], fs=9.2)
        y = p.checklist(y - 4, [("My own " + season.lower() + " tasks", ["", "", "", ""])], cols=2, fs=9.2)
        p.notes_fill(y, "Notes")

    y = p.new_page("Year at a glance", "Tick the month you plan to do each job. Circle the tick when it is done.")
    y = p.fields(y, ["Year"], cols=2)
    p.month_grid(y, ANNUAL, row_h=26)

    y = p.new_page("Appliances & systems", "Model and serial numbers are usually on a sticker inside the door or on the back.")
    p.table(y, [("Item", 3), ("Brand & model", 4), ("Serial #", 3), ("Bought", 2), ("Warranty until", 2.4), ("Manual kept", 2)],
            prefill=[["Furnace"], ["AC / heat pump"], ["Water heater"], ["Refrigerator"], ["Dishwasher"], ["Range / oven"],
                     ["Microwave"], ["Washer"], ["Dryer"], ["Garage door opener"], ["Water softener"], ["Sump pump"]], row_h=27)

    for n in (1, 2):
        y = p.new_page("Maintenance log", "Every repair, service and upgrade. Your future self (and buyer) will thank you.")
        p.table(y, [("Date", 2), ("Task / repair", 5), ("Area", 2.4), ("Done by", 2.6), ("Cost", 1.8), ("Notes", 4)], row_h=24)

    y = p.new_page("Service providers", "People you trust, and a few you would not call again.")
    p.table(y, [("Service", 2.6), ("Company / person", 4), ("Phone / email", 4), ("Last used", 2), ("Rating", 1.6), ("Notes", 3.2)],
            prefill=[["Plumber"], ["Electrician"], ["HVAC"], ["Roofer"], ["Handyman"], ["Pest control"], ["Lawn care"],
                     ["Cleaner"], ["Locksmith"], ["Appliance repair"], ["Gutter cleaning"], ["Painter"]], row_h=30)

    y = p.new_page("Project planner", "One page per project: plan it, price it, then do it.")
    y = p.fields(y, ["Project", "Room / area", "Goal", "Target finish", "Budget", "DIY or hire?"], cols=2)
    y = p.section(y, "Materials & costs")
    y = p.table(y, [("Item", 5), ("Qty", 1.3), ("Store", 3), ("Est. cost", 2), ("Actual", 2), ("Bought", 1.5)], rows=9, row_h=20)
    y = p.section(y, "Steps")
    y = p.checklist(y - 2, [("", ["", "", "", "", ""])], cols=2, fs=9.2)
    p.notes_fill(y, "Notes & measurements")

    y = p.new_page("Repair & project budget", "Track what the house really costs you each year.")
    y = p.fields(y, ["Year", "Yearly budget"], cols=2)
    p.table(y, [("Date", 2), ("What", 5), ("Category", 3), ("Planned", 2), ("Actual", 2), ("Paid with", 2.4)], row_h=23)

    y = p.new_page("Paint & finishes", "Never guess the paint colour again.")
    p.table(y, [("Room / surface", 3), ("Brand", 2.6), ("Colour name & code", 4), ("Finish", 2), ("Date", 1.8), ("Leftover kept?", 2.2)],
            prefill=[["Living room"], ["Kitchen"], ["Primary bedroom"], ["Bathroom"], ["Hallways"], ["Trim & doors"],
                     ["Ceilings"], ["Front door"], ["Exterior"]], row_h=30)

    y = p.new_page("Home inventory", "A simple record for insurance. Take a photo of each item too.")
    p.table(y, [("Item", 4), ("Room", 2.4), ("Brand / serial #", 4), ("Bought", 2), ("Value", 2), ("Photo", 1.5)], row_h=23)

    y = p.new_page("Notes")
    p.lined(y - 6, dotted=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in build(OUT, "Home-Maintenance-Planner", PRODUCT, "#5F826C", pages, FOOT):
        print(f)
