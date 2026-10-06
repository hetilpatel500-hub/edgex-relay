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

**Etsy status (2026-10-02):** the owner says the Etsy account is created and
approved, and pays $10/month for **Etsy Plus** ("just keep that in mind and
work"). Etsy Plus includes 15 listing credits a month (covers 15 x $0.20
listing fees) and a $5 Etsy Ads credit a month; both expire at the end of
each billing cycle if unused, so use the 15 credits every month before paying
listing fees. Etsy Ads stays off unless the owner asks (agents don't change
Etsy settings). On 2026-10-02 none of the 33 Printify products had an Etsy
listing ID yet; publishing resumes once the owner confirms it.

**Etsy is live (2026-10-02):** the owner said "publish the 33 drafts, use the
$5 monthly for ads". 30 went live on Etsy that day, seasonal first. The first
15 used the month's Etsy Plus credits and the next 15 paid $3.00, the daily cap.
The last 3 (strawberry sweatshirt, art print, sticker) publish on Oct 3. From now on, new
products are published to Etsy as soon as they're Legal-cleared. The $3/day cap
counts **paid** listing fees only, so each month the first 15 listings (credits)
don't count toward it. Etsy Ads: the owner turns it on in Etsy Shop Manager
with the $5 monthly credit; agents suggest which listings, never change the setting.
Etsy makes new shops wait 15 days before Etsy Ads: Ads open for Edgexhp about
2026-10-13 (a reminder Routine emails the owner the plan that day).

**Etsy Ads allowed (owner, 2026-10-06: "lift for etsy, try to do everything by
you").** The no-ads rule is lifted for Etsy Ads only (no Meta, Pinterest,
Zeely or other ad tools). Agents do all the ad work: pick listings, sharpen
titles and tags, set the stop rules and read results. The plan lives in the
office DB at `etsy_ads/plan-2026-10` (Legal cleared, Chief of Staff approved).
Etsy itself is blocked from the cloud environment, so the owner still makes
the Shop Manager clicks. Spend stays on the $5 monthly Etsy Plus credit
($1/day, about 5 days); after that Etsy bills the owner's card, so ads pause
unless the owner approves a paid budget. Agents never raise or extend it.
Printify sits behind Cloudflare: every API call must send a User-Agent
(printify.py sends `edgex-pod-desk`), or it fails with 403 "error code: 1010".

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
| Unisex tee | Bella+Canvas 3001, 12 / Monster Digital 29 | $11.77 (2XL $14.38) | $24.99 (2XL $26.99) |
| Crewneck sweatshirt | Gildan 18000, 49 / Monster Digital 29 | $19.45 (2XL $22.35) | $35.99 (2XL $38.99) |
| 11 oz mug (art on both sides) | 68 / SPOKE 1 | $6.44 | $16.99 |
| Art print (the painting on cream paper) | Matte poster 282 / Sensaria 2 | $6.60 / $11.84 / $12.00 | $19.99 / $29.99 / $34.99 (11x14 / 16x20 / 18x24) |
| Kiss-cut sticker | 400 / SPOKE 1 | $1.66 (3x3) / $2.08 (4x4) | $6.75 (3x3) / $7.40 (4x4) |
| Full-wrap white mug (pattern designs) | 68 / SPOKE 1, wrap 2700 x 1120 | $6.44 | $16.99 |
| Accent mug, colored handle/rim/inside (pattern designs) | 635 / Printify Choice 99, wrap 2475 x 1155 (11 oz), 2475 x 1275 (15 oz) | $6.40 / $8.44 | $19.99 / $22.99 |

