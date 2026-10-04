# pod-kit: watercolor print-on-demand designs

See `../POD-DESK.md` for the runbook. Quick start:

    python3 design.py designs/strawberry-season.json OUT --preview   # fast check
    python3 build.py  designs/strawberry-season.json OUT             # full 4500x5400 + mockups + listing page
    python3 pattern.py designs/reading-ghosts.json OUT --preview      # all-over mug pattern, fast check
    python3 build.py  designs/reading-ghosts.json OUT                # every mug wrap size + 3D mockups + page
    python3 printify.py designs/reading-ghosts.json OUT --products mug_wrap,accent_mug   # Printify drafts

- `watercolor.py`: the painting engine (stacked deformed washes, edge darkening, granulation, wet-in-wet, subtractive mixing, loose ink, lettering)
- `motifs.py`: rose, daisy, wildflower, tulip, sprig, eucalyptus, berries, bouquet, wreath, mug, books, heart, paw, dog, lemon, strawberry, sun, succulent, pumpkin, ghost (optionally reading), maple_leaf, acorn, sparkle, moon, bat, book_single, soup_bowl, carrot, garlic, mushroom, bay_leaf, peppercorns, cardinal, pine_bough, pinecone, holly, snowflake, snow_dot, cocoa_mug, marshmallow, cinnamon_stick, orange_slice, star_anise, peppermint, gingerbread_man, sugar_cookie (star, tree, heart, round, mitten), candy_cane, sprinkles, menorah, flame, plate, sufganiyah, dreidel, gelt, olive_sprig
- `pattern.py`: seamless all-over patterns for wraparound mugs, and 3D accent-mug mockups
- `printify.py`: creates products on Printify (and publishes within the owner's $3/day cap)
- `photos.py`: 9 extra Etsy listing photos per product, drawn from the real print files (Printify gives mugs 1, tees 3)
- `design.py`: templates (arch, stack, badge, wreath), palettes, shirt mockups; an art item with `"front": true` is painted first and later paint goes around it
- `build.py`: listing checks (title, 13 tags, risky words, trademark note) and the delivery page
- `fonts/`: SIL Open Font License fonts with their license files
