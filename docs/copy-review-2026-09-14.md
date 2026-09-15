# Marketing copy review — September 14, 2026

Applied Corey Haines's `copywriting` (2.0.2), then `copy-editing` (2.0.0). This is public source documentation; the marketing build excludes it.

## Delivered copy and rationale

The final section copy is in index.html, vibe-code-to-production.html, about.html, contact.html, careers.html, portfolio.html, and civic.html.

- Homepage: kept the approved headline; aligned problem cards with websites, internal tools, and CRM costs. Added concrete examples without invented savings. Search and social descriptions now match the custom-software offer.
- Services: clarified the role of AI and human review; kept the full-width feature and published prices. Replaced the generic project timeline with scope-specific language.
- Production page: emphasized working directly with an engineer, usable handoff, and a clear inquiry response. Added a from-scratch FAQ so visitors from the custom-software service have an answer. Kept the user-written opening.
- About and Careers: removed repeated introductions and explained responsibility more directly.
- Contact: replaced the blanket repair timeline with scope and price agreed upfront; gave useful guidance for the initial message.
- Portfolio: replaced generic agency phrases with project descriptions; preserved sourced quotes and confirmed credits.
- Civic: tightened the engagement and inquiry copy; preserved project facts and commercial terms.
- Corrected inherited Twitter titles and descriptions on About, Careers, Portfolio, and the production page.

## Editing checks

Ran sequential passes for clarity, voice, customer benefit, evidence, specificity, emotional relevance, and friction at calls to action. No new statistics, testimonials, savings claims, guarantees, or project credits were added. Emotional relevance comes from recognizable work problems rather than fear or urgency.

A final editorial review used three perspectives (self-review, not independent reviewers): conversion copywriter 8/10, UX writer 8/10, skeptical business owner 8/10. Remaining limitation: this is an editorial assessment, not evidence of conversion uplift. Concrete cost savings would require actual customer results.

## Optional copy alternatives, not deployed

The approved homepage headline remains unchanged.

- Future service headline A: “Software built around your workflow.” Direct customer benefit.
- Future service headline B: “Custom tools for the way your team works.” Adds the team context.
- CTA A: “Tell us about your project.” Low-pressure inquiry.
- CTA B: “Discuss your workflow.” Appropriate for customers who have a business problem but no technical brief.

## Brand context

Saved the established audience, offer, voice, evidence rules, and user preferences in `.agents/product-marketing.md` for future copy passes.

## Technical SEO follow-up

Verified all eight canonical sitemap routes and robots.txt. Added complete social metadata, public social artwork, favicon, and a noindex 404 page. Root and nested missing URLs return 404 on production. The implementation follows [Cloudflare Pages serving behavior](https://developers.cloudflare.com/pages/configuration/serving-pages/). Run `python3 scripts/build-public.py` then `python3 scripts/check-public-seo.py` for future checks.
