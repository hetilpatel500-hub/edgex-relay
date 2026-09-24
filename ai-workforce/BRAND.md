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
- **Landing pages** ($500-1,500), **research reports** ($300-800), and
  **dashboards** ($600-2,000) are still the **old, unverified numbers** —
  nobody has actually researched real market pricing for these yet.
  Treat them as provisional; Market Research Agent should research each
  before the studio prices from them with any real confidence.
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
