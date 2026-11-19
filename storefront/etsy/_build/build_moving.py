import os
from planner import build

OUT = os.path.join(os.path.dirname(__file__), "..", "06-moving-planner")
PRODUCT = "Moving Planner"
FOOT = "Edgex Studio  ·  For personal use  ·  Print as many copies as you need"

COUNT_A = [
    ("8 weeks before", [
        "Set a moving budget (see Moving budget page)",
        "Start a folder for quotes, receipts and contracts",
        "Get 3 quotes from movers or truck rental companies",
        "Walk each room and decide what to keep, sell, donate or toss",
        "Measure large furniture and check it fits the new place",
        "If renting: check your notice period and give notice",
        "If you have kids: ask about school records and transfers",
    ]),
    ("6 weeks before", [
        "Book movers or a truck and confirm the date in writing",
        "Order boxes, tape, markers and packing paper",
        "Start packing rooms you use least",
        "Sell or donate what you are not taking",
        "Ask your vet for pet records if you are changing vets",
        "Book time off work for moving day",
    ]),
    ("4 weeks before", [
        "Update your address with the post office",
        "Schedule utility shut-off (old home) and set-up (new home)",
        "Arrange internet install at the new place",
        "Update address with bank, employer and insurance",
        "Use up frozen food and pantry items",
        "Arrange child or pet care for moving day",
    ]),
]
COUNT_B = [
    ("2 weeks before", [
        "Confirm the moving company, time and address details",
        "Refill any prescriptions",
        "Return borrowed items and library books",
        "Pack most rooms; label every box with room + contents",
        "Plan parking or elevator booking at both homes",
    ]),
    ("1 week before", [
        "Pack a suitcase for the first few days",
        "Pack the first-night box (see Moving day page)",
        "Clean out the fridge and freezer",
        "Take photos of electronics wiring before unplugging",
        "Set aside valuables and documents to carry yourself",
        "Confirm keys and access for the new home",
    ]),
    ("1-2 days before", [
        "Defrost the freezer if it is moving with you",
        "Charge phones and power banks",
        "Get cash for tips or snacks",
        "Take meter readings or photos at the old home",
        "Pack the last of the kitchen",
    ]),
]
MOVING_DAY = [
    ("Morning", [
        "Walk the movers through; point out fragile boxes",
        "Keep documents, keys, chargers and meds with you",
        "Check every room, cupboard and closet is empty",
        "Take photos of the empty old home",
        "Lock windows, turn off lights, hand over keys",
    ]),
    ("At the new home", [
        "Take photos of the empty new home before unloading",
        "Check utilities are on: power, water, heat",
        "Direct boxes to the right rooms",
        "Check the inventory and note any damage",
        "Make the beds first",
    ]),
]
FIRST_NIGHT = [
    ("First-night box", [
        "Toilet paper, soap, hand towel", "Phone chargers", "Medications", "Change of clothes",
        "Bedding and pillows", "Toothbrushes, toothpaste", "Snacks and water", "Paper plates, cups, cutlery",
        "Box cutter, scissors, basic tools", "Light bulbs, flashlight", "Cleaning wipes, trash bags",
        "Pet food, bowl, leash / litter", "Kids' favourite toys", "", "",
    ]),
]
ADDRESS = [
    ("Government & mail", ["Post office / mail forwarding", "Driver's licence", "Vehicle registration",
                            "Voter registration", "Tax office", ""]),
    ("Money", ["Bank", "Credit cards", "Loans / mortgage", "Investments / pension", "Payment apps", ""]),
    ("Work & health", ["Employer / payroll", "Doctor", "Dentist", "Pharmacy", "Health insurance", "Vet"]),
    ("Home & life", ["Home / renters insurance", "Car insurance", "Subscriptions & deliveries", "Online shopping accounts",
                     "Schools", "Gym / clubs", "Friends & family", ""]),
]
WALKTHROUGH = [
    ("Safety", ["Change or rekey the locks", "Test smoke and CO alarms", "Find the main water shutoff",
                "Find the electrical panel", "Find the gas shutoff (if any)", "Check fire extinguisher"]),
    ("Check it works", ["Heating and cooling", "Hot water", "All taps and toilets", "Appliances", "Lights and outlets",
                        "Windows and door locks", "Internet and phone signal"]),
    ("Record it", ["Photos of every room before unpacking", "Note existing damage (send to landlord if renting)",
                   "Meter readings", "Where the bins go and pickup day"]),
    ("Settle in", ["Unpack kitchen and bathroom first", "Set up beds", "Meet the neighbours",
                   "Find the nearest grocery, pharmacy and urgent care", "Update your address anywhere you missed", ""]),
]


