"""Write storefront/gumroad/PACKAGE.md from the Last-Touch-cleared Etsy package.

The product copy is the same text Last Touch cleared for Etsy, with the Etsy-only
lines swapped for Gumroad ones. Run from anywhere: python3 make_package.py
"""
import os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
etsy = open(os.path.join(ROOT, 'etsy', 'PACKAGE.md')).read()
CONTACT = 'ai--edgex@edgex--ai.com'

P = [  # n, folder, name, slug, price, summary, details, files
 (1, '01-freelancer-income-tax-tracker', 'Freelancer Income & Tax Tracker (Excel + Google Sheets)', 'freelancer-tax-tracker', 9.50,
  'Log income and expenses; it works out your tax set-aside for you.',
  [('Format', 'Excel (.xlsx) + quick-start PDF'), ('Works with', 'Microsoft Excel, Google Sheets'), ('Tabs', '8')],
  'Freelancer-Income-Tax-Tracker.xlsx, Freelancer-Income-Tax-Tracker_Quick-Start-Guide.pdf'),
 (2, '02-wedding-budget-planner', 'Wedding Budget Planner (Excel + Google Sheets)', 'wedding-budget-planner', 8.50,
  'Budget, payments, guests and to-dos in one calm place.',
  [('Format', 'Excel (.xlsx) + quick-start PDF'), ('Works with', 'Microsoft Excel, Google Sheets')],
  'Wedding-Budget-Planner.xlsx, Wedding-Budget-Planner_Quick-Start-Guide.pdf'),
 (3, '03-debt-payoff-planner', 'Debt Payoff Planner: Snowball vs Avalanche (Excel + Google Sheets)', 'debt-payoff-planner', 7.50,
  'Type your debts once and compare snowball, avalanche and minimums.',
  [('Format', 'Excel (.xlsx) + quick-start PDF'), ('Works with', 'Microsoft Excel, Google Sheets')],
  'Debt-Payoff-Planner.xlsx, Debt-Payoff-Planner_Quick-Start-Guide.pdf'),
 (4, '04-home-maintenance-planner', 'Home Maintenance Planner (Printable PDF)', 'home-maintenance-planner', 6.50,
  'Seasonal checklists, a year at a glance and repair logs for your home.',
  [('Format', 'PDF, US Letter + A4'), ('Use', 'Print at home or use in a PDF note app')],
  'Home-Maintenance-Planner_US-Letter.pdf, Home-Maintenance-Planner_A4.pdf'),
 (5, '05-pet-care-record', 'Pet Care & Health Record (Printable PDF)', 'pet-care-record', 6.50,
  "Your pet's profile, vet visits, meds and vaccines, all on paper.",
  [('Format', 'PDF, US Letter + A4'), ('Use', 'Print at home or use in a PDF note app')],
  'Pet-Care-Health-Record_US-Letter.pdf, Pet-Care-Health-Record_A4.pdf'),
 (6, '06-moving-planner', 'Moving Planner (Printable PDF)', 'moving-planner', 5.50,
  'An 8-week countdown, moving-day checklist and box inventory.',
  [('Format', 'PDF, US Letter + A4'), ('Use', 'Print at home or use in a PDF note app')],
  'Moving-Planner_US-Letter.pdf, Moving-Planner_A4.pdf'),
]
BUNDLE = 24.00

def keep_direct(p): return p - (0.10 * p + 0.50) - (0.029 * p + 0.30)
def keep_discover(p): return 0.70 * p

desc = {}
for n, body in re.findall(r'\n### Listing (\d): .*?\n(.*?)(?=\n### Listing |\n## Part 3)', etsy, re.S):
    d = re.search(r'\*\*Description:\*\*\n```\n(.*?)```', body, re.S).group(1)
    d = d.replace('1. Download from You > Purchases after checkout.',
                  '1. After checkout, Gumroad emails you a link to your files, and they stay in your Gumroad Library.')
    d = d.replace('Questions? Send us a message.', f'Questions? Email us at {CONTACT}.')
    assert 'Etsy' not in d and 'Purchases' not in d, n
    desc[int(n)] = d

