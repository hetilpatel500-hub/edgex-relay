# pod-kit: watercolor print-on-demand designs

See `../POD-DESK.md` for the runbook. Quick start:

    python3 design.py designs/strawberry-season.json OUT --preview   # fast check
    python3 build.py  designs/strawberry-season.json OUT             # full 4500x5400 + mockups + listing page

- `watercolor.py`: the painting engine (stacked deformed washes, edge darkening, granulation, wet-in-wet, subtractive mixing, loose ink, lettering)
- `motifs.py`: rose, daisy, wildflower, tulip, sprig, eucalyptus, berries, bouquet, wreath, mug, books, heart, paw, dog, lemon, strawberry, sun, succulent, pumpkin
- `design.py`: templates (arch, stack, badge, wreath), palettes, shirt mockups
- `build.py`: listing checks (title, 13 tags, risky words, trademark note) and the delivery page
- `fonts/`: SIL Open Font License fonts with their license files