**Pricing review (owner, 2026-10-05: "competitive pricing while also making profits").** Prices were checked against Etsy search results for the same product types: tees $23-59 (often on sale at $15-28), watercolor crewnecks $25-40, 11 oz mugs $12-28 (mostly $14-21), accent mugs about $15-21, prints $18+ (11x14) and $30-50 (16x20), 3" stickers $3-5.50 with free shipping. The buyer also pays Printify's US shipping (tee $4.95, sweatshirt $8.79, mug $7.29, print $7.49-7.69, sticker $4.79; the highest US rate is used to be safe). Net profit per sale after cost and Etsy's 6.5% transaction, 3% + $0.25 processing and $0.20 listing fees: tee $9.93, sweatshirt $11.84, mug $7.79, accent mug $10.55-11.02, prints $10.33 / $13.96 / $18.65, stickers $3.54 / $3.71. A sale that comes through Etsy Offsite Ads loses another 15% of the order (the tee still nets $5.43). The sweatshirt was the outlier: $42 plus shipping was about $51 to the buyer. Stickers stay at $6.75/$7.40 (decisions/2026-09-28-sticker-pricing-update): Printify's $4.79 sticker shipping means no POD sticker can match the $3-5 free-shipping sellers, so they earn their place as add-ons. Price floor: never below the lower of these prices without a new margin check; `printify.py` still refuses cost + $4.

Costs are Printify's catalog prices read through the API on 2026-09-28,
before shipping (the buyer pays shipping). `printify.py` refuses to price
anything below cost + $4 and raises that variant's price instead. The tote
(609 / 74) costs $20.72, too little margin: not in the lineup until a
cheaper tote is found. Kiss-cut sticker prices were raised 2026-09-28 (from $5.99/$6.99 to $6.75/$7.40) after a live Etsy fee re-check found the old prices cleared cost+$4 in raw margin but only $3.31/$3.80 net of Etsy's real $0.20 listing + 6.5% transaction + 3%+$0.25 payment-processing fees (suggestions/2026-09-28-tiktok-monetization-sticker-margin, decisions/2026-09-28-sticker-pricing-update). Sweatshirts sell best Sept-Feb; mugs and stickers are
cheap add-ons and gifts; art prints suit the evergreen niches (books,
flowers, pets). With 5 listings per design, the $3/day cap covers 3 designs a
day.

## The team

Owner directive, 2026-09-28: "the tik tok agents and the youtube agents
will now work on printify and etsy" (the Instagram & Facebook agents stay
on video). The ten keep their names; their files in `agents/` have the new
jobs. They work alongside the Brand & Graphic Design, Copywriter + SEO,
Quality Bar and Legal Desk agents named in the steps below.

| Room on the Studio Floor | Agent | POD job | Steps |
|---|---|---|---|
| Printify Studio (TikTok team) | TikTok Trend-Sync Agent | Trend Scout | 1a |
| | TikTok Posting/Scheduling Agent | Printify Product Builder | 9 (drafts) |
| | TikTok Monetization Agent | Pricing & Margin, the $3/day ledger | 9 |
| | TikTok Analytics Agent | Sales Analyst | 10 |
| | TikTok Live/Engagement Agent | Buyer Care (order problems, reply drafts for the owner) | after sales |
| Etsy Shop Desk (YouTube team) | YouTube Analytics Agent | Competitor Analyst | 1b |
| | YouTube Shorts Specialist | Product Line Adapter (which products, placement, per-product wording) | 4-5 |
| | YouTube Monetization & Policy Agent | Etsy & Printify Policy | 7 (before the Legal Desk) |
| | YouTube Upload/Scheduling Agent | Etsy Publish Coordinator | 9 (publish) |
| | YouTube Community Tab Agent | Shop Presence (sections, collections, announcement drafts) | weekly |

## What sells: the owner's Etsy scan (2026-09-28)

The owner sent 7 screenshots of Etsy mug searches (saved as
`pod_research/owner-etsy-mug-scan-2026-09-28`). What they show:

- **All-over wraps win.** The biggest printed sellers are patterns that go
  all the way around: ghosts and pumpkins (18.1k reviews), ghost library,
  faux patchwork pumpkins (812), bookshelves, dachshund florals. A single
  picture on each side looks plain next to them.
- **Accent mugs** (colored handle, rim and inside: orange, pink, black,
  maroon) are everywhere and look finished. Offer 2-3 accent colors that
  match the art.
- **Themes now:** cute ghosts (often with florals or books), fall
  leaves and pumpkins, witchy moons, black cats, dark-academia books, pets
  with florals. Stained-glass styles are a strong trend.
- **Personalized mugs are the biggest category** (a repeating-name mug
  shows 152.6k reviews, $6.99). Not done yet: it needs per-order artwork,
  so it waits for the owner's go-ahead.