L = []
w = L.append
w('# Edgex on Gumroad: paste-ready package\n')
w('Prepared 2026-10-03 by the Edgex crew from the six products in `storefront/etsy/` (the same files and the same Last-Touch-cleared copy, adapted for Gumroad). Nothing has been listed; you create the account and paste.\n')
w('## What it costs\n')
w('- **To open and keep a store: $0.** No monthly fee and no listing fee ([Gumroad pricing](https://gumroad.com/pricing)).')
w('- **Per sale through your own link or profile:** Gumroad keeps 10% + $0.50. Card processing comes on top, about 2.9% + $0.30 for a US card ([Gumroad fees](https://gumroad.com/help/article/66-gumroads-fees), [breakdown](https://checkoutpage.com/blog/gumroad-fees)).')
w("- **Per sale that Gumroad's Discover marketplace brings you:** 30% flat, processing included.")
w('- **Sales tax and VAT:** Gumroad is the merchant of record, so it collects and pays them for you ([sales tax on Gumroad](https://gumroad.com/help/article/121-sales-tax-on-gumroad)).')
w("- **Refunds:** Gumroad doesn't give its fee back when you refund a sale (reported by [Checkout Page](https://checkoutpage.com/blog/gumroad-fees)).")
w('- **Getting paid:** you pick daily, weekly, monthly or quarterly payouts to a bank account or PayPal. Each sale is held for at least 7 days first. Guides report a $10 minimum for verified accounts and $100 for unverified ones ([getting paid](https://gumroad.com/help/article/13-getting-paid), [payout guide](https://roo.beehiiv.com/p/gumroad-fees-2026)). Your payout settings show the real number.\n')
w("Gumroad's own pages are blocked from our environment, so the figures above come from search results quoting them. Check the pricing page once when you sign up.\n")
w('### What you keep per sale (suggested prices)\n')
w('| # | Product | Suggested price | Keep, direct sale | Keep, Discover sale |')
w('|---|---|---|---|---|')
for n, f, name, slug, price, *_ in P:
    w(f'| {n} | {name.split(" (")[0]} | ${price:.2f} | ${keep_direct(price):.2f} | ${keep_discover(price):.2f} |')
w(f'| B | Life Admin Bundle (all 6) | ${BUNDLE:.2f} | ${keep_direct(BUNDLE):.2f} | ${keep_discover(BUNDLE):.2f} |\n')
w("These are the same prices as the Etsy package, so a buyer sees the same price on both. The flat $0.50 fee takes a bigger share of cheap items, which is why there's a bundle. Its $24 is $20 off the $44 for all six bought separately. You set the final prices.\n")
w('---\n')
w('## Part 1. Open the store (about 10 minutes, only you can do this)\n')
w('1. **Sign up** at gumroad.com with the email you want buyers\' receipts and payouts tied to. The studio mailbox works: ' + CONTACT + '.')
w('2. **Username:** this becomes your store address, `username.gumroad.com`. Try in this order: `edgexstudio`, `edgextemplates`, `edgexplanners`.')
w('3. **Profile:** set the name to **Edgex**. Add no personal name or photo. Use the bundle cover as the profile banner if you like. Bio:')
w('```\nPractical templates for money, home and life\'s big moments: spreadsheets that do the math for you and printable planners that keep the important stuff in one place. Made by a small studio with the help of AI tools, and tested before release.\n```')
w("4. **Payouts:** add a bank account or PayPal, and the tax details Gumroad asks for. These must be your real details. Gumroad keeps them private and doesn't show them to buyers. Turn on two-factor sign-in.")
w('5. **Support email:** if Gumroad asks for one, use ' + CONTACT + '. It matches the "Questions?" line in every description.\n')
w('---\n')
w('## Part 2. Add each product (Products > New product > Digital product)\n')
w('Same steps every time:\n')
w('1. **Name** and **price:** paste from the product below.')
w('2. **Description:** paste the block. **URL:** set the custom slug shown.')
w('3. **Cover:** upload `images/<folder>_cover.png` (1280 x 720, Gumroad\'s recommended size). You can add the four extra images from `storefront/etsy/<folder>/images/` (02 to 05) as more covers.')
w('4. **Thumbnail:** upload `images/<folder>_thumb.png` (600 x 600).')
w('5. **Summary** and **Additional details** (in the product info box): paste from below.')
w('6. **Content:** upload the files listed, from `storefront/etsy/<folder>/`.')
w("7. **Refund policy:** if the product form offers one, choose the option closest to \"refund or fix if a file is faulty\" and paste the note from Part 3. Don't promise no refunds at all; EU and UK buyers keep their legal rights.")
w('8. **Publish.**\n')
w('**Spreadsheets (1 to 3):** do the Google Sheets check from the Etsy package first (open each .xlsx in Sheets and enter one test row). Both listings promise the files work in Sheets, and nobody has opened them in Sheets yet.\n')
for n, f, name, slug, price, summary, details, files in P:
    w(f'### Product {n}: {name}\n')
    w(f'**Price:** ${price:.2f}  |  **URL:** `{slug}`  |  **Files:** {files}  |  **Images:** `images/{f}_cover.png`, `images/{f}_thumb.png`\n')
    w('**Summary:**\n```\n' + summary + '\n```')
    w('**Additional details:**\n```\n' + '\n'.join(f'{k}: {v}' for k, v in details) + '\n```')
    w('**Description:**\n```\n' + desc[n] + '```\n')
