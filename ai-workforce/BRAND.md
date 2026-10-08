# Edgex — Studio Identity & Operating Rules

Single source of truth for identity, tone, money, and compliance. Every
agent that produces a client-facing draft (email, proposal, post, invoice)
follows this file. Set from the owner's direct answers on 2026-09-24.

## Identity

- **Business name: Edgex.**
- **The owner stays anonymous in every client-facing draft** — never name
  them, in an email, proposal, post, or anywhere a client/prospect sees.
  Sign outreach and support messages as **Ava, from Edgex**. Sign formal
  documents (proposals, invoices, contracts) as **The Edgex Team**.
- "Ava" is a business voice, not a fabricated person: no invented age,
  photo, backstory, or claims of being human when directly asked. If a
  prospect asks outright whether they're talking to a person or an AI
  system, answer honestly — that's a different thing from disclosing the
  owner's name, and honesty there isn't optional.
- Heads-up, not a blocker: depending on jurisdiction, a formal contract
  (not a casual email) may still legally need to name the real
  responsible party somewhere in the fine print, even under a trade name.
  Worth a 10-minute check with a local resource before the first real
  contract goes out — flagging it here so it doesn't get missed, not
  treating it as solved.

## Voice & tone

Warm, clear, contemporary. **Soft but authoritative** — confident without
being pushy, approachable without being sloppy. Short sentences over
clever ones. This is the tone for every piece of client-facing copy:
outreach, landing pages, social posts, support replies.

## Payment

Processor: **Stripe** — owner already has an account. Connector added via
claude.ai → Settings → Connectors (same mechanism as Gmail); once live,
`finance-bookkeeping-agent` creates real Payment Links/Invoices from
approved deal cards. Creating one is safe (nothing charges or notifies
the client); sending or sharing it with a client follows the same
explicit-approval rule as every other client-facing action. Actually
sending a real invoice is still the owner's own confirmed action.

## Pricing philosophy — updated 2026-09-24, real research required

**The price for any specific deal comes from real market research on that
specific opportunity, never from defaulting to a generic band.** The
studio was caught pricing every automation deal at a flat $950 pulled
straight from the catalog below, without ever checking what the market
actually pays for that exact kind of work — real 2026 research on
AI-automation agencies shows a custom-built single-workflow automation
like the studio's actually runs **$3,000–$10,000 setup** plus
$300–$800/mo ongoing support industry-wide (see `market-research-agent.md`
for sourcing). $950 wasn't a deliberate discount decision; it was an
unresearched number. That doesn't happen again.

**The rule going forward:** before any deal card gets a price, Market
Research Agent researches what real, comparable providers actually charge
for *that specific service, in that specific niche* — competitor pricing,
industry pay surveys, marketplace comparables, cited sources. The catalog
below is a **rough starting reference only**, not a target and not a
ceiling. When real research and the catalog disagree, **real research
wins** — Proposal & Contract Agent prices from the research, and flags
the catalog as stale for Chief of Staff to reconcile later.

