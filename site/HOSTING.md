# Publishing the Edgex site

The site is plain HTML and CSS (no build step, no JavaScript, no server).
Any static host works. Three free options are below. They all do the job;
the choice is yours.

## Step 0 (every option): make the public copy

`site/` contains files that must **not** go on the public web:

- `products/_deliverables/`: the paid setup guide (PDF + Markdown). If it
  is published, anyone can download it for free.
- `_preview/`: review screenshots.
- `HOSTING.md` and `make-public-copy.sh`: internal notes.

Run this from the repo root:

```bash
bash site/make-public-copy.sh
```

It creates `site-public/` next to `site/` with only the 7 public files
(4 pages, a 404 page, the stylesheet and the icon) and refuses to finish if
the guide slipped in. **Publish `site-public/`, never `site/`.**

Also: **don't make the `edgex-relay` repo public.** It holds the studio's
internal operating docs and unrelated code. If you use GitHub, put the
site in a new, separate repo.

## Option A: GitHub Pages

- **Cost:** free for a **public** repository on a free GitHub account.
  Publishing from a **private** repo needs a paid plan (GitHub Pro, about
  $4/month, or a Team/Enterprise plan).
- **Limits:** fine for this site (1 GB site size, soft limit of about
  100 GB bandwidth a month).
- **Note:** the repo's contents are public. That's fine for `site-public/`
  (it's the same as the website) but is why the paid guide must not be in it.

Steps:

1. Run Step 0.
2. On github.com, click **New repository**. Name it, for example,
   `edgex-site`. Choose **Public** (or Private if on a paid plan). Create it.
3. Upload the **contents** of `site-public/` (not the folder itself) with
   **Add file → Upload files**, keeping the `assets/` and `products/`
   folders. Commit.
4. Go to **Settings → Pages**. Under **Build and deployment**, choose
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
5. After a minute or two the site is live at
   `https://<your-username>.github.io/edgex-site/`.
6. Custom domain (optional): in **Settings → Pages → Custom domain**, enter
   the domain, then add the DNS records GitHub shows you at your domain
   registrar. Tick **Enforce HTTPS** once it becomes available.

## Option B: Cloudflare Pages

- **Cost:** free plan. No bandwidth limit on static files; 500 builds a
  month and 20,000 files per site (this site uses 7).
- **Works with a private GitHub repo** or with no repo at all (drag and drop).

Steps (drag and drop, no Git needed):

1. Run Step 0.
2. Create a free account at dash.cloudflare.com.
3. Go to **Workers & Pages → Create → Pages → Upload assets** (Cloudflare
   calls this "Direct Upload").
4. Name the project (for example `edgex`), then drag the `site-public`
   folder (or a zip of it) into the upload box. Deploy.
5. The site is live at `https://<project-name>.pages.dev`.
6. To update later: open the project and choose **Create new deployment**,
   then upload the new `site-public` folder.
7. Custom domain (optional): in the project, **Custom domains → Set up a
   custom domain**. If the domain's DNS is on Cloudflare this is automatic;
   otherwise add the CNAME record it shows at your registrar.

## Option C: Netlify

- **Cost:** free plan with 300 credits a month (hard cap: no surprise
  bills, but if credits run out the site is paused until the next month).
  Roughly, a deploy costs 15 credits and bandwidth costs 20 credits per GB,
  so a small site with a handful of updates a month fits comfortably.
- **Works with** drag and drop or a private GitHub repo.

Steps (drag and drop):

1. Run Step 0.
2. Create a free account at app.netlify.com.
3. Go to **Sites → Add new site → Deploy manually** and drag the
   `site-public` folder in.
4. The site is live at `https://<random-name>.netlify.app`. Rename it under
   **Site configuration → Change site name**.
5. To update: open the site's **Deploys** tab and drag the new
   `site-public` folder in again.
6. Custom domain (optional): **Domain management → Add a domain**, then
   follow the DNS instructions.

## Custom domain: what it costs

A domain is optional; every option above gives a free address. A `.com`
costs roughly **$10.50 to $11 a year** at registrars that sell near cost
(Cloudflare Registrar, Porkbun). Some registrars advertise a cheaper first
year and then renew at $18 or more, so compare the **renewal** price, not
the first-year price. The wholesale price of `.com` is scheduled to rise
to $10.97 on 1 November 2026, so expect prices a little above $11 after
that. Other endings (`.co`, `.io`, `.ai`) cost more, often much more.

The contact email uses `edgex--ai.com`. If the owner already controls that
domain, the site can be pointed at it (or at a subdomain like
`www.edgex--ai.com`) at no extra cost. **Don't change or delete the
domain's existing MX records** when adding website records, or the email
address stops working.

Any purchase (domain or paid GitHub plan) goes through the weekly budget
process in `ai-workforce/OPERATIONS.md`; agents can't buy it.

## Before going live: owner checklist

- [ ] Chief of Staff approval to publish (the site is public, client-facing
      copy).
- [ ] Price for the setup guide set from real research, then a Stripe
      Payment Link created and swapped in for the placeholder in
      `site/products/index.html` (search for `PLACEHOLDER`).
- [ ] Decide how buyers receive the PDF. The simplest options: Stripe's
      "after payment" confirmation page shows a download link (note: that
      link then works for anyone who has it), or send the PDF by email
      after each sale, or sell through Gumroad/Lemon Squeezy, which handle
      delivery. Don't put the PDF inside `site-public/`.
- [ ] One real end-to-end test of the guide on live Twilio + Make.com
      accounts before the first sale (it has not been run against live
      accounts yet).
- [ ] Once the final address is known: add a `sitemap.xml` and canonical
      links, and submit the site in Google Search Console (free).
- [ ] Confirm `ai--edgex@edgex--ai.com` receives mail.