w('### Bundle: Life Admin Bundle (Products > New product > Bundle)\n')
w(f'Create this after the six products exist, then select all six. **Price:** ${BUNDLE:.2f}  |  **URL:** `life-admin-bundle`  |  **Images:** `images/00-bundle_cover.png`, `images/00-bundle_thumb.png` ([bundles](https://help.gumroad.com/article/339-product-bundles))\n')
w('**Name:**\n```\nLife Admin Bundle: 3 Spreadsheets + 3 Printable Planners\n```')
w('**Summary:**\n```\nAll six Edgex templates in one purchase: $20 less than buying them one by one.\n```')
w('**Description:**\n```\nMade with AI assistance: these templates were designed and built by our studio with the help of AI tools, and every spreadsheet formula was tested with sample data before release.\n\nEverything for the money, home and life admin in one download.\n\nINSTANT DIGITAL DOWNLOAD. Nothing will be shipped.\n\nSPREADSHEETS (Excel + Google Sheets)\n- Freelancer Income & Tax Tracker: log income and expenses, and it works out your tax set-aside\n- Wedding Budget Planner: budget, payments, guest list with RSVPs, and a checklist\n- Debt Payoff Planner: compare snowball, avalanche and minimum payments\n\nPRINTABLE PLANNERS (PDF, US Letter + A4)\n- Home Maintenance Planner: seasonal checklists, year at a glance, repair logs\n- Pet Care & Health Record: profile, vet visits, meds and vaccines\n- Moving Planner: 8-week countdown, moving-day checklist, box inventory\n\nGOOD TO KNOW\n- Spreadsheets need Microsoft Excel or Google Sheets. Software not included.\n- The tax tracker helps you save for tax. It is not tax advice and does not calculate the tax you owe.\n- For personal use. Please don\'t share or resell the files.\n\nQuestions? Email us at ' + CONTACT + '.\n```\n')
w('---\n')
w('## Part 3. Refund note (paste where Gumroad asks, or in each description\'s footer if it doesn\'t)\n')
w("```\nBecause files can't be returned once downloaded, we don't offer refunds for change of mind. If a file won't open, is damaged, or isn't what the description said, email us and we will fix it, replace it, or refund you. Buyers in the EU and UK keep their statutory rights.\n```\n")
w('## Part 4. After launch\n')
w("- Share the Gumroad links (for example `username.gumroad.com/l/life-admin-bundle`) on your own channels only. Don't put them in Etsy listings or Etsy messages: Etsy's seller policy doesn't allow steering Etsy buyers to buy elsewhere.")
w("- Tell the crew your store URL. We'll add it to the office DB so the agents can track sales you report. Agents don't log in to Gumroad.")
w('- Each new template the studio builds can go up here the same day it\'s cleared.\n')
w('## Files\n```\nstorefront/gumroad/\n  PACKAGE.md         this guide\n  images/            00-bundle_cover/_thumb + <folder>_cover (1280x720) and <folder>_thumb (600x600) for all six\n  _build/            make_gumroad_images.py (images from the Etsy heroes), make_package.py (this file)\n```')
open(os.path.join(ROOT, 'gumroad', 'PACKAGE.md'), 'w').write('\n'.join(L) + '\n')
print('ok', len('\n'.join(L)))
