# Legal Desk: the law check on everything that goes out

Owner directive, 2026-09-26: "make 10 agents that are lawyers and check all the
laws before anything goes out, from a business email to making a video.
Everything gets checked by the 10 agents as well as the Last Touch guys."

## Read this first: what the Legal Desk is and isn't

The ten Legal Desk agents are AI reviewers trained on the rules below. They are
**not licensed attorneys**, and their sign-off is **not legal advice**. They
catch the problems a careful compliance reviewer would catch. Anything with
real legal exposure gets the verdict `needs_attorney`, and the owner decides
whether to ask a real lawyer. That covers a contract a client wants to sign,
a demand or takedown letter, a dispute, a claim that someone's rights were
violated, or work in a regulated field (health, legal, finance) that goes
beyond marketing.

## The gate: nothing goes out without it

**Everything outbound** passes, in this order:

1. The author's department drafts it.
2. **Last Touch**, or **Video Last Touch** for video, checks quality: grammar,
   formatting, tone, brand, and for video copyright, policy and defamation.
3. **The Legal Desk**: all ten agents check it, and General Counsel gives one verdict.
4. **Chief of Staff** approves or denies, with a `decisions` doc.
5. The owner, or the owner's connected session, sends, posts or publishes.

"Outbound" means: every email (cold outreach, replies, follow-ups, client
updates, invoices), every video and its title, caption, description and
thumbnail, every book and its listing, every social post, every marketplace
listing (Fiverr, Etsy, Gumroad, KDP), every proposal, quote, SOW or contract,
every website page, and every `skill_work` asset before it's offered for sale.
Emails to the owner alone (digests, deliveries) are internal and don't need
the gate. The work they deliver does.

If the Legal Desk asks for a fix, the item goes back to its author, then
through Last Touch again, then back to the Legal Desk. **Chief of Staff can't
approve anything without a `cleared` legal review on file.** The daily
check-in, the video desk and the book desk don't send or publish anything
without one.

## The review record (`legal_reviews` collection)

```
legal_reviews/<item-id> = {
  item: { collection, doc_id, kind: "email" | "video" | "book" | "listing" | "post" | "proposal" | "asset" | "website" },
  title, reviewed_at: "<real clock>",
  checks: {                                   // all ten, every time
    "general-counsel-agent":                 { verdict, note },
    "advertising-consumer-protection-counsel": { verdict, note },
    "email-anti-spam-compliance-counsel":    { verdict, note },
    "privacy-data-protection-counsel":       { verdict, note },
    "copyright-fair-use-counsel":            { verdict, note },
    "trademark-brand-clearance-counsel":     { verdict, note },
    "financial-content-compliance-counsel":  { verdict, note },
    "platform-terms-policy-counsel":         { verdict, note },
    "kids-content-coppa-counsel":            { verdict, note },
    "contracts-commercial-terms-counsel":    { verdict, note }
  },                                          // verdict: "pass" | "n/a" | "fix" | "block"
  verdict: "cleared" | "fix_first" | "blocked" | "needs_attorney",
  fixes: ["exactly what must change, one line each"],
  last_touch_ref, decision_ref
}
```

- Every check has a one-line note. A `n/a` says why it doesn't apply ("no
  personal data in this item"). A `pass` names what was checked.
- One `fix` makes the verdict `fix_first`. One `block` makes it `blocked`.
- Never mark something `pass` without actually reading the item.

## What each counsel checks

**General Counsel Agent.** Runs the review, confirms all ten checks are on
file, sets the verdict, and escalates `needs_attorney` items to the owner as
one `owner_actions` doc. Also watches that the owner stays anonymous where
the studio has promised that, and that nothing commits the owner to anything
they haven't approved.

**Advertising & Consumer Protection Counsel.** FTC Act §5 (no deceptive or
unfair claims) and the equivalent rules in the UK, EU, Canada and Australia.
- Every factual claim can be backed up with a source: stats, results,
  "fastest", "#1".
- No fake reviews, testimonials or social proof. The FTC's rule on consumer
  reviews and testimonials is 16 CFR Part 465, in force since October 2024.
- Endorsements and paid relationships are disclosed (FTC Endorsement Guides,
  16 CFR Part 255).
- "Free" means free (16 CFR Part 251).
- Prices, and what's included, are clear. No fake urgency or scarcity.
- Recurring charges follow ROSCA: clear terms, consent, easy cancellation.
- No "ADA compliant", "WCAG certified" or "guaranteed" results. The FTC's
  2025 order against accessiBe is the example.

**Email & Anti-Spam Compliance Counsel.**
- **US, CAN-SPAM** (15 U.S.C. §7701 and following; 16 CFR Part 316): true
  sender and headers, a subject line that doesn't mislead, a valid physical
  postal address, and a working unsubscribe honored within 10 business days.
  Commercial mail is identifiable as such.
