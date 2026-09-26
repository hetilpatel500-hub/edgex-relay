# Book desk: coloring books for the owner's KDP account

Owner directive, 2026-09-26: "keep making me books like these, but different
topics". The model book is the owner's own **My First Trucks Coloring Book: 30 Big
& Easy Things That Go** by JONNY COLOR, in the **my first step** series (ages 2–5).
Every book comes with its title, subtitle, description, 7 keywords and
categories, ready to paste into KDP.

The owner uploads and publishes. Agents never sign in to KDP, never publish,
and never set a price.

## The format (keep every book in the series consistent)

- "My First <Topic> Coloring Book: 30 Big & Easy <Things> – A, B, C & More for Kids Ages 2-5", by JONNY COLOR, series "my first step".
- 30 subjects, one big picture per page, extra-thick outlines, the subject's name in outlined letters on the page.
- Pictures print on one side only (blank back), then a "Great job!" certificate. 64 pages.
- Paperback: 8.5 x 11 in, no bleed, white paper. The cover is a full wrap with bleed. There's no spine text, because KDP only allows spine text on books over 79 pages.
- Cover: sky, smiling sun, rainbow, rounded title box with the topic word in rainbow letters, an "AGES 2-5" badge, and three subjects in color on the grass.

## How a book gets made (`book-kit/`)

| Step | Agent | What they do |
|---|---|---|
| 1 | Trend Scout + Market Research Agent | Pick the next topic from the rotation below. Check the `books` collection so nothing repeats. |
| 2 | Brand & Graphic Design Agent | Draw 30 subjects in `book-kit/art/<topic>.js` with the helpers in `art/core.js`: big simple shapes, cute faces, closed outlines, and a colour palette for the cover. |
| 3 | Quality Bar Agent | `node sheet.js art/<topic>.js sheet.png` and look at every drawing. Fix anything broken, overlapping, too detailed for a 2-year-old, or hard to recognize. |
| 4 | Copywriter + SEO Agent | Write `books/<id>.json`: title, subtitle, description, 7 keywords (50 characters max each), 3 categories. Keywords are real phrases parents search for. Never use other authors, brands or trademarked characters. |
| 5 | Grammar & Copy Editor, Deliverable QA Reviewer | `node build.js books/<id>.json OUT`, then `python3 page.py OUT`. Check the page previews, the cover, and that the cover size printed by page.py matches KDP's formula. |
| 6 | Legal Desk (all ten counsel) | Review the book and listing per `LEGAL-DESK.md`: trademark (title, keywords), copyright (original art, font license, AI-art copyright note), platform (KDP AI disclosure, metadata rules), kids/COPPA, advertising (description claims). Write one `legal_reviews` doc. |
| 7 | Chief of Staff | Approve or deny, only with a `cleared` legal review, and log it in `decisions`. |
| 8 | Publish Coordinator | Publish `OUT/index.html` as a new private artifact (`capabilities {"downloads": true}`, files: interior.pdf, cover-paperback.pdf, cover-kindle.jpg, preview-cover.jpg, preview-pages.png). Email the owner the link, title, subtitle, description, keywords and categories. Add a `books` doc. |

Run with `NODE_PATH=/opt/node22/lib/node_modules` (Playwright and Chromium are
already in the environment). Build output goes in the scratchpad, never the repo.

## Topic rotation (my first step)

Done: Trucks (owner's), Animals (2026-09-26).
Next, in order, unless the owner asks for something else: Dinosaurs, Fruits &
Veggies, Bugs & Butterflies, Ocean, Space, Toys, Yummy Food, Birds, Shapes &
Colors, At Home, Weather & Nature, Pets, Music, Sports.

## Rules

- Original art only. No licensed characters (no Disney, Paw Patrol, Pokémon or
  other franchises) and no copying of anyone's drawings.
- KDP asks about AI-generated content. The pictures and text are made by AI
  agents, so every delivery tells the owner to answer Yes for images and text.
- No invented claims in the description (no "bestselling", no fake reviews).
  Prices are only suggested, with a source.
- Why vector art: Canva's AI images come back as small thumbnails here (its file
  hosts are blocked), too small for 300 DPI print. Vector line art is sharp at
  any size and needs no credits.

Sources for the print numbers: KDP spine width is page count × 0.002252 in for
white paper, cover width is bleed + back + spine + front + bleed with 0.125 in
bleed (kdpeasy.com KDP cover and spine guides, 2026).
