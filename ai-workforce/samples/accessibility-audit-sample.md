# Sample Website Accessibility Audit — Illustrative Store (sample deliverable, not a real client)

Prepared as a portfolio/sample piece for the `website-accessibility-remediation-small-ecommerce`
opportunity. Built by Full-Stack Dev Agent using the same axe-core-based WCAG 2.2 AA methodology
already used on Edgex's own site (`site/`, zero violations). No client site was scanned — every
finding below is a realistic, commonly-found issue on small e-commerce sites, illustrating the
report format a real client would receive.

**This is the sales format, and it is deliberate:** a concrete, itemized issue report with real
fixes — never an automated overlay, and never a claim of "ADA/WCAG compliant" or "certified." The
FTC's 2025 final order against accessiBe fined them $1M for exactly that claim, and UsableNet found
overlay widgets don't reduce lawsuit exposure. Edgex sells fixes and documentation, not a badge.

## Findings

| # | Issue | WCAG 2.2 criterion | Real-world impact | Concrete fix |
|---|---|---|---|---|
| 1 | 24 product images with no `alt` text | 1.1.1 Non-text Content (A) | Screen-reader users hear "image, image, image" with no idea what's for sale | Write one real, specific alt attribute per product image (e.g. `alt="Navy blue canvas tote bag, front view"`) |
| 2 | "Add to Cart" button: white text on light-green background | 1.4.3 Contrast (Minimum) (AA) | Low-vision users can't read the button text; measured contrast ratio 2.1:1, needs 4.5:1 | Darken the button background or use a darker text color to reach at least 4.5:1 |
| 3 | Checkout email/phone fields use placeholder text only, no `<label>` | 1.1.1 / 4.1.2 Name, Role, Value (A) | Screen readers announce the field as unlabeled once text is typed and the placeholder disappears | Add a real `<label for="...">` tied to each input; placeholder text can stay as a hint, not a replacement |
| 4 | Homepage heading order jumps from `<h1>` to `<h3>`, skipping `<h2>` | 1.3.1 Info and Relationships (A) | Screen-reader users navigating by heading level lose the page's structure | Correct the heading hierarchy so levels aren't skipped |
| 5 | No visible focus indicator on top navigation links | 2.4.7 Focus Visible (AA) | Keyboard-only users can't tell which link is focused while tabbing through the nav | Restore or add a visible `:focus` outline instead of suppressing the browser default |
| 6 | Product demo video has no captions | 1.2.2 Captions (Prerecorded) (A) | Deaf/hard-of-hearing users and anyone browsing with sound off miss the video's content entirely | Add a caption track (SRT/VTT) synced to the video |

## Delivery format

- One PDF/document per client: this table, plus a short intro (why it matters, the real legal
  context — 4,928 US web accessibility lawsuits in 2025, 70% against e-commerce, UsableNet) and a
  closing note on scope (what was checked, what wasn't).
- Priced from the opportunity's own real research: $1,500–$3,500 for a small-business audit + fix
  pass (a11yproof.com, 2026); larger 10–50 page sites run $5,000–$25,000 plus a $2,000–$5,000/yr
  monitoring retainer (connectmediaagency.com, 2026).
- Sold alongside the cart-recovery opportunity where relevant — same DTC/Shopify buyer, two
  different real problems.

## Status

Sample only. First real sale path is a Fiverr gig (once the owner's Fiverr account exists,
`owner_actions/fiverr-account`) or an inbound inquiry — cold outreach stays paused pending a new
posture from Dispatch/Chief of Staff (`decisions/2026-09-25-pilot-pivot-resolved-dropped`).
