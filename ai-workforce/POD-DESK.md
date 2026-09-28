# Print-on-demand desk: watercolor designs for Etsy + Printify

Owner directive, 2026-09-28: do what the reel showed (AI agents making cute
watercolor shirt designs sold on Etsy through Printify), learn the watercolor
look, do it smartly, and make the agents capable of it.

The owner opens the Etsy shop, links a free Printify account, uploads and
publishes. Agents never sign in to Etsy or Printify, never publish, and never
set the final price.

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
| 1 | Trend Scout + Market Research Agent | Pick a niche and phrase buyers actually search for (books, dogs, gardening, teachers, nurses, coffee, seasons, hobbies). Check the `pod_designs` collection so nothing repeats. Avoid anything tied to a brand, show, team, celebrity or franchise. |
| 2 | Legal Desk: IP & Trademark Counsel | Before any art is made, search the phrase (WebSearch: "<phrase> trademark clothing", Justia/uspto.report results; tmsearch.uspto.gov is blocked from our sessions, so say so). Reject phrases that are a registered or pending clothing mark, an existing apparel brand name, or a known enforced format (e.g. "Saturdays Are For ..."). Record what was searched and found in `listing.trademark_check`. |
| 3 | Brand & Graphic Design Agent | Write `pod-kit/designs/<id>.json`: template (arch, stack, badge, wreath), lettering and fonts, motifs from `motifs.py`, bouquet flowers (use "none" for spots hidden behind objects), palette, shirt colors, seed. New motif needed? Add it to `motifs.py` following the pattern: a light first wash, darker wet-on-dry shaping, details, optional loose ink line. |
| 4 | Quality Bar Agent | `python3 design.py designs/<id>.json OUT --preview` and look at the paper image and mockups. Fix anything muddy, anything hidden behind transparent paint, awkward overlaps, lettering too small to read on a shirt at 3 m, or objects that don't read (a dog should read as a dog). Change the seed if a wash lands badly. |
| 5 | Copywriter + SEO Agent | The `listing` section: a title of 140 characters max, front-loaded with the phrase buyers search; 13 tags of 20 characters max, all different, real search phrases; a 2-3 sentence product description (the standard how-it's-made, details and care text is added automatically); products; a price note with a source. |
| 6 | Grammar & Copy Editor, Deliverable QA Reviewer | `python3 build.py designs/<id>.json OUT` (full size). build.py refuses the build if a title, tag or trademark rule is broken. Check `<id>.png` is 4500 x 5400 with a transparent background. |
| 7 | Legal Desk (all ten counsel) | One `legal_reviews` doc: trademark (the phrase, tags, title), copyright (original art, OFL fonts in `pod-kit/fonts`), platform (Etsy's production-partner disclosure; the description says the art is digitally painted by the studio and printed by a production partner), advertising (no claims like "best seller" or "free"). |
| 8 | Chief of Staff | Approve or deny, only with a `cleared` legal review, in `decisions`. |
| 9 | Publish Coordinator | Publish `OUT/index.html` as a private artifact (`capabilities {"downloads": true}`, all files in OUT). Email the owner the link, title and one mockup. Add a `pod_designs` doc {title, phrase, niche, artifact, created, status: "delivered"}. |

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

One design every weekday, from the "Edgex POD desk" Routine, delivered by
email like the coloring books. The owner can ask for a themed batch from the
Studio Floor at any time.

## Done

- 2026-09-28: Currently Reading, Morning Walks & Good Dogs, Strawberry Season
  ("Farmers Market Club" rejected in trademark screening: existing apparel
  brand, and a FARMERS MARKET clothing filing).