- **Price band** for printed mugs: about $9-24, often shown as a "sale".
  We never inflate an original price to fake a discount.
- **Photos sell:** hands, sweaters, books, candles, autumn leaves, and a
  short video. Printify generates mockups for the Etsy listing; our own
  3D mockups (`pattern.py`) go on the delivery page.
- **Our edge:** almost every printed competitor is flat vector or
  stained glass. Real-looking watercolor on painted paper is rare (one
  watercolor witch mug, 54 reviews). Keep every design unmistakably
  watercolor.

## Gift-category plan (owner, 2026-10-05)

The owner sent Etsy's gift-category menu and said: "i want to you to list for
all these products and more if there are more best selling products". Every
category gets at least one design (5 products each: tee, sweatshirt, mug, art
print, sticker), researched, trademark-screened and Legal-cleared as usual.
The $3/day cap allows 15 paid listings a day, so up to **3 designs a day**:
while this queue has open rows, the daily POD run makes up to 3 (the next
open rows, in order) instead of 1, and marks each row done with the date.

| Etsy category | Live designs | Next (queue order) |
|---|---|---|
| Top 100 Halloween Finds | Reading Ghosts, Autumn Leaves, Pumpkins & Purrs (Oct 5) | done for 2026 |
| Gifts for Pets & Owners | Morning Walks & Good Dogs, Pumpkins & Purrs | 4. a dog-breed florals design (dachshund was in the owner's mug scan) |
| Gifts for Grandparents | Grandma's Garden (Oct 5) | 5. a grandpa design (garden, fishing or coffee) |
| Top 100 Gifts for Libras (zodiac) | Scorpio Constellation (drafted Oct 5) | 1. zodiac series, one design per sign (constellation + birth-month flower): **Scorpio done 2026-10-05** (drafts). **Libra held 2026-10-05**: a pending LIBRA application covers t-shirts and sweatshirts (Astryx LLC, serial 99209588), so the owner decides; the art is ready in `designs/libra-constellation.json`. Next: Sagittarius (Nov 22-Dec 21), then one sign a day; screen each sign name for clothing marks first |
| Gifts for Him | Campfire Season (drafted Oct 5) | 2. outdoors: **Campfire Season done 2026-10-05** (drafts) |
| Top 100 Holiday Gifts | Cocoa Season, Christmas Cookies, Snowy Pine Cardinals, Sufganiyot Season (live Oct 5) | 3. Thanksgiving (Nov 26) design; then more Christmas |
| Housewarming Gifts | Soup Season and Cocoa Season art prints and mugs | 6. a kitchen or home art print design |
| Gifts for Couples, Anniversary, Engagement, Special Wedding Gifts | none | 7. a couples design that works on matching mugs (no names, no dates) |
| Birthday Gifts | every design (tags) | 8. a birthday design (cake and candles) |
| Most Whimsical Finds | Reading Ghosts, Pumpkins & Purrs, Christmas Cookies | covered |
| Gifts for Her | Currently Reading, Strawberry Season, Grandma's Garden, Good Dogs | covered |
| Gifts under $50 / under $100 | every product (our highest price is $38.99) | covered: Etsy groups these by price |
| Personalized Gifts | none | **waits for the owner:** needs per-order artwork (a name or date added to each order by hand) |
| Gifts for Kids | none | **waits for the owner and Legal:** kids' sizes are children's products under US law (CPSIA tracking labels and testing); the Legal Desk checks what Printify's kids' blueprints cover first |

**Drafts waiting for Etsy:** Scorpio Constellation and Campfire Season (10 Printify drafts, made 2026-10-05 after the day's
$3.00 cap was used). The next run publishes these first, within that day's cap (10 listings = $2.00), then makes new rows
with what is left of the cap (1 design = $1.00), and creates any extra designs as drafts.

More best sellers outside the menu (from the 2026 Etsy/Printify niche guides):
9. teacher appreciation, 10. nurse, 11. coffee lover, 12. plant lover,
13. Valentine's Day (from early January), 14. Mother's Day (from early April).
Book lovers are covered by Currently Reading and Reading Ghosts.

## Pattern designs (all-over mugs)

`pod-kit/pattern.py` paints seamless all-over patterns: motifs placed by
dart throwing (no overlaps unless `spacing` < 1), largest first, then
fillers; the wrap joins invisibly at the handle; a painted cream paper
background with white kept under the ghosts (like masking fluid). A spec
has `"kind": "pattern"`, `elements`, `background` and `mug_colors` (see
`designs/reading-ghosts.json`). `build.py` paints every mug print area at
its exact size plus 3D mockups for each accent color; `printify.py
--products mug_wrap,accent_mug` creates the products. Look at the full-size
wrap, not just the preview: ink lines and small motifs must read at print
size. Aim for the density of the best sellers: little empty background.

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
| 1a | Trend Scout (TikTok Trend-Sync Agent) | **What's rising now.** Run at least 3 fresh web searches (e.g. "Etsy trending shirts <month year>", "<season/holiday> shirt ideas <year>", "<niche> gift trends <year>") and read the results. Check the seasonal calendar: design for the holiday or season **4-8 weeks ahead** (listings need time to index): Oct: Halloween, fall, Thanksgiving; Nov: Christmas, winter; Jan: Valentine's; Feb: St Patrick's, spring; Apr: Mother's Day, teacher/nurse appreciation; May: Father's Day, summer, graduation. Evergreen niches that sell all year: occupations (teachers, nurses), pets and breeds, books and readers, gardening, coffee, hiking and camping, family humor. vidIQ social trend search only if credits allow. |
| 1b | Competitor Analyst (YouTube Analytics Agent) + Market Research Agent | **What the competition sells.** Search for the candidate phrase plus "shirt" and "etsy" and study at least 5 competing listings the results show: their wording, style, prices, and what they all have in common. Note what's missing (a style, a sub-niche, a better phrase) and pick an angle that is clearly different: never copy a competitor's phrase, art or layout. Rate the idea 1-5 on demand, competition (5 = little), timing, fit with our watercolor style, and trademark risk (5 = safe); only ideas scoring 17+ of 25 go ahead. Write one `pod_research` doc {phrase, niche, sources: [urls], competitors: [{what, price, style}], gap, scores, decision, created}. Check `pod_designs` so nothing repeats. Avoid anything tied to a brand, show, team, celebrity or franchise. |
| 2 | Legal Desk: IP & Trademark Counsel | Before any art is made, search the phrase (WebSearch: "<phrase> trademark clothing", Justia/uspto.report results; tmsearch.uspto.gov is blocked from our sessions, so say so). Reject phrases that are a registered or pending clothing mark, an existing apparel brand name, or a known enforced format (e.g. "Saturdays Are For ..."). Record what was searched and found in `listing.trademark_check`. |
| 3 | Brand & Graphic Design Agent | Write `pod-kit/designs/<id>.json`: template (arch, stack, badge, wreath), lettering and fonts, motifs from `motifs.py`, bouquet flowers (use "none" for spots hidden behind objects), palette, shirt colors, seed. New motif needed? Add it to `motifs.py` following the pattern: a light first wash, darker wet-on-dry shaping, details, optional loose ink line. |
| 4 | Quality Bar Agent | `python3 design.py designs/<id>.json OUT --preview` and look at the paper image and mockups. Fix anything muddy, anything hidden behind transparent paint, awkward overlaps, lettering too small to read on a shirt at 3 m, or objects that don't read (a dog should read as a dog). Change the seed if a wash lands badly. |
| 5 | Copywriter + SEO Agent | The `listing` section: a title of 140 characters max, front-loaded with the phrase buyers search; 13 tags of 20 characters max, all different, real search phrases; a 2-3 sentence product description (the standard how-it's-made, details and care text is added automatically); products; a price note with a source. |
| 6 | Grammar & Copy Editor, Deliverable QA Reviewer | `python3 build.py designs/<id>.json OUT` (full size). build.py refuses the build if a title, tag or trademark rule is broken. Check `<id>.png` is 4500 x 5400 with a transparent background. |
| 7 | Legal Desk (all ten counsel) | One `legal_reviews` doc: trademark (the phrase, tags, title), copyright (original art, OFL fonts in `pod-kit/fonts`), platform (Etsy's production-partner disclosure; the description says the art is digitally painted by the studio and printed by a production partner), advertising (no claims like "best seller" or "free"). |
| 8 | Chief of Staff | Approve or deny, only with a `cleared` legal review, in `decisions`. |
| 9 | Product Builder (TikTok Posting/Scheduling), Pricing & Margin (TikTok Monetization), Etsy Publish Coordinator (YouTube Upload/Scheduling) | Check the $3/day cap and the Etsy status above, then `python3 printify.py designs/<id>.json OUT --products tee,sweatshirt,mug,poster,sticker [--publish]` (creates one Printify product per type with its own title, tags, description, colors and price; `--publish` sends them to Etsy). Only pass `--publish` when Etsy is verified and the cap allows all of them; otherwise run once with `--publish` for the ones that fit and once without for the rest. If Printify answers 429 (rate limit), the script waits and retries; run product types one at a time with a pause if it keeps happening. Write one `pod_listings` doc per product {design, product, product_id, published, listing_fee_usd, price_cents, etsy_listing_id, created}. Publish `OUT/index.html` as a private artifact (`capabilities {"downloads": true}`, all files in OUT) as the record. Email the owner the title, the artifact link, and which products are live on Etsy and which are drafts. Add or update the `pod_designs` doc {title, phrase, niche, artifact, product_ids: {product: id}, created, status: "listed" or "drafted"}. |
| 9b | Brand & Graphic Design Agent + Etsy Publish Coordinator | **9+ photos per listing (owner directive 2026-10-04: "more than 8 pictures for each product").** Printify only gives our mugs 1 photo, tees 3, sweatshirts 2-3 and stickers 6 (prints and accent mugs get 20), and its API ignores custom images. Run `python3 photos.py OUT_PHOTOS --only <product ids>` for the new products: it draws 9 more from the real print file (hero, art, close-ups, second view, colors or sizes to scale, size chart or specs, details and care, the collection, made to order). Open every `00-sheet.png` and fix anything clipped or mirrored. Deliver the photo folders to the owner (private artifact, `downloads`), who adds them to each Etsy listing (Edit > Photos, after Printify's own; Etsy allows 20). **After that, never re-publish those listings from Printify with `images: true`:** it would replace the owner's photos. Send text fixes with `images: false`. |
| 10 | Sales Analyst (TikTok Analytics Agent), weekly on Mondays | **Learn from sales.** Pull orders from Printify (`GET /v1/shops/29114200/orders.json`) and count sales per design and niche. Write a `pod_review` doc: what sold, what didn't, and the rule for next week (more of the winning niche and style, retire what isn't working after 60 days). Trend Scout reads the latest review before step 1a. |

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
made, Legal-cleared, published to Etsy, and reported to the owner by email. While the gift-category queue above has open rows, the run makes up to 3
designs (15 listings, the $3 cap) instead of 1. The owner can ask for a themed batch from the
Studio Floor at any time.

## Done

- 2026-09-28: Currently Reading, Morning Walks & Good Dogs, Strawberry Season.
  Tees sent to Etsy through Printify on 2026-09-28 (3 publish calls; no
  Etsy listing yet, waiting on Etsy's ID check). Sweatshirt, mug, art print
  and sticker drafts created unpublished, waiting for the same check
  ("Farmers Market Club" rejected in trademark screening: existing apparel
  brand, and a FARMERS MARKET clothing filing).
- 2026-09-28 (15:17 UTC run): Soup Season (watercolor soup bowl with carrots,
  garlic, mushrooms, bay leaves; new motifs `soup_bowl`, `carrot`, `garlic`,
  `mushroom`, `bay_leaf`, `peppercorns`). Tee, sweatshirt, mug, art print and
  sticker created as Printify drafts (Etsy ID check still pending). The
  Winter Cardinals & Snowy Pine pattern research
  (`pod_research/winter-cardinals-pine-2026-09-28`) is queued for the next
  pattern-day run.
- 2026-09-29 (15:18 UTC run, pattern day): Snowy Pine Cardinals, an all-over
  watercolor mug wrap (cardinals on snowy pine, holly, pinecones, falling
  snow; new motifs `cardinal`, `pine_bough`, `pinecone`, `holly`,
  `snowflake`, `snow_dot`; new `pattern.py` option `"gaps": true` for snow
  placed only where the paint left the paper empty). Wrap mug and accent
  mug (Red, Navy, Black) created as Printify drafts (Etsy ID check still
  pending). The spec's `listing.per_product` now gives each product its own
  title and tags, so the two mugs no longer carry duplicate listings.
- 2026-09-30 (15:19 UTC run, motif day): Cocoa Season (a red mug of hot cocoa
  with marshmallows and a cinnamon stick, snowy pine boughs behind it,
  peppermint, star anise, holly and a dried orange wheel; subline "extra
  marshmallows, please"; new motifs `cocoa_mug`, `marshmallow`,
  `cinnamon_stick`, `orange_slice`, `star_anise`, `peppermint`). New engine
  option: an art item with `"front": true` is painted first and everything
  after goes around it (washes, gouache and pen lines), so boughs sit behind
  the mug instead of showing through its transparent paint. `printify.py`
  sticker prices now match the approved $6.75/$7.40. Tee, sweatshirt, mug,
  art print and sticker created as Printify drafts (Etsy ID check still
  pending: 0 of 26 products had an Etsy listing ID).
- 2026-10-01 (15:19 UTC run, pattern day): Christmas Cookies, an all-over
  watercolor mug wrap (gingerbread men, iced sugar cookies in five shapes,
  candy canes, peppermints, holly, star anise and sprinkles on cream; no
  lettering; new motifs `gingerbread_man`, `sugar_cookie` with kinds star,
  tree, heart, round and mitten, `candy_cane`, `sprinkles`; the cookie's baked
  edge is painted as a ring so blue and pink icing stay clean). Wrap mug and
  accent mug (Red, Light Green, Maroon) created as Printify drafts (Etsy ID
  check still pending: 0 of 31 products had an Etsy listing ID).
- 2026-10-02 (15:18 UTC run, motif day): Sufganiyot Season, a watercolor
  Hanukkah design (a lit nine-branch gold menorah with blue candles over a
  plate of jam-filled sufganiyot dusted with sugar, two dreidels with nun,
  gimel, shin and hei, gold and silver gelt, olive sprigs; subline "jelly
  donuts by candlelight"; new motifs `menorah`, `flame`, `plate`,
  `sufganiyah`, `dreidel`, `gelt`, `olive_sprig`). Tee, sweatshirt, mug, art
  print and sticker created as Printify drafts: today's paid listing fees were
  already at the $3.00 cap, so they publish on the next run with room.
- 2026-10-05 (owner request: list for every Etsy gift category): the 5
  Sufganiyot Season drafts went live on Etsy. Two new designs went live the same
  day: **Pumpkins & Purrs** (a watercolor black cat with pumpkins, a mushroom,
  maple leaves, a crescent moon and bats; subline "a cozy spooky season"; new
  motif `cat` with `tail` 1/-1 and `color`/`color2` for other coats; the tail
  is painted around the body so it sits behind it) for Halloween and pet
  owners, and **Grandma's Garden** (a rose bouquet; subline "picked with love")
  for grandparents. "Cookies at Grandma's" was rejected in trademark screening
  (GRANDMA'S cookies is a Frito-Lay brand) and "where love grows" too (LOVE +
  GROW CLOTHING CO). 15 paid listings = $3.00, the daily cap.
- 2026-10-05 (15:18 UTC run, gift-category queue rows 1-2): **Scorpio
  Constellation** (the Scorpius stars in gold on a watercolor night sky,
  framed by November chrysanthemums, the birth-month flower; "October 23 -
  November 21") and **Campfire Season** (a campfire, an orange tent, pine
  trees and snowy mountains under a crescent moon; subline "s'mores under the
  stars") for Gifts for Him. New motifs `night_sky`, `constellation`
  (`scorpius`, `libra`), `chrysanthemum`, `marigold`, `libra_scales`,
  `mountains`, `pine_tree`, `tent`, `campfire`. 10 Printify drafts ($0; the
  day's $3.00 cap was already used). Libra Constellation was painted but held:
  a pending LIBRA application for t-shirts and sweatshirts (Astryx LLC,
  99209588). Sticker tag "nalgene sticker" was dropped (a brand).
  `photos.py` close-ups for opaque art-print files now follow color
  saturation instead of transparency, so they land on the painting.