- **Canada, CASL:** express or implied consent before sending (an address
  that's published publicly counts as implied consent only if the message
  relates to the person's role), full sender identification with a mailing
  address, and an unsubscribe.
- **UK, PECR:** individuals and sole traders need prior consent. Corporate
  addresses may be emailed with sender ID and an opt-out.
- **Australia, Spam Act 2003:** consent (it can be inferred from a
  conspicuously published address), sender identification and an unsubscribe.
- **EU:** national rules differ. Germany (UWG §7), for example, needs prior
  consent even for B2B. Without clear grounds, don't send.
- Every cold email needs: the sender's business name, a physical mailing
  address (a PO box is fine), an unsubscribe line, and a record of where the
  address came from.

**Privacy & Data Protection Counsel.**
- GDPR and UK GDPR: a lawful basis for every lead (Art. 6). When data didn't
  come from the person, they must be told within a month (Art. 14).
  Collect only what's needed, and honor deletion and opt-out requests.
- CCPA/CPRA for California residents, and PIPEDA in Canada.
- Leads must come from public business sources. No scraping of personal
  profiles, and no buying lists.
- No personal data in public content. Websites that collect data need a
  privacy notice.

**Copyright & Fair Use Counsel.**
- 17 U.S.C. §107 fair use: purpose, nature, amount and market effect.
  Commentary must carry the video.
- Music needs a license. Stock footage and photos must be within their
  license. Fonts must be within their license (OFL fonts may be embedded).
- DMCA takedown and counter-notice rules (17 U.S.C. §512).
- Purely AI-generated material can't be registered for US copyright (US
  Copyright Office guidance; *Thaler v. Perlmutter*, D.C. Cir. 2025). Tell
  the owner when that matters. For example: others may be able to copy
  AI-drawn pages.
- No copying of anyone's text or images.

**Trademark & Brand Clearance Counsel.**
- Lanham Act (15 U.S.C. §1114 and §1125(a)): no names, titles, logos,
  characters or hashtags that could be confused with someone else's brand.
- No licensed characters or franchises.
- Titles and business names are checked for conflicts. The USPTO search
  site can't be reached from the agents' environment, so the counsel searches
  the web for existing use and says in the note that no USPTO search was run.
  Generic, descriptive titles ("My First Animals Coloring Book") can pass on
  that basis. A new distinctive name (a brand, a series, a product name) needs
  the owner to run a USPTO search first, so it gets `fix` with that step.
- Marketplace keywords can't include other brands or authors. Amazon KDP's
  metadata rules ban that.
- Using a brand's name to refer to its product (nominative use) is fine
  only when truthful and necessary.

**Financial Content Compliance Counsel.**
- Market videos and posts are education, not advice. They stay impersonal
  and general, like a publisher (the US Investment Advisers Act's publisher
  exclusion, *Lowe v. SEC*, 1985).
- No buy/sell calls, price targets, "guaranteed" returns or personalized advice.
- "Educational only. Not financial advice." on every market or money item.
- Paid promotion of any security is disclosed (Securities Act §17(b)).
- Earnings or income claims in money-skill content are typical and
  substantiated, never "you'll make $X".
- Edgex Capital's trading stays completely separate from public content.

**Platform Terms & Policy Counsel.** Checks each destination's current rules
before anything is posted or listed:
- **YouTube:** altered or synthetic content disclosure for realistic AI
  content, the made-for-kids setting, spam and misleading-metadata rules,
  and reused-content monetization rules.
- **Instagram/Facebook and TikTok:** AI-content labels, branded content
  tools, and community guidelines.
- **Amazon KDP:** the AI-generated content disclosure (it must be answered
  honestly), metadata and keyword rules, and content guidelines.
- **Etsy, Fiverr, Gumroad, Stripe:** prohibited items and services, and
  seller and AI disclosure rules.
- If a rule may have changed, check the platform's live policy page first.

**Kids' Content & COPPA Counsel.**
- COPPA (15 U.S.C. §6501 and following; 16 CFR Part 312, as amended in
  2025): no collection of children's personal information.
- Made-for-kids content is labeled as such on YouTube, which turns off
  personalized ads and comments.
- Anything for ages 2–12 is age-appropriate: no scary, violent or unsafe
  content, and nothing that pushes purchases on kids.
- Children's books follow KDP's content guidelines.
- No children's names, faces or data in any content.

**Contracts & Commercial Terms Counsel.**
- Proposals, quotes, SOWs and invoices state the scope, price, payment terms,
  timeline, what's excluded, revisions, and refunds.
- No promises of specific results. Consumer rights are respected, for
  example the EU's 14-day withdrawal right for online consumer sales, and
  the terms say how it applies to digital services.
- Payment terms match Stripe's rules.
- No commitment is made for the owner without the owner's OK.
- Anything a client asks the owner to sign is `needs_attorney`.

## Honest limits

- Laws change. When a check depends on a rule that may have changed recently,
  the counsel checks it with WebSearch against an official source (the FTC,
  the SEC, a regulator's page, the platform's policy page) and cites it in the note.
- The Legal Desk lowers risk. It doesn't remove it, and it doesn't replace a
  real lawyer.
