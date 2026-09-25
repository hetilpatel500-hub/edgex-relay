# Fiverr research notes (2026-09-25)

Market Research Agent + Competitor Analysis Agent + SEO Agent.
Method: web search only. The Fiverr Help Center and most third-party pages
were blocked from direct fetch in this session, so the rules below come from
search-result text quoting those pages. Where sources disagree, it says so.
Re-check anything marked "unconfirmed" on the live Fiverr screens.

## 1. Fiverr rules that affect Edgex

### AI use and disclosure
- AI use is allowed in every category. Fiverr's guideline says AI should
  "support the freelancer's own skill and effort, not as a replacement for
  them," and work must be "high-quality, customized" to the client. The
  freelancer is "fully accountable" for what is delivered.
  Source: [Using AI on Fiverr: Guidelines for freelancers and clients](https://help.fiverr.com/hc/en-us/articles/37333301560593-Using-AI-on-Fiverr-Guidelines-for-freelancers-and-clients)
- Freelancers are not forced to list every tool in the gig, but must
  honor a client's explicit "no AI" request and disclose their workflow
  when the client states that preference. (same source)
- Penalty for "misrepresentation of AI usage" or "deception about how work
  was delivered": order cancelled, full refund, account may be
  permanently suspended. (same source; also [How we enforce policies](https://help.fiverr.com/hc/en-us/articles/22569899568913-How-we-enforce-policies))
- Generic, unmodified, or reused AI output does not meet Fiverr's quality
  standard. Source: [AI Disclosure on Fiverr and Upwork, Memvers](https://memvers.com/blog/ai-disclosure-rules-freelance-platforms-2026) (third-party summary)
- **Decision:** every gig says plainly that the work is AI-assisted and
  human-reviewed. We never market "hand-written" or "100% human." We do
  not take orders where the buyer asks for no AI; the playbook says to
  decline those politely before starting. This also covers BRAND.md's
  honesty rule.
- **Real risk to flag:** Fiverr frames AI as a tool supporting a
  freelancer's own skill. Edgex's model is agents doing most of the work,
  with the owner relaying. To stay inside the rule, the owner must
  actually read and approve every delivery (the Last Touch step in
  FULFILLMENT.md), and the gig text must never hide the AI workflow.

### Account and identity
- One account per person; a second account can get both banned. Only
  exception is a seat inside one Team Account.
  Source: [Fiverr Tutorials: Can you have two Fiverr accounts?](https://fiverrtutorials.com/fiverr-secrets-multiple-fiverr-accounts/), [Community Standards](https://help.fiverr.com/hc/en-us/articles/32242973123985-Our-Community-Standards)
- Identity verification: name, address and business info must match the
  owner's government ID exactly, entered in English. Tax form (W-9 for US,
  DAC7 info for EU) before gigs go live.
  Sources: [Verifying your identity as a new freelancer](https://help.fiverr.com/hc/en-us/articles/6348992414097-Verifying-your-identity-as-a-new-freelancer), [Personal & business information verification](https://help.fiverr.com/hc/en-us/articles/22582440968849-How-to-verify-your-personal-and-business-information), [W-9 collection](https://help.fiverr.com/hc/en-us/articles/360011135837-W-9-collection), [Fiverr Tutorials seller guide](https://fiverrtutorials.com/fiverr-getting-started)
- **Username is permanent** (it is the profile URL fiverr.com/username).
  A separate **display name** exists and can be changed later.
  Sources: [Managing your display name](https://help.fiverr.com/hc/en-us/articles/13409224346257-Managing-your-display-name), [Fiverr Tutorials: change username](https://fiverrtutorials.com/how-to-change-fiverr-username)
- **Unconfirmed:** one 2026 third-party video claims the display name must
  match the ID. Fiverr's own help page describes display name as a
  public name you can change. Expect "Edgex" to work as display name; if
  Fiverr rejects it, fall back to the owner's first name + last initial.
  Source of the claim: [YouTube: Fiverr ID verification name match](https://www.youtube.com/watch?v=g8Po6LWLZkc)
- Profile photo: Fiverr allows an original photo of you, **your company
  logo**, or an image that represents your service. Not another person,
  not a celebrity, not a GIF. So the Edgex logo is allowed and keeps the
  owner anonymous. Face photos convert better, but we don't use one.
  Sources: [Creating & editing your freelancer profile](https://help.fiverr.com/hc/en-us/articles/360010558598-Creating-editing-your-freelancer-profile), [makeaiphotos: Fiverr profile picture rules](https://www.makeaiphotos.com/blog/fiverr-profile-picture-requirements/)
- Never use a stock or AI-generated face as the profile photo. That would
  be a fabricated person (BRAND.md) and misrepresentation (Fiverr).

### Gig limits
- **Active gigs for a new seller: 4** per Fiverr Help Center search
  snippet ("up to 4 active gigs, Level 1 & 2 up to 10, Top Rated up to
  30"). Third-party blogs still say 7. Plan for 4: that's why this
  package has exactly 4 gigs.
  Sources: [Managing your Gigs](https://help.fiverr.com/hc/en-us/articles/360011028318-Managing-your-Gigs), vs. [Fiverr Tutorials seller levels](https://fiverrtutorials.com/fiverr-seller-levels) (says 7)
- Title: max 80 characters; only ~50-60 show on the search card.
- Description: max 1,200 characters.
- Tags: 5 tags, max 20 characters each.
- Package description: 100 characters per tier.
- FAQ: question ~70 chars, answer 300 chars, up to 10 FAQs.
- About/profile bio: 600 characters.
  Sources for these limits (third-party, consistent with each other):
  [SwiftCopy gig description guide](https://swiftcopy.io/blog/how-to-write-fiverr-gig-description),
  [Eduearnhub: Fiverr character limits 2026](https://eduearnhub.com/fiverr-character-limits/),
  [Fiverr Community: title characters](https://community.fiverr.com/forums/topic/312638-how-many-characters-can-we-write-in-fiverr-gig-title/)
- Gig image: recommended 1280 x 769 px, min 712 x 430, max 4000 x 2416,
  JPG/PNG, under 5 MB. Up to 3 images, 1 video, 2 PDFs in the gallery; at
  least 1 image required. Keep text ~70 px from left/right edges.
  Sources: [Creating Gig images and tagging your Gig gallery](https://help.fiverr.com/hc/en-us/articles/15863342952977-Creating-Gig-images-and-tagging-your-Gig-gallery), [touhfa.art gig image guide](https://touhfa.art/blog/thumbnails/fiverr-gig-thumbnail-size-design-guide/), [Fiverr101](https://fiverr101.com/fiverr-gig-image-size/)
- Gig prices start at $5 per package.
  Source: [Creating and managing Gig packages](https://help.fiverr.com/hc/en-us/articles/360010559138-Creating-and-managing-Gig-packages)

### Money
- Seller fee: flat **20%** of every order, incl. extras and tips. A $100
  order pays $80.
  Sources: [Fiverr Help Center search result on seller revenue](https://help.fiverr.com/hc/en-us/articles/360050216133-Paying-for-orders-extras-or-custom-offers), [FreelancerCalculator 2026](https://freelancercalculator.com/fiverr-seller-fees-2026-official-guide/)
- Buyer pays a 5.5% service fee, plus $3.50 on orders under $200.
  Same sources.
- **Clearance: 14 days** after the order completes, for new sellers.
  7 days only for Seller Plus / Top Rated / Pro. Then withdrawal fees
  depend on method.
  Sources: [Your earnings page](https://help.fiverr.com/hc/en-us/articles/9234443621137-Your-earnings-page), [Early Payout](https://help.fiverr.com/hc/en-us/articles/4402267122449-Early-Payout), [Withdrawing your earnings](https://help.fiverr.com/hc/en-us/articles/360010530058-Withdrawing-your-earnings-managing-payout-methods)
- So the first real dollar lands roughly 2-3 weeks after the first order
  is delivered and accepted (delivery days + up to 3 days auto-complete
  + 14 days clearing). Plan cash around that.

### Other
- Keep all buyer communication inside Fiverr. No emails, phone numbers,
  or outside links for contact. (Fiverr Community Standards.)
- New-seller pricing: enter at the low end of the market, collect 10-15
  reviews at 4.8+, then raise prices step by step.
  Sources: [Eduearnhub pricing strategy](https://eduearnhub.com/fiverr-gig-pricing-strategy/), [Zenlance pricing](https://zenlance.net/how-to-price-your-fiverr-gigs-2/)

## 2. Gig choice

Picked 4 (the new-seller cap). All four are deliverable end-to-end with
tools the studio actually has: writing, WebSearch, Gamma (decks, PDF and
PPTX export), Canva (images, report layout).

| Gig | Tool path | Why it's safe to deliver |
|---|---|---|
| Product descriptions | Copywriter + SEO Agent, text | Pure writing; buyer supplies product facts |
| Landing page copy | Copywriter + SEO Agent, text | Pure writing; copy only, no build |
| Pitch deck | Copywriter + Gamma (PPTX/PDF) | Gamma generates and exports decks |
| Market/competitor research | Market Research + Competitor Analysis, WebSearch, PDF | Desk research with cited public sources |

Skipped: anything video (vidIQ credits exhausted), LinkedIn ghostwriting
(needs ongoing founder voice interviews; weaker fit for fully async), web
development (studio can't host/build for a buyer reliably yet), logos
(heavy revision cycles, image-only tools).

## 3. Pricing evidence per gig

All prices below are what real Fiverr sellers list, found via search on
2026-09-25. "From $X" is the Basic price shown on the gig card.

### Product descriptions
- Fiverr category page: typical order $100-$120 for e-commerce product
  descriptions. [Fiverr category](https://www.fiverr.com/categories/writing-translation/buy/product-description/e-commerce-store)
- Low end: from $5 ([rocky49](https://www.fiverr.com/rocky49/write-shopify-description-with-seo), [maddogondray](https://www.fiverr.com/maddogondray/do-professional-descriptions-for-your-shopify-store)), $10 with SEO ([sumitselim](https://www.fiverr.com/sumitselim/write-shopify-description-shopify-seo-title), [narafi](https://www.fiverr.com/narafi/write-shopify-product-description-with-shopify-seo)), $20 ([folkiptv](https://www.fiverr.com/folkiptv/write-your-product-description-and-articles)).
- Upper: $125 ([faswaldo](https://www.fiverr.com/faswaldo/write-catchy-product-descriptions)), $150 ([twocakes](https://www.fiverr.com/twocakes/write-a-unique-product-description)); a Pro seller at ~$175 for 10 (~$17.50 each), per search summary.
- **Our price:** $35 / 5, $65 / 10, $150 / 25 descriptions (about
  $6-7 each). Low end of the real range on purpose: no reviews yet.
  Above the $5 race-to-bottom, well under the $100-120 category norm.

### Landing page copy
- Fiverr copywriting marketplace: landing page copy commonly $41-$211.
  [Fiverr gigs: landing page copy](https://www.fiverr.com/gigs/landing-page-copy)
- Real gigs: $20 ([the_copy_girl](https://www.fiverr.com/the_copy_girl/be-your-sales-page-copy-and-landing-page-copywriter)), $75 ([sam2406](https://www.fiverr.com/sam2406/copywrite-your-landing-page-to-accelerate-sales)), $80 ([tonyykay](https://www.fiverr.com/tonyykay/be-your-strategic-copywriter-for-landing-page-ad-copy-and-website-content)), $100 ([creat1vepattern](https://www.fiverr.com/creat1vepattern/write-your-landing-page-content)).
- Specialists: $150-$500 per page; off-platform strategic pages $750-$3,000+.
  [Copywriting rates 2026, NewMedia](https://newmedia.com/blog/copywriting-rates), [Damongo 2026 rates](https://damongo.com/freelance-copywriter-rates-2026-how-much-to-charge/)
- **Our price:** $60 / $110 / $190. Basic sits at the low-mid of the
  $41-211 band; Premium stays under the $211 top so a new seller isn't
  the most expensive option in search.
- Note: BRAND.md lists landing pages at $500-1,500 as "old, unverified."
  That band is for a built page off-platform. Fiverr copy-only pricing is
  much lower. Flag for Chief of Staff: the catalog number does not apply
  to Fiverr.

### Pitch deck
- Fiverr pitch deck category: typical $200-$250.
  [Fiverr pitch decks category](https://www.fiverr.com/categories/business/online-presentations/pitch-decks)
- Real gigs: $40 ([robertwycliffe](https://www.fiverr.com/robertwycliffe/create-your-investor-ready-pitch-deck)), $70 ([waseem100](https://www.fiverr.com/waseem100/create-a-professional-business-presentation-or-investor-pitch-deck)), $80 ([baritechsol](https://www.fiverr.com/baritechsol/write-research-design-investor-pitch-deck-fund-powerpoint-deck-sponsorship)), $100 ([rrgraph](https://www.fiverr.com/rrgraph/design-a-modern-pitch-deck-presentation)), $110 ([spietrobono](https://www.fiverr.com/spietrobono/create-a-professional-pitch-deck-presentation)), $200 ([adamazurek](https://www.fiverr.com/adamazurek/design-a-pitch-deck-presentation-in-powerpoint), [draganna981](https://www.fiverr.com/draganna981/create-3-templates-pitch-deck)), $250 ([sramanaaiift](https://www.fiverr.com/sramanaaiift/create-an-awesome-presentation-and-word-document)), $650 ([williambryan392](https://www.fiverr.com/williambryan392/investor-pitch-deck-presentation-investment-venture-capital-angel-seed-funding)).
- Visible.vc: well-reviewed Fiverr freelancers $50-$200. [Visible.vc](https://visible.vc/blog/pitch-deck-design-cost/)
- **Our price:** $75 / $150 / $260. Basic in line with the $70-$110
  cluster; Premium near the $200-250 category norm because it includes
  writing plus researched market and competitor slides.

### Market / competitor research
- Fiverr cost guide: basic packages $43-$100, standard $100-$200.
  [Fiverr market researcher cost guide](https://www.fiverr.com/resources/guides/costs/market-researcher)
- Real gigs: $15 ([shiva_karampudi](https://www.fiverr.com/shiva_karampudi/research-and-deliver-a-clear-data-or-market-research-report)), $45 ([market_reserchr](https://www.fiverr.com/market_reserchr/do-competitor-analysis-competition-research-competitive-pricing)), $50 ([ziahasan76](https://www.fiverr.com/ziahasan76/create-market-research-based-report-strategy-and-analysis), [muhammadzoha703](https://www.fiverr.com/muhammadzoha703/do-market-research-and-market-analysis-at-low-cost)), $95 ([mila0501](https://www.fiverr.com/mila0501/do-market-research-market-analysis-competitor-analysis-for-you)), $100 ([simonkaruku](https://www.fiverr.com/simonkaruku/complete-a-comprehensive-market-research-report-competitor-analysis), [muneebliaqat56](https://www.fiverr.com/muneebliaqat56/do-market-and-competitor-research-for-your-brand)), $125 ([aadilskb](https://www.fiverr.com/aadilskb/do-business-competitor-research-and-competitive-analysis)), $135 ([tina_kennedy](https://www.fiverr.com/tina_kennedy/conduct-target-market-research-report-for-yoour-business)).
- **Our price:** $45 / $95 / $180. Matches the real basic and standard
  bands. Premium slightly under the $200 standard ceiling.
- BRAND.md lists research reports at $300-800 ("old, unverified"). Fiverr
  desk-research reality is much lower. Flag for Chief of Staff.

### What competitors miss (positioning)
- Most low-price gigs promise "comprehensive" or "SEO" without saying
  what the buyer gets. We list exact counts, word ranges, file types,
  and say every research claim is cited with a link.
- Almost none say how they use AI. We say it plainly. That is both the
  rule-safe choice and a real difference.
- Catch: these categories are crowded with $5-$50 sellers. A new
  account with no reviews will get few impressions at first. Expect
  slow weeks; the first 5-10 orders matter most.

## 4. Search tags and title keywords (SEO Agent)

Tags come from the words real sellers put in titles in search results
above (shopify product description, landing page copy, pitch deck,
investor pitch deck, competitor analysis, market research). No search
volume numbers were available, so none are claimed.
