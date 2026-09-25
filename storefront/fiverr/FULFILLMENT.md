# Fiverr fulfillment playbook

How an order goes from "new order" to "delivered" on time. You (the
owner) do the Fiverr clicks; agents do the work. Rule of thumb: agents
finish by the halfway point of the delivery window, so there is always
time for your read-through and one fix.

## 0. Tools and limits to know

- **No Fiverr connector exists.** Agents can't see orders or messages.
  They only know what you forward.
- **Files out:** agents build every deliverable locally and write it
  into `storefront/fiverr/orders/<order-number>/deliver/`. When Google
  Drive is connected in that session, they also put a copy in a Drive
  folder named `Edgex Fiverr Orders/<order-number>`. You download from
  there and attach the files in Fiverr.
- **Builders (no cost, no watermark):**
  - Word files (Gigs 1-2): `python3 tools/md_to_docx.py draft.md out.docx`
  - Decks (Gig 3): `python3 tools/build_deck.py spec.json deck.pptx`
  - PDF from either: `soffice --headless --convert-to pdf <file>`
  - These need `pip install python-docx python-pptx` and LibreOffice
    Impress/Writer (`apt-get install libreoffice-impress
    libreoffice-writer fonts-crosextra-carlito`) in a fresh session.
- **Don't use Gamma for buyer decks.** Free Gamma exports carry a "Made
  with Gamma" watermark. Upgrading is a spend for the weekly budget
  meeting, not an agent decision.
- **Canva:** the free resize quota is used up. Gig images are already
  done, so this only matters for new designs.

## 1. When an order arrives (you, 5 minutes)

1. Open the order in Fiverr. Check the requirements are answered.
2. **Check the AI question.** If the buyer answered "No, I need AI-free
   work", don't start the work. Fiverr requires us to honor that.
   - First send the "AI-free check" message below. Sometimes buyers
     click "No" by mistake; if they reply in chat that AI-assisted work
     is fine, save that reply and go ahead.
   - If they do want AI-free work, open Resolution Center > request a
     cancellation, reason: we can't meet their requirement. The buyer
     has 48 hours to accept; if they don't respond, Fiverr cancels
     automatically and refunds them. Tell the buyer this in the message.
   - Cost: cancellations can count against our Order Completion Rate
     (Fiverr says some cancellation types weigh less). It's still the
     right call, and the up-front FAQ and requirement question exist to
     make it rare. Tell the studio about every one, so we can see if a
     gig's wording needs to be clearer.
   Sources: [Cancel an order with the Resolution Center](https://help.fiverr.com/hc/en-us/articles/37332582945169-Cancel-an-order-with-the-Resolution-Center), [How cancellations work for freelancers](https://help.fiverr.com/hc/en-us/articles/47789995041297-How-cancellations-work-for-freelancers)
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
| 3. Pitch deck | Copywriter writes slide text (8-10 slides) from buyer notes → Market Research + Competitor Analysis add cited market and competitor slides (Premium) → Brand & Graphic Design writes the deck spec (buyer's colors, logo, slide types) and runs `tools/build_deck.py`, then exports a PDF → speaker notes + 1-page summary as .docx (Premium) → Last Touch |
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
- [ ] **Research (Gig 4) and Premium decks: spot-check 3 sources.** Pick
      3 cited links at random, open each, and confirm the page loads and
      says what our report says (same number, same claim). If any one
      fails, send the whole thing back for a full link check. The gig
      copy says a person checks the sources: this is that check.

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

**AI-free check** (send before any cancellation)
```text
Thanks for your order! Quick check before we start: you answered that you need AI-free work. Our process uses AI tools for research and drafts, with a person reviewing everything. If AI-assisted work is fine after all, just reply here and we'll begin. If you do need AI-free work, we're not the right fit, and we'll send a cancellation request so you get a full refund. You'll have 48 hours to accept it, and Fiverr cancels it automatically if there's no reply. Sorry for the trouble.

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
