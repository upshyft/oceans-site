# Search visibility and mobile performance

Checklist for future edits to this static site. These notes do not claim a ranking change. Production at https://www.theoceans.com stays on `main` until that branch is approved and deployed.

## Canonical host and paths

Live behavior checked on 2026-11-05:

- `http://` redirects to `https://`.
- `https://theoceans.com` 301s to `https://www.theoceans.com/`.
- `https://www.theoceans.com/contact`, `/contact.html`, and `/contact/` all return 200 with the same page. Render serves `contact.html` at those paths. The same is true for valuation, investor, loan-signing, and rate.

Use these canonical URLs in `<link rel="canonical">`, Open Graph `og:url`, internal links, `sitemap.xml`, and JSON-LD:

| File | Canonical |
| --- | --- |
| `index.html` | `https://www.theoceans.com/` |
| `contact.html` | `https://www.theoceans.com/contact` |
| `valuation.html` | `https://www.theoceans.com/valuation` |
| `investor.html` | `https://www.theoceans.com/investor` |
| `loan-signing.html` | `https://www.theoceans.com/loan-signing` |
| `rate.html` | `https://www.theoceans.com/rate` |
| `next-home.html` | `https://www.theoceans.com/next-home` |
| `move-plan.html` | `https://www.theoceans.com/move-plan` |
| `investment-plan.html` | `https://www.theoceans.com/investment-plan` |
| `how-we-sell.html` | `https://www.theoceans.com/how-we-sell` |
| `seller-prep.html` | `https://www.theoceans.com/seller-prep` |

Do not point canonicals at the apex domain. Do not add a `routes` block to `render.yaml`. A redirect from `/contact/` to `/contact` also matches `/contact` on this service and sends that URL to itself. Each page is one `.html` file. Do not commit a second extensionless copy, and do not add a `Content-Type` header for the clean path. Render already serves the `.html` file as HTML at the canonical URL, the `.html` URL, and the trailing-slash URL.

`first-home.html` is only a document that sends `/first-home`, `/first-home.html`, and `/first-home/` to `/next-home`. It is not a content page and it is not in the sitemap. The check still rejects every `routes` block, so this is not a Render service redirect.

## When a page changes

1. Keep one unique `<title>` and one unique meta description taken from copy already on the page. Do not invent prices, reviews, addresses, credentials, or testimonials.
2. Update that page's canonical, Open Graph tags, and `WebPage` JSON-LD so the URL matches the table above.
3. Update `sitemap.xml` `lastmod` for that URL to the date the visible content changed.
4. Add the new page to `sitemap.xml`, the footer links, and the header nav only if it is a real page with its own content. Do not add city landing pages that repeat the homepage.
5. Keep structured data as `RealEstateAgent` / `Organization` / `WebPage` / `Service`. Do not mark the site or the investor page as a `VacationRental`.
6. Use only facts already published on the site: Oceans Real Estate Group, eXp Realty of Greater Los Angeles, Inc., info@theoceans.com, 424-257-2021, Keston Abe DRE 02167533 (keston@theoceans.com), Tracey Takeshita DRE 02087436 (tracey@theoceans.com, and the loan-signing line 424-254-1010), based in Hermosa Beach, serving the six communities named in the footer. There is no street address on the site, so do not add one.
7. Leave FormSubmit (`https://formsubmit.app/f/q8vhg24vbb`), the `data-lead-form` values, and the Redfin stat hooks (`data-target`, source links, and the "updated …" line) in place.
8. Run `python3 scripts/check_seo.py`, `python3 scripts/check_clean_urls.py`, and `python3 scripts/check_guides.py`. Preview with `python3 scripts/preview.py` and click the mobile Menu, one form (do not submit a real lead), and the main links.

The homepage market counters include the published November 2026 figures in the HTML, so they stay visible when JavaScript is off. The count-up script still replaces those figures while it animates. Guide pages are one `.html` file each and are linked from the Guides menu and the footer. `styles/site.css` is the shared chrome for those pages; the original six pages keep their inline styles. Do not add extensionless copies of the new pages.

## Images

- Logos and headshots are files under `images/`, not data URIs in the HTML.
- The homepage phone hero is `images/hero-manhattan-pier-mobile.jpg`, used below 760px. The desktop hero file was left as-is.
- New image filenames are not content-hashed. `render.yaml` sets a 7-day browser cache for `/images/*` after deploy. Render still replaces the CDN copy on each deploy.

## What this pass measured locally

Lab only, on this machine's Chrome Lighthouse mobile run against `http://127.0.0.1:8765/`. Same command before and after. Not field data from www.theoceans.com, and not a ranking result.

| | Before | After |
| --- | --- | --- |
| Homepage HTML | 341,279 bytes | 43,859 bytes |
| Phone hero JPEG | 834,041 bytes (1100×1774) | 553,548 bytes (900×1451) |
| Lighthouse performance | 0.65 | 0.85 |
| Lighthouse SEO | 0.91 | 1.00 |
| Lighthouse accessibility | 0.89 | 0.96 |
| FCP | 4.2 s | 1.7 s |
| LCP | 7.7 s | 4.3 s |
| CLS | 0 | 0 |
| Total byte weight | 1,236 KiB | 695 KiB |

The phone hero was resized to 900 pixels wide and saved at JPEG quality 90. Structural similarity versus a lossless resize to that same size was 0.971. The desktop hero file was not recompressed. Lighthouse still estimates more savings on the phone hero; that was left in place so the photograph stays close to the original.

Gold labels (`#b59863`) and muted text (`#6d7a87`) still fail WCAG AA contrast on the cream background. Recoloring them would change the brand, so this pass did not.

Re-run Lighthouse the same way after later performance edits and record the new numbers here.