The studio can still choose to price below what big agencies charge —
lower overhead, faster turnaround, and building repeat business are real
advantages — but that has to be a **deliberate, evidence-based choice**
("we're pricing at the low end of the real $3k-$10k range because we're
leaner, not below it because we never checked"), not an accident of
reaching for a round number.

**Studio catalog (starting reference, updated 2026-09-24 where noted):**
- **Automations** (one-time build): $2,000–$6,000, positioned toward the
  low-to-mid end of the real $3,000–$10,000 market range — updated from
  the old unresearched $750-3,000 band. Add an optional $300–$800/mo
  maintenance retainer where a client wants ongoing tuning.
- **Content packages**: $800–$2,500/mo, positioned toward the low end of
  the real $1,000–$5,000/mo typical range for single-location local SEO
  and content — updated from the old unresearched $400-1,200/mo band.
- **Chatbot/lead-capture builds** (new catalog item, backed by real
  research): $1,500–$4,000 setup plus $500–$1,500/mo, positioned toward
  the low end of the real $2,000–$5,000 setup / $500–$2,500/mo range.
- **Landing pages**: $500–1,500 — confirmed by real 2026 comparables
  for a custom-designed page with basic CRO (clicksgeek.com, pitchsite.io,
  eseospace.com). A fuller package with real copywriting and CRO strategy
  runs $1,500–3,000; price toward that only when that scope is included.
  (Chief of Staff sign-off: decisions/2026-09-25-landing-pages-pricing-signoff.)
- **Research reports (competitor-analysis write-up)**: $400–900 — replaces the old unresearched $300-800.
  Freelance fixed-price competitor write-ups run $100–400 (commodity
  floor); full enterprise competitor-analysis projects run $8,000–30,000
  (wrong tier). $400–900 is deliberate lean positioning above the floor,
  justified by real cited sourcing. (decisions/2026-09-24-research-reports-pricing-signoff.)
- **Custom market research reports (broader scope: market sizing, demand
  evidence, buyer/persona analysis — not just a competitor write-up)**:
  $1,500–5,000, with a $299–499 fast-turnaround budget tier for a
  narrower ask and full enterprise projects running $5,000–40,000+.
  This is a genuinely different, higher-scope product from the
  competitor-write-up line above, not a replacement for it — sourced from
  fiverr.com/resources/guides/costs/market-researcher, blackridgeresearch.com,
  yunojuno.com, thefarnsworthgroup.com, and preuve.ai (2026).
  (decisions/2026-09-25-research-reports-tier-added.)
- **Fixed-price SEO audit (checklist-based, no implementation)**: $450-$750 for a single small-business site, positioned at the low-to-mid end of the real $300-2,500 range for this MONEY-MAP item 42 tier -- distinct from the broader Research reports and Custom market research report lines above. (decisions/2026-09-25-skill-work-batch-2.)
- **Dashboards** (custom reporting build, e.g. a Looker Studio dashboard
  connecting a client's existing data — GA4, Google Sheets, CRM exports):
  $2,000–$6,000 one-time — replaces the old unverified $600-2,000 band.
  Sourced from real 2026 freelancer/consultant pricing for a standard
  3-5 connected-report build with standard data sources (lets-viz.com
  "Looker Studio Consultant Cost: 2026 Pricing Guide", datastudio-experts.com
  "How Much Does It Cost to Hire a Looker Studio Freelancer in 2026?").
  If a client's data needs a genuinely custom pipeline (an ERP or a
  proprietary database via a BigQuery-style connector, not just
  connecting standard sources) that's materially more build work —
  $5,000–$15,000 — and should be scoped and priced as that larger job,
  not quoted from this line. (decisions/2026-09-25-dashboard-pricing-signoff.)
- Marketplace listings (Fiverr, Etsy) are priced from that marketplace's
  own real comparables, not this catalog — see storefront/fiverr/RESEARCH.md
  and storefront/etsy/PACKAGE.md.
- **Retainers** (general ongoing service): $1,000-4,000/mo — plausible
  against the chatbot-retainer research above, not independently verified
  beyond that.

## Geographic reach & compliance

Pursue leads across **North America and Europe**. Don't skip a region for
being more paperwork — only skip a specific action if it would actually
be illegal.

**EU/UK outreach specifically:** unsolicited B2B commercial email is
generally permitted under GDPR/PECR when it (a) is sent to a business
contact in their business capacity, (b) clearly identifies the real
sending business (Edgex) and a working reply address, and (c) includes a
simple, working opt-out. Every EU-directed draft must include all three.
This is operating guidance, not legal advice — flag anything that looks
like it's actually targeting an individual consumer rather than a
business contact, since that's a stricter category the studio doesn't
currently have clearance to approach.

**Australia (Spam Act 2003):** there is no B2B exemption from consent —
it must be express or inferred (e.g. the address is conspicuously
published for business purposes and the message relates to that
person's role). Every message must clearly identify Edgex as the sender
and include a functional unsubscribe that keeps working for at least 30
days, with opt-outs actioned promptly (about 5 business days). Sources:
ACMA, Sprintlaw, DLA Piper Data Protection Guide (2026). Adopted in
decisions/2026-09-24-au-spam-act-compliance-adopted.

**Canada (CASL):** commercial email needs consent — express, or implied
(e.g. an existing business relationship, or the address was
conspicuously published without a "no unsolicited messages" notice and
the message is relevant to the recipient's business role). Every message
must identify the sender and include **a valid mailing address** plus one
other contact method (email, phone, or web), and an unsubscribe that is
honoured within 10 business days and works for at least 60 days after
sending. The mailing-address requirement conflicts with keeping the
owner anonymous: before any Canadian outreach, the owner must supply a
business mailing address (a PO box or virtual business address works) —
until then, Canadian leads stay research-only. Adopted in
decisions/2026-09-25-casl-compliance-adopted; the original shift's full
write-up was lost to a blocked git push, so this summary was rebuilt
from the CASL requirements themselves — re-verify against the CRTC's
current guidance before the first Canadian send.

## Sales motion

**Fully async — no phone calls.** `sales-call-prep-agent` stays on the
roster but goes unused unless the owner explicitly decides to take a
call themselves. Closing happens through Proposal Writer's deal cards and
Account Manager's async messages, both still gated by the same
explicit-approval rule as every other client-facing action.

## Lead sourcing

**Web search only, no paid API — this was checked and corrected.** Yelp's
current offering is a paid data-licensing product (checked 2026-09-24:
$229-643/month, no free tier), not the free API this file originally
assumed. Not worth it pre-revenue. Revisit once the studio has paying
clients to justify the cost; Google Places (usage-based, has a monthly
free credit) and OpenStreetMap/Overpass (fully free, weaker contact-info
coverage) are the candidates to check then — verify actual current
pricing before recommending either, the same way this entry got fixed.
