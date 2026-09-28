# Print-on-demand desk: watercolor designs for Etsy + Printify

Owner directive, 2026-09-28: do what the reel showed (AI agents making cute
watercolor shirt designs sold on Etsy through Printify), learn the watercolor
look, do it smartly, and make the agents capable of it.

**Publishing authority (owner, 2026-09-28):** "I give you authority to
publish up to $3 a day." Agents publish finished, Legal-cleared designs to
the owner's Etsy shop through the Printify API, up to **$3.00 of Etsy listing
fees per day** ($0.20 each = 15 listings/day). Count today's `pod_listings`
docs with `published: true` before every publish; at 15, create the product
unpublished instead. Prices are in the product table below unless the owner sets
others. The Printify key is an API credential on the cloud environment (the
proxy attaches it to api.printify.com; agents never see it). Agents never
buy anything, never order samples, and never change the owner's Etsy or
Printify account settings.

Shop: Printify shop 29114200 ("My new store"), sales channel Etsy.

**Etsy status (2026-09-28):** the owner submitted Etsy's ID + selfie check;
Etsy said it takes 1-3 days. Until it clears, Printify accepts publish calls
but no Etsy listing appears (the product's `external` stays empty). While a
product has no Etsy listing ID: create new products **unpublished** (drafts,
$0), don't call publish again, and check once a day
(`GET /v1/shops/29114200/products/<id>.json`, field `external.id`). When the
first one shows an Etsy ID, publish the waiting drafts oldest first, within
the daily cap.

## Product lineup (one Etsy listing per product per design)

Owner, 2026-09-28: "don't just design only t-shirts, also use other things
they offer to print." Every design is made into all of these unless it
doesn't suit one (say why in the `pod_listings` doc):

| Product | Printify blueprint / printer | Printify cost | Our price |
|---|---|---|---|
| Unisex tee | Bella+Canvas 3001, 12 / Monster Digital 29 | $11.77 (2XL $14.38) | $26 (2XL $28) |
| Crewneck sweatshirt | Gildan 18000, 49 / Monster Digital 29 | $19.45 (2XL $22.35) | $42 (2XL $45) |
| 11 oz mug (art on both sides) | 68 / SPOKE 1 | $6.44 | $18 |
| Art print (the painting on cream paper) | Matte poster 282 / Sensaria 2 | $6.60 / $11.84 / $12.00 | $22 / $30 / $36 (11x14 / 16x20 / 18x24) |
| Kiss-cut sticker | 400 / SPOKE 1 | see Printify | $4.50 (3x3) / $5.50 (4x4) |

Costs are Printify's catalog prices read through the API on 2026-09-28,
before shipping (the buyer pays shipping). `printify.py` refuses to price
anything below cost + $4 and raises that variant's price instead. The tote
(609 / 74) costs $20.72, too little margin: not in the lineup until a
cheaper tote is found. Sweatshirts sell best Sept-Feb; mugs and stickers are
cheap add-ons and gifts; art prints suit the evergreen niches (books,
flowers, pets). With 5 listings per design, the $3/day cap covers 3 designs a
day.

## Why our own watercolor engine (the smart part)

The image generators reachable from our sessions return small thumbnails,
far below the 4500 x 5400 px Printify wants for a shirt, and AI-image output
raises Etsy disclosure and copyright questions. So the studio paints with its
own code (`pod-kit/watercolor.py`), using a known generative-art technique:
each wash is ~40 stacked, randomly deformed transparent copies of a shape,
plus edge darkening (pigment pools at the rim), granulation (pigment in the
paper's tooth), wet-in-wet color blends, and subtractive color mixing. It
renders at full print size in ~30 seconds, looks the same every time for the
same seed, costs nothing, and every design is original work the studio owns.
The US Copyright Office does not register purely machine-generated images;
our designs are composed by the agents and drawn by code we wrote, and the
Legal Desk still notes this on every delivery.

## Making a design (`pod-kit/`)

| Step | Agent | What they do |
|---|---|---|
| 1a | Trend Scout | **What's rising now.** Run at least 3 fresh web searches (e.g. "Etsy trending shirts <month year>", "<season/holiday> shirt ideas <year>", "<niche> gift trends <year>") and read the results. Check the seasonal calendar: design for the holiday or season **4-8 weeks ahead** (listings need time to index): Oct: Halloween, fall, Thanksgiving; Nov: Christmas, winter; Jan: Valentine's; Feb: St Patrick's, spring; Apr: Mother's Day, teacher/nurse appreciation; May: Father's Day, summer, graduation. Evergreen niches that sell all year: occupations (teachers, nurses), pets and breeds, books and readers, gardening, coffee, hiking and camping, family humor. vidIQ social trend search only if credits allow. |
| 1b | Market Research Agent + Competitor Analysis Agent | **What the competition sells.** Search for the candidate phrase plus "shirt" and "etsy" and study at least 5 competing listings the results show: their wording, style, prices, and what they all have in common. Note what's missing (a style, a sub-niche, a better phrase) and pick an angle that is clearly different: never copy a competitor's phrase, art or layout. Rate the idea 1-5 on demand, competition (5 = little), timing, fit with our watercolor style, and trademark risk (5 = safe); only ideas scoring 17+ of 25 go ahead. Write one `pod_research` doc {phrase, niche, sources: [urls], competitors: [{what, price, style}], gap, scores, decision, created}. Check `pod_designs` so nothing repeats. Avoid anything tied to a brand, show, team, celebrity or franchise. |
| 2 | Legal Desk: IP & Trademark Counsel | Before any art is made, search the phrase (WebSearch: "<phrase> trademark clothing", Justia/uspto.report results; tmsearch.uspto.gov is blocked from our sessions, so say so). Reject phrases that are a registered or pending clothing mark, an existing apparel brand name, or a known enforced format (e.g. "Saturdays Are For ..."). Record what was searched and found in `listing.trademark_check`. |
| 3 | Brand & Graphic Design Agent | Write `pod-kit/designs/<id>.json`: template (arch, stack, badge, wreath), lettering and fonts, motifs from `motifs.py`, bouquet flowers (use "none" for spots hidden behind objects), palette, shirt colors, seed. New motif needed? Add it to `motifs.py` following the pattern: a light first wash, darker wet-on-dry shaping, details, optional loose ink line. |
| 4 | Quality Bar Agent | `python3 design.py designs/<id>.json OUT --preview` and look at the paper image and mockups. Fix anything muddy, anything hidden behind transparent paint, awkward overlaps, lettering too small to read on a shirt at 3 m, or objects that don't read (a dog should read as a dog). Change the seed if a wash lands badly. |
| 5 | Copywriter + SEO Agent | The `listing` section: a title of 140 characters max, front-loaded with the phrase buyers search; 13 tags of 20 characters max, all different, real search phrases; a 2-3 sentence product description (the standard how-it's-made, details and care text is added automatically); products; a price note with a source. |
| 6 | Grammar & Copy Editor, Deliverable QA Reviewer | `python3 build.py designs/<id>.json OUT` (full size). build.py refuses the build if a title, tag or trademark rule is broken. Check `<id>.png` is 4500 x 5400 with a transparent background. |
| 7 | Legal Desk (all ten counsel) | One `legal_reviews` doc: trademark (the phrase, tags, title), copyright (original art, OFL fonts in `pod-kit/fonts`), platform (Etsy's production-partner disclosure; the description says the art is digitally painted by the studio and printed by a production partner), advertising (no claims like "best seller" or "free"). |
| 8 | Chief of Staff | Approve or deny, only with a `cleared` legal review, in `decisions`. |
| 9 | Publish Coordinator | Check the $3/day cap and the Etsy status above, then `python3 printify.py designs/<id>.json OUT --products tee,sweatshirt,mug,poster,sticker [--publish]` (creates one Printify product per type with its own title, tags, description, colors and price; `--publish` sends them to Etsy). Only pass `--publish` when Etsy is verified and the cap allows all of them; otherwise run once with `--publish` for the ones that fit and once without for the rest. If Printify answers 429 (rate limit), the script waits and retries; run product types one at a time with a pause if it keeps happening. Write one `pod_listings` doc per product {design, product, product_id, published, listing_fee_usd, price_cents, etsy_listing_id, created}. Publish `OUT/index.html` as a private artifact (`capabilities {"downloads": true}`, all files in OUT) as the record. Email the owner the title, the artifact link, and which products are live on Etsy and which are drafts. Add or update the `pod_designs` doc {title, phrase, niche, artifact, product_ids: {product: id}, created, status: "listed" or "drafted"}. |
| 10 | Analytics & Reporting Agent (weekly, Mondays) | **Learn from sales.** Pull orders from Printify (`GET /v1/shops/29114200/orders.json`) and count sales per design and niche. Write a `pod_review` doc: what sold, what didn't, and the rule for next week (more of the winning niche and style, retire what isn't working after 60 days). Trend Scout reads the latest review before step 1a. |

Run with plain `python3` (numpy and Pillow are enough). Output goes in the
scratchpad, never the repo. Only the design JSON files are committed.

## Rules

- Original art and lettering only. No brands, franchises, characters,
  celebrities, sports teams, universities, song lyrics or movie quotes.
- One phrase must pass the trademark search before any work starts.
- Designs are made for light shirts (white, natural, pastel). Dark shirts
  need a white-underbase version; not supported yet.
- Never claim sales numbers, "best seller", or reviews. Prices are
  suggestions with a source; the owner decides.

## Cadence

One design every weekday, from the "Edgex POD desk" Routine: researched,
made, Legal-cleared, published to Etsy, and reported to the owner by email. The owner can ask for a themed batch from the
Studio Floor at any time.

## Done

- 2026-09-28: Currently Reading, Morning Walks & Good Dogs, Strawberry Season.
  Tees sent to Etsy through Printify on 2026-09-28 (3 publish calls; no
  Etsy listing yet, waiting on Etsy's ID check). Sweatshirt, mug, art print
  and sticker drafts created unpublished, waiting for the same check
  ("Farmers Market Club" rejected in trademark screening: existing apparel
  brand, and a FARMERS MARKET clothing filing).
