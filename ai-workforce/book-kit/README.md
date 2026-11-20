# book-kit

Makes KDP coloring books for the owner's "my first step" series. The runbook is
`../BOOK-DESK.md`.

    export NODE_PATH=/opt/node22/lib/node_modules
    node sheet.js art/animals.js /tmp/sheet.png          # review every drawing
    node build.js books/my-first-animals.json /tmp/out   # interior, covers, listing
    python3 page.py /tmp/out                             # exact cover size + delivery page

- `art/core.js`: drawing helpers. Every subject draws in a 1000x1000 box, and shapes
  painted later hide the lines under them.
- `art/<topic>.js`: 30 subjects per topic, each with a label and a cover palette.
- `books/<id>.json`: the subject order, cover words and the KDP listing.
  Optional `cover.ground` ({fill, edge, text}) swaps the grass under the cover and A+ art,
  e.g. light-blue snow for a winter book; keep the fill darker than near-white so the bleed check passes.
- `fonts/`: Fredoka (SIL Open Font License).
