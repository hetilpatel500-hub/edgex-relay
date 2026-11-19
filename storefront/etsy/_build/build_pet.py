import os
from planner import build

OUT = os.path.join(os.path.dirname(__file__), "..", "05-pet-care-record")
PRODUCT = "Pet Care & Health Record"
FOOT = "Edgex Studio  ·  For personal use  ·  Print a set for each pet"


def pages(p):
    p.cover(["Pet Care", "& Health", "Record"], "Everything your vet, sitter and you need, in one place.",
            ["Pet profile", "Vet & emergency contacts", "Vaccination record", "Medication log",
             "Vet visit log", "Flea, tick & heartworm tracker", "Weight tracker", "Feeding plan",
             "Grooming log", "Weekly care log", "Symptom log", "Pet sitter sheet", "Expense tracker", "Notes"],
            "Printable planner  ·  Letter + A4  ·  Dogs, cats & more")

    y = p.new_page("How to use this record")
    y = p.paragraph(y, "Keep one set of pages for each pet. Print them and keep them in a folder by the door, or write on them "
                       "in any note-taking app that lets you mark up a PDF. Bring the vaccination and medication pages to every vet visit.")
    tips = [
        ("1. Start with the profile", "Fill in the Pet profile and Vet & emergency contacts first. These are the pages a sitter or emergency vet will ask for."),
        ("2. Copy in past records", "Add dates from old vet paperwork to the Vaccination record so you can see what is due next."),
        ("3. Tick the monthly tracker", "Use the prevention tracker for flea, tick, heartworm or any other monthly treatment your vet recommends."),
        ("4. Log changes early", "Small changes in weight, appetite or energy are easy to forget. Note them in the Symptom log and show your vet."),
        ("5. Leaving your pet?", "Fill in the Pet sitter sheet and leave it on the fridge with the contacts page."),
    ]
    for h, t in tips:
        y -= 6
        y = p.paragraph(y, h, fs=11, font="SerifSemi", color=p.accent)
        y = p.paragraph(y + 2, t)
    y -= 10
    p.box(p.M, y, p.W - 2 * p.M, 70, "A friendly note")
    p.paragraph(y - 34, "This record helps you keep track of care. It is not veterinary advice. Always follow your vet's "
                        "instructions for vaccines, medicines, doses and diet.", fs=8.6, color=p.accent, width=p.W - 2 * p.M - 24, x=p.M + 10)

    y = p.new_page("Pet profile", "Paste or tape a photo in the box.")
    bw = 150
    p.box(p.W - p.M - bw, y + 4, bw, 150, "Photo")
    y2 = p.fields(y, ["Name", "Species", "Breed", "Birthday / age", "Sex", "Spayed / neutered", "Colour & markings",
                      "Adoption date"], cols=1, width=p.W - 2 * p.M - bw - 20)
    y = min(y2, y - 170)
    y = p.fields(y, ["Microchip number", "Microchip registry", "License / tag number", "Insurance & policy number",
                     "Current weight", "Healthy weight range (ask your vet)"], cols=2)
    w = (p.W - 2 * p.M - 16) / 2
    p.box(p.M, y, w, 150, "Allergies & sensitivities", lines=6)
    p.box(p.M + w + 16, y, w, 150, "Personality & quirks", lines=6)
    y -= 166
    p.box(p.M, y, p.W - 2 * p.M, y - 40, "Ongoing conditions & notes", lines=10)

    y = p.new_page("Vet & emergency contacts", "Keep a copy on the fridge and one in your phone photos.")
    p.table(y, [("Who", 3), ("Name / clinic", 4), ("Phone", 3), ("Address / notes", 5)],
            prefill=[["Primary vet"], ["Emergency vet (24h)"], ["Animal poison hotline"], ["Specialist"], ["Groomer"],
                     ["Pet sitter"], ["Dog walker"], ["Trainer"], ["Boarding / daycare"], ["Pet insurance"],
                     ["Backup caregiver"], ["Microchip registry"], ["Local animal control"]], row_h=31)

    y = p.new_page("Vaccination record", "Copy dates from your vet paperwork. Ask your vet which vaccines your pet needs.")
    p.table(y, [("Vaccine", 3.4), ("Date given", 2.2), ("Next due", 2.2), ("Vet / clinic", 3), ("Lot / tag #", 2.2), ("Notes", 3)], row_h=25)

    y = p.new_page("Medication log", "Prescriptions, supplements and one-off treatments.")
    p.table(y, [("Medication", 3.2), ("Dose", 1.8), ("How often", 2.2), ("Start", 1.8), ("End", 1.8), ("For what", 2.8), ("Prescribed by", 2.6)], row_h=25)

    for _ in (1, 2):
        y = p.new_page("Vet visit log", "Write down what the vet said before you leave the car park.")
        p.table(y, [("Date", 1.8), ("Reason", 3), ("Vet", 2.2), ("What they found / said", 5.4), ("Weight", 1.6), ("Cost", 1.6), ("Follow-up", 2.2)], row_h=33)

    y = p.new_page("Monthly prevention tracker", "Tick each month's dose. Use the blank rows for anything else your vet recommends.")
    y = p.fields(y, ["Pet", "Year"], cols=2)
    p.month_grid(y, ["Flea & tick", "Heartworm", "Deworming", "Dental chew / care", "Nail trim", "Bath / brush",
                     "Check ears", "Check teeth & gums", "Wash bedding", "Replace toys / check for damage",
                     "", "", "", "", "", ""], label_head="TREATMENT / CARE", row_h=30)

    y = p.new_page("Weight tracker", "Weigh at the same time of day on the same scale. Share big changes with your vet.")
    y = p.fields(y, ["Pet", "Healthy weight range", "Scale used", "Weigh-in day"], cols=2)
    p.table(y, [("Date", 2), ("Weight", 2), ("Change", 2), ("Body shape / notes", 6)], row_h=24)

    y = p.new_page("Feeding plan", "Handy for sitters, family and diet changes.")
    y = p.fields(y, ["Food brand & type", "Amount per meal", "Meals per day", "Feeding times", "Treats allowed",
                     "Water bowl refreshed", "Foods to avoid", "Where food is kept"], cols=2)
    y = p.section(y, "Food change log")
    p.table(y, [("Date", 2), ("Old food", 3.4), ("New food", 3.4), ("How it went", 5)], row_h=26)

    y = p.new_page("Grooming log", "Baths, haircuts, nails, teeth and ears.")
    p.table(y, [("Date", 2), ("Service", 3.6), ("Done by", 3), ("Cost", 1.8), ("Next due", 2), ("Notes", 4)], row_h=25)

    for _ in (1,):
        y = p.new_page("Weekly care log", "Tick as you go. Great for households with more than one person feeding.")
        y = p.fields(y, ["Pet", "Week of"], cols=2)
        p.table(y, [("Day", 2.2), ("Breakfast", 2), ("Dinner", 2), ("Walk / play", 2.2), ("Meds", 1.8), ("Potty / litter", 2.2), ("Notes", 4.6)],
                prefill=[["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"], ["Saturday"], ["Sunday"]], rows=7, row_h=78)

    y = p.new_page("Symptom log", "Note anything unusual: appetite, energy, stool, scratching, limping, sneezing.")
    p.table(y, [("Date", 2), ("What you noticed", 5.4), ("How long", 2), ("What you did", 4), ("Better?", 1.6)], row_h=30)

    y = p.new_page("Pet sitter sheet", "Fill in, then leave with your contacts page.")
    y = p.fields(y, ["Pet name(s)", "Dates away", "Your phone", "Where you will be", "Back-up contact", "Vet & phone"], cols=2)
    y = p.section(y, "Daily routine")
    y = p.table(y, [("Time", 2), ("What to do", 8)], rows=6, row_h=22,
                prefill=[["Morning"], ["Midday"], ["Afternoon"], ["Evening"], ["Bedtime"], [""]])
    y = p.two_col_checklist(y, [("Before you go", ["Food and treats stocked", "Medicines labelled", "Leash, litter, bags ready",
                                                   "Spare key arranged", "Vet told who the sitter is"])],
                            [("House notes", ["", "", "", "", ""])], fs=9)
    p.notes_fill(y, "Anything else the sitter should know")

    y = p.new_page("Pet expense tracker", "Food, vet, grooming, toys, insurance, boarding.")
    y = p.fields(y, ["Pet", "Year"], cols=2)
    p.table(y, [("Date", 2), ("Category", 2.8), ("What", 5), ("Where", 3), ("Amount", 2)], row_h=23)

    y = p.new_page("Notes")
    p.lined(y - 6, dotted=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in build(OUT, "Pet-Care-Health-Record", PRODUCT, "#B8704F", pages, FOOT):
        print(f)
