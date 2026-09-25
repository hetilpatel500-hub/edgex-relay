# Fiverr fulfillment playbook

How an order goes from "new order" to "delivered" on time. You (the
owner) do the Fiverr clicks; agents do the work. Rule of thumb: agents
finish by the halfway point of the delivery window, so there is always
time for your read-through and one fix.

## 0. Tools and limits to know

- **No Fiverr connector exists.** Agents can't see orders or messages.
  They only know what you forward.
- **Files out:** agents can't download from Canva or Gamma in this
  environment (network policy). For decks, agents send you the Gamma
  link and you export PDF/PPTX there. For text work, agents write the
  file into `storefront/fiverr/orders/<order-number>/deliver/` and, when
  Google Drive is connected in that session, also put a copy in a Drive
  folder named `Edgex Fiverr Orders/<order-number>`.
- **Gamma free plan:** 10 slides per deck, about 60 credits per deck,
  340 credits left on 2026-09-25 (about 5 decks). If credits drop under
  120, pause Gig 3 in Fiverr (Gigs > Pause) and raise a Gamma upgrade in
  the weekly budget meeting.
- **Canva:** the free resize quota is used up. Gig images are already
  done, so this only matters for new designs.

## 1. When an order arrives (you, 5 minutes)

1. Open the order in Fiverr. Check the requirements are answered.
2. **Check the AI question.** If the buyer answered "No, I need AI-free
   work", don't start. Send the "AI-free decline" message below and use
   Resolution Center > cancel the order. Fiverr requires us to honor
   that request.
3. If requirements are missing, send the "missing info" message below.
   The Fiverr clock doesn't start until requirements are in.
4. Forward the order to the studio. In a Claude session in this repo,
   paste this block filled in:

```text
NEW FIVERR ORDER
Order number:
Gig: (1 product descriptions / 2 landing page / 3 pitch deck / 4 research)
Package: (Basic / Standard / Premium)
Due date and time (from Fiverr):
Buyer's answers to the requirements (paste all):
Attachments: (paste text, or say "uploaded to Drive folder <name>")
Anything the buyer said in messages:
```

## 2. Who does what (agents)

Each order gets a deal card from the package (scope = the package text
in PACKAGE.md, nothing more) and a folder
`storefront/fiverr/orders/<order-number>/` with `brief.md` (your pasted
block), drafts, and `deliver/`.

| Gig | Steps, in order |
|---|---|
| 1. Product descriptions | SEO Agent picks one keyword per product from the buyer's material → Copywriter drafts → (Amazon: format to title + 5 bullets + backend terms) → Last Touch |
| 2. Landing page | Competitor Analysis reads 3 competitor pages (Standard/Premium) → Copywriter drafts sections, headline options, meta tags (and 3 emails for Premium) → Last Touch |
| 3. Pitch deck | Copywriter writes slide text (≤10 slides) from buyer notes → Market Research + Competitor Analysis add cited market and competitor slides (Premium) → Brand & Graphic Design builds it in Gamma with the buyer's colors → speaker notes + 1-page summary (Premium) → Last Touch |
| 4. Research | Market Research + Competitor Analysis gather facts with links → Data Analyst builds tables → Copywriter writes takeaways → a checker opens every link to confirm it says what we claim → PDF → Last Touch |

Hard rules for every order:
- Scope is exactly the package. Anything extra is a custom offer, not a
  freebie.
- Never invent facts, reviews, stats or results. Buyer-supplied numbers
  only; market facts only with a link.
- Write for this buyer. No reused text between orders.
- Health, finance, legal or safety claims: flag them to the buyer for
  their sign-off.

## 3. Last Touch (agents), then your read (you)

**Last Touch** (DEAL-DESK.md): Grammar & Copy Editor → Visual &
Formatting Reviewer → Tone & Sensitivity Reviewer → Brand Consistency
Checker → Final Release Coordinator stamps CLEARED. Deliverable QA checks
every package bullet is delivered and no placeholder text is left
([brand], TODO, lorem ipsum).

**Your read (5-10 minutes), then Deliver:**
- [ ] Does it answer what the buyer asked for, in their words?
- [ ] Right count (products, words, slides, competitors)?
- [ ] Any fact you can't trace to the buyer's material or a link? Send it back.
- [ ] Any leftover placeholder or odd sentence? Send it back.
- [ ] Files open correctly (PDF, Word, PPTX, CSV)?

Chief of Staff logs the delivery decision to `decisions` like any other
client-facing action.

## 4. Timing

| Delivery window | Agents finish by | You deliver by |
|---|---|---|
| 3 days | end of day 1 | day 2 |
| 4-5 days | end of day 2 | day 3-4 |
| 6-7 days | end of day 3 | day 5 |

If an order is at risk, ask the buyer for more time **before** the due
time (Fiverr: Extend delivery date). Never deliver late and never
deliver unfinished work to stop the clock.

## 5. Revisions and messages

- Paste the buyer's revision request to the studio with the order
  number. Same flow, same Last Touch, same read.
- A revision that asks for new scope (more products, more slides) is a
  custom offer. Agents draft it; you send it.
- Buyer messages before an order: paste them to the studio; agents draft
  a reply within the hour when a session is active; you paste it back.
  Fast replies help Fiverr ranking.
- Sign Fiverr messages "The Edgex Team". (BRAND.md allows "Ava, from
  Edgex" for email, but on Fiverr the account holder is one verified
  person, so a named persona risks looking like misrepresentation.
  Flagged for Chief of Staff.) If a buyer asks whether they're talking
  to a person or AI, answer honestly.

## 6. After delivery

- Fiverr auto-completes 3 days after delivery if the buyer does nothing.
  Money clears 14 days after completion.
- Tell the studio "order <number> completed, $<price>". Finance &
  Bookkeeping logs revenue at 80% of the price (Fiverr keeps 20%), and
  marks it cleared 14 days later.
- Ask for a review only through Fiverr's normal flow. Never offer
  anything in exchange for a review.

## Message templates (paste into Fiverr)

**Thanks + start** (after requirements are in)
```text
Thanks for your order! We have everything we need and we've started. You'll get your delivery on or before the due date. If anything changes on your side, just message us here.

The Edgex Team
```

**Missing info**
```text
Thanks for your order! Before we start, could you send: <list>. As soon as we have it, we'll get going.

The Edgex Team
```

**AI-free decline**
```text
Thanks for choosing us. You mentioned you need AI-free work. Our process uses AI tools for research and drafts, with a person reviewing everything, so we don't think we're the right fit for this order. We'll request a cancellation so you get a full refund. Sorry for the trouble, and good luck with your project.

The Edgex Team
```

**Delivery**
```text
Your order is ready! Attached: <files>. Everything is written for your brief. Please take a look, and if anything needs changing, request a revision and tell us what to adjust. You have <N> revisions included.

The Edgex Team
```

**Extension request** (only before the due time)
```text
Quick update: we want to get this right and need <N> more day(s) for <reason>. We've sent an extension request. If that doesn't work for you, tell us and we'll deliver on the original date.

The Edgex Team
```