def pages(p):
    p.cover(["Moving", "Planner"], "A calm, week-by-week plan for moving house.",
            ["Move overview", "8-week countdown checklist", "Moving day checklist", "First-night box list",
             "Moving budget", "Mover quote comparison", "Change of address checklist", "Utilities set-up & cancel",
             "Room-by-room packing tracker", "Box inventory log", "Declutter plan", "New home walkthrough",
             "Contacts", "Notes"],
            "Printable planner  ·  Letter + A4")

    y = p.new_page("How to use this planner")
    y = p.paragraph(y, "Moving has hundreds of small jobs. This planner breaks them into weeks so nothing important slips. "
                       "Print it and keep it in a clear folder, or write on it in any note-taking app that lets you mark up a PDF.")
    tips = [
        ("1. Fill in the overview", "Write your moving date on the Move overview page, then count back to find your 8-week start."),
        ("2. Work the countdown", "Tick tasks week by week. Skip what does not apply. Add your own in the blank lines."),
        ("3. Compare before you book", "Use the quote comparison page to line up movers or truck rentals side by side."),
        ("4. Number every box", "Give each box a number and log it. You will know exactly what is in box 23 without opening it."),
        ("5. After the move", "Use the walkthrough and change-of-address pages in your first two weeks."),
    ]
    for h, t in tips:
        y -= 6
        y = p.paragraph(y, h, fs=11, font="SerifSemi", color=p.accent)
        y = p.paragraph(y + 2, t)

    y = p.new_page("Move overview", "The key facts, all in one place.")
    y = p.fields(y, ["Moving date", "Keys handed over (old)", "Keys collected (new)", "Moving company / truck",
                     "Pick-up time", "Budget", "Moving from (area)", "Moving to (area)"], cols=2)
    y = p.section(y, "Key dates")
    y = p.table(y, [("Date", 2), ("What happens", 6), ("Confirmed?", 2)], rows=8, row_h=22)
    p.notes_fill(y, "Notes")

    y = p.new_page("Countdown: 8 to 4 weeks", "Start here about two months before your move.")
    y = p.two_col_checklist(y, COUNT_A[:2], COUNT_A[2:] + [("My extra tasks", ["", "", "", ""])], fs=9.2)
    p.notes_fill(y, "Notes")

    y = p.new_page("Countdown: final 2 weeks", "The busy stretch. Keep going, you are nearly there.")
    y = p.two_col_checklist(y, COUNT_B[:2], COUNT_B[2:] + [("My extra tasks", ["", "", "", ""])], fs=9.2)
    p.notes_fill(y, "Notes")

    y = p.new_page("Moving day", "Keep this page with you, not in a box.")
    y = p.two_col_checklist(y, [MOVING_DAY[0]], [MOVING_DAY[1]], fs=9)
    items = FIRST_NIGHT[0][1]
    y = p.two_col_checklist(y - 6, [("First-night box", items[:8])], [("(continued)", items[8:])], fs=9)
    p.notes_fill(y, "Moving day notes")

    y = p.new_page("Moving budget", "Plan it, then track what you really spent.")
    y = p.fields(y, ["Total budget", "Deposit(s) paid"], cols=2)
    p.table(y, [("Item", 4), ("Estimate", 2), ("Actual", 2), ("Paid?", 1.5), ("Notes", 4)],
            prefill=[["Movers / truck rental"], ["Fuel & tolls"], ["Boxes & packing supplies"], ["Cleaning (old home)"],
                     ["Storage"], ["Deposits (new home)"], ["Utility connection fees"], ["Travel & hotel"],
                     ["Food on moving days"], ["Pet / child care"], ["New furniture & basics"], ["Tips"], [""], [""], [""]],
            row_h=24)

    y = p.new_page("Mover quote comparison", "Get at least three quotes. Ask what is included and how damage is handled.")
    p.table(y, [("Question", 3.4), ("Quote 1", 3), ("Quote 2", 3), ("Quote 3", 3)],
            prefill=[["Company"], ["Phone / email"], ["Date & time slot"], ["Total price"], ["Hourly or flat?"],
                     ["Deposit required"], ["What is included"], ["Packing service?"], ["Insurance / damage cover"],
                     ["Licensed & insured?"], ["Cancellation terms"], ["Reviews checked?"], ["Gut feeling"], ["Decision"]],
            row_h=34)

    y = p.new_page("Change of address", "Tick each one when updated. Write the date in the margin.")
    y = p.two_col_checklist(y, ADDRESS[:2], ADDRESS[2:], fs=9.4)
    p.notes_fill(y, "Other places to update")

    y = p.new_page("Utilities & services", "Cancel or transfer at the old home, set up at the new one.")
    p.table(y, [("Service", 2.6), ("Provider", 3), ("Account #", 2.6), ("Stop date (old)", 2.4), ("Start date (new)", 2.4), ("Done", 1.3)],
            prefill=[["Electricity"], ["Gas"], ["Water & sewer"], ["Trash & recycling"], ["Internet"], ["Mobile phone"],
                     ["TV / streaming"], ["Home security"], ["Lawn / cleaning"], ["Newspaper / deliveries"], [""], [""]],
            row_h=32)

    y = p.new_page("Room-by-room packing", "One row per room. Pack the rooms you use least first.")
    p.table(y, [("Room", 3), ("# of boxes", 1.8), ("Started", 1.8), ("Packed", 1.8), ("Labelled", 1.8), ("Unpacked", 1.8), ("Notes", 4)],
            prefill=[["Kitchen"], ["Living room"], ["Dining room"], ["Primary bedroom"], ["Bedroom 2"], ["Bedroom 3"],
                     ["Bathroom(s)"], ["Office"], ["Laundry"], ["Garage"], ["Closets & storage"], ["Outdoor / shed"], [""], [""]],
            row_h=33)

    for _ in (1, 2):
        y = p.new_page("Box inventory", "Number each box and write the number on two sides.")
        p.table(y, [("Box #", 1.3), ("Room", 2.6), ("What is inside", 7), ("Fragile", 1.5), ("Arrived", 1.5), ("Unpacked", 1.6)], row_h=23)

    y = p.new_page("Declutter plan", "Every item you do not move saves time and money.")
    p.table(y, [("Item", 5), ("Keep", 1.3), ("Sell", 1.3), ("Donate", 1.5), ("Toss", 1.3), ("Where / price", 3.5)], row_h=23)

    y = p.new_page("New home walkthrough", "Do this in your first days in the new place.")
    y = p.two_col_checklist(y, WALKTHROUGH[:2], WALKTHROUGH[2:], fs=9.4)
    p.notes_fill(y, "Things to fix or buy")

    y = p.new_page("Moving contacts", "Everyone involved in the move.")
    p.table(y, [("Who", 3), ("Name / company", 4), ("Phone", 3), ("Email / notes", 5)],
            prefill=[["Moving company"], ["Truck rental"], ["Old landlord / agent"], ["New landlord / agent"],
                     ["Lawyer / closing agent"], ["Storage unit"], ["Cleaner"], ["Helpers"], ["Building manager"],
                     ["Childcare / pet care"], [""], [""], [""]], row_h=33)

    y = p.new_page("Notes")
    p.lined(y - 6, dotted=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in build(OUT, "Moving-Planner", PRODUCT, "#50708F", pages, FOOT):
        print(f)
