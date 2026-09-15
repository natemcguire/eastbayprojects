# East Bay Projects — Current Status

Last updated: September 15, 2026

## Source of truth

- Repository: `git@github.com:natemcguire/eastbayprojects.git`
- Branch: `main`
- `origin/main` is the sole canonical code state.
- `nates-mac-mini` is the canonical development and runtime host, not the canonical Git history.
- Only cloud-safe source and documentation belong in GitHub. Approval records, browser sessions,
  generated drafts, credentials, contact data, logs, and queue state remain private on the mini.
- Current deployment source: `4609df4` (privacy notice and McGuire LLC legal identity)
- Production: `https://eastbayprojects.com`
- Cloudflare Pages project: `eastbayprojects`
- Latest deployment URL: `https://61b33161.eastbayprojects-1vq.pages.dev`
- Google Ads tag `AW-18335868802` is installed immediately after `<head>` on every public HTML page.
- Production routes were verified after the September 13 deployment.

After the July 20 handoff, development should continue from the Mac mini checkout at
`~/Projects/eastbayprojects`. Do not treat the laptop checkout as the active development
workspace unless a new handoff explicitly reverses this decision.

## Active test revision (September 11, 2026)

- User superseded the content changes: the active test must use the live site's exact text and structure, with styling changes only and no campaign hero feature.
- `scripts/build-restyle.py` copies the five live marketing pages and applies `design-lab/restyle/style.css`. It asserts exact visible-text equality on every page.
- The latest style uses oversized condensed typography, warm white, charcoal, and vermilion accents. Preview builds omit analytics and neutralize form submission; no production source is modified.
- Previous content explorations remain in `design-lab/current/` but are not part of this build.
- Local desktop/mobile review, navigation and asset checks passed. Deployed to `https://4b150e4f.eastbayprojects-designs.pages.dev` from `42f5e87`; production deployment ID verified unchanged.

## Design exploration (September 11, 2026)

- Nate requested ten distinct design directions, following the Seamaphore review approach,
  on a separate test site. Production is not being redesigned or deployed in this change.
- Test project: `eastbayprojects-designs`, URL `https://eastbayprojects-designs.pages.dev`.
- Initial exploration source: `2325d7a`; deployment `https://8245e059.eastbayprojects-designs.pages.dev`.
- Public source: `design-lab/`; build with `python3 scripts/build-design-lab.py`.
- The generated `design-dist/` contains only the prototypes and public portfolio/team assets.
  Run the deploy command from `design-lab/`, with explicit project name `eastbayprojects-designs`.
- The gallery offers ten complete homepage directions, local shortlisting, and side-by-side
  comparison at desktop and phone widths. Editorial also includes work, civic, and contact pages.
- The positioning study pairs a business/product partner with a senior engineer. Shared offers
  focus on reaching people, improving workflows, and launching products or public initiatives.
  Civic projects share the main portfolio with commercial work; Seamaphore and Nate’s Software
  are included as public examples. Copy remains exploratory.
- Prototype forms stay in the browser. No advertising tags, production Functions, database
  bindings, or private runtime state are included. Indexing is disabled.
- Verification: all ten deployed routes load in the browser; no missing gallery images. Desktop
  (1440px), phone (390px), and narrow gallery/comparison (320px) checks passed. Shortlisting,
  comparison selectors, portfolio filters, interactive heroes, and both preview forms were checked.
  The deployed response includes `X-Robots-Tag: noindex, nofollow`.
- Production baseline remains deployment `ebee08a6-5604-49e9-aa83-413cda292621` at source `8a88235`,
  verified unchanged after the test deployment.

## Live site

- `/` — primary commercial site
- `/contact` — lead form and Google Ads landing page
- The founder bio now links to `natemcguire.com` and identifies Mayven Studios, selected major
  clients, and its acquisition by the holding company founded by Uber's first employee and CEO.
- Performance claims are framed as measured and reported outcomes, not an absolute score guarantee.
- `/portfolio.html` — selected work
- `/civic.html` — civic and campaign work
- `/privacy.html` — privacy notice
- Contact form submissions are stored in the Cloudflare D1 database bound as `LEADS_DB`.

## Google Workspace email and outbound drafts

- Google Workspace now handles mail for `eastbayprojects.com`.
- The primary branded sender is `nate@eastbayprojects.com`; `contact@eastbayprojects.com` is an
  alias on the same mailbox.
- Cloudflare Email Routing is disabled so it does not conflict with Google Workspace delivery.
- The live DNS baseline includes Google MX, SPF, 2048-bit DKIM with selector `google`, and a
  monitoring-only DMARC policy (`p=none`).
- Inbound and outbound delivery tests passed. A post-setup authentication test returned SPF,
  DKIM, and DMARC `pass` for `eastbayprojects.com`.
- The 400 active East Bay Projects drafts from the personal Gmail account were captured to
  private Mac mini storage, recreated in the branded mailbox, and verified one-to-one by subject,
  recipients, body, and sender.
- The 400 verified source drafts were moved to Trash in the personal account and remain
  recoverable there for 30 days. Their private capture and verification manifests are not stored
  in Git.
- The Google Workspace MCP connection is authorized for both the personal and branded accounts;
  its credentials remain private on the Mac mini.
- A persistent Gmail API sender now runs from the Mac mini through LaunchAgent
  `com.eastbayprojects.outbound-sender`; the Air and Apple Mail are not part of delivery.
- The private queue contains 398 unique recipient-ready drafts and skips the two drafts without
  recipients. Its proposed weekday ramp is 10, 15, and 20 messages on July 27–29, then up to 25
  per weekday through August 19, between 9:30 a.m. and 3:30 p.m. Eastern.
- All 398 sendable drafts include the verified commercial-message disclosure, reply-based opt-out,
  list-unsubscribe header, and business postal address supplied by Nate. Sender and recipient
  fields were also verified across the full queue.
- The outbound queue is active with 398 pending messages and zero campaign sends at activation.
  The first message is scheduled for July 27 at 9:51 a.m. Eastern.
- The sender retries transient failures without duplicating sends, supports a private suppression
  list, and auto-pauses on an excessive bounce rate or a stale backlog.

### Outbound email next steps

1. Review the two unfinished drafts that do not yet have recipients.
2. Monitor the active Mac mini queue, replies, bounces, spam placement, and domain reputation
   before increasing volume.
3. Review DMARC reports and move from monitoring to an enforcement policy only after legitimate
   senders are confirmed.

## Google Ads status

- The first campaign has been configured around government and defense contractor website work.
- Target geography: Washington, DC; Northern Virginia; and Montgomery County, Maryland.
- Daily budget: `$25.00`.
- Final URL: `https://eastbayprojects.com/contact`.
- The campaign uses East Bay Projects branding, four sitelinks, two custom image ratios, and a
  `Get quote` call to action.
- Google asset text/URL/image/video expansion was turned off during setup.
- The Google Ads UI reported that the ads will go live after review.
- A Google Ads promotional link was inspected. It contained an account-specific tracking token,
  not a readable coupon code. Nothing was manually redeemed from that inspection.

## Positioning boundary

- `eastbayprojects.com`: purchasable websites and digital systems for specific business buyers.
- `natemcguire.com`: fractional CTO, architecture, engineering productivity, technical due
  diligence, and other high-value advisory engagements.
- Do not mix Nate McGuire advisory keywords into East Bay Projects ad groups.

## Ad approval system — requested product

Host a private review and approval application on the Mac mini. It must be reachable only over
Tailscale and should remain available when the laptop is offline.

### Review surfaces

1. **Display ads**
   - Show generated assets by campaign, region, aspect ratio, and status.
   - Provide large previews plus useful metadata.
   - Put an approve checkmark and reject X in the upper-right review controls.
2. **Text ads**
   - Show a clean selectable table of ad variants on the left.
   - Show the selected ad in a realistic Google Search context preview on the right.
   - Put the same approve/reject controls in the upper-right.

### Workflow

- Suggested lifecycle: `draft -> pending_review -> approved|rejected -> queued -> syncing -> synced|failed`.
- Every approval/rejection must be timestamped and auditable.
- Approved items enter a Google Ads update queue; rejected items remain available for revision.
- The Google Ads worker must be idempotent and must never publish an unapproved asset.
- Keep account IDs, API credentials, browser profiles, and ntfy secrets outside Git.
- Use ntfy to send concise review notifications whose link opens the Tailscale-only review page.
- Prefer `tailscale serve` in front of an application bound to loopback instead of exposing a
  public listener.

## Display-ad creative queue

Create coherent East Bay Projects campaign families rather than generic stock imagery:

- Made in USA badge/credibility asset
- Northern Virginia
- Virginia
- Washington, DC
- Texas
- Bay Area / San Francisco
- Government contractor / federal buyer credibility
- Defense contractor recruiting and teaming
- Senior-led delivery / no agency layers
- Website modernization / credibility before the bid

Required Google Ads shapes should include horizontal, square, and vertical 4:5 variants. Avoid
fake interface text, generic AI office scenes, compliance claims, and unrelated stock imagery.

## Immediate next steps on the Mac mini

1. Review the remaining display assets through the Tailscale-only interface.
2. Approve or reject the campaign geography, daily budget, and paused/active launch choice.
3. Build a separate dry-run Google Ads worker with idempotency and account-target validation.
4. Require explicit authorization before the first Google Ads mutation; keep the proposed Search
   campaign PAUSED.

## Operational safety

- Do not launch new spend, raise budgets, or broaden targeting without explicit approval.
- Do not auto-approve generated copy or images.
- Do not claim that a public marketing site is CMMC- or HIPAA-compliant.
- Keep the review application private to Tailscale and do not publish it to Cloudflare Pages.

## Private ad review foundation

- A loopback-only review service now lives under `ad_review/` and runs on the Mac mini at
  `http://127.0.0.1:8765`.
- The display page shows regional creative previews; the text page provides a selectable list and
  a Google Search-style context preview. Both have approve/reject controls in the upper-right.
- The campaign page ties review to the exact private plan digest and requires explicit geography,
  daily budget, and paused/active launch approval. Defaults are DMV, $15/day, and create paused.
- SQLite records ads, audit events, and idempotent sync jobs. A database trigger prevents
  unapproved ads from entering the sync queue.
- Private state defaults to `~/.local/share/eastbayprojects/ad-review/`; it is not stored in Git.
- The importer accepts private JSON arrays with stable IDs and skips existing records.
- Tailscale Serve proxies port 8765 at the configured tailnet-only URL; Funnel is prohibited.
- ntfy is configured privately and its review notification/link flow has been tested.
- The Google Ads sync worker is intentionally not implemented, and no approved item has been
  synchronized to the live account.

### Infrastructure checkpoint (July 27, 2026)

- Colima now runs under the user LaunchAgent `homebrew.mxcl.colima` with `RunAtLoad` and
  `KeepAlive`; it is no longer dependent on a manually started terminal session.
- The ntfy container retains `unless-stopped`, publishes host port `8082`, and recovered with the
  other Colima containers during a controlled VM restart. Localhost and Tailscale health checks
  passed on `8082`; nothing is listening on the retired `8081` port.

### Runtime checkpoint (July 20, 2026)

- LaunchAgent `com.eastbayprojects.ad-review` is running successfully on loopback port 8765.
- Tailscale Serve is active at the configured tailnet-only URL. The hostname remains private
  operational configuration.
- The private queue contains 12 text variants, 15 original display assets, and 15 branded display
  assets. At this checkpoint, 11 items are approved and 2 are rejected; the rest await review.
- ntfy is configured and tested without committing its topic, token, or private review URL.
- Google Ads customer, campaign, and asset-group IDs live only in private SQLite settings.
- The deterministic plan currently contains 10 approved text RSAs across four PAUSED Search ad
  groups and 1 approved display asset for the configured Performance Max asset group.
- Campaign-level review is pending with safe defaults: DMV geography, $15 daily budget, and
  create paused.
- Actual Google Ads synchronization has not run and remains a separate, explicitly authorized step.

### Local engagement proposal revision (September 11, 2026)

- Completed the private, neutral `output/pdf/growth-partnership-pitch.pdf`: seven-page engagement pitch followed by evidence, scenario analysis, and the prior technical appendix.
- The PDF and supporting source remain ignored and local-only. No private research or customer evidence was added to Git.
- Rendered and reviewed the new pages and checked scenario arithmetic. No production or test deployment changed.

### Engagement model and styled proposals (September 11, 2026)

- Added the bounded fit review to the test homepage, clarified the agreement-before-build model, and retained integrated civic work and the existing design language.
- Added a public-source Sea Trek opportunity study in place of Straus on the study index, and expanded the Kingstowne renewal explanation. No private customer evidence is in the site.
- Completed two eight-page, print-friendly local proposal PDFs in `output/pdf/`; artifacts and editable builders remain ignored and local-only.
- Checked PDF page layouts, local website links, desktop layout, and mobile navigation. Deployed to `https://b8ea5886.eastbayprojects-designs.pages.dev` (source `18703f6`). Production deployment ID is unchanged; direct scripted HTTP verification received a 403, so the deployed pages were checked in the browser.

### Second exact-content style (September 11, 2026)

- Reworked typography, color, service grids, and buttons while preserving all five live pages verbatim. No campaign imagery added to the homepage.
- Previous ivory/green preview remains available at `https://4b150e4f.eastbayprojects-designs.pages.dev`. Latest preview: `https://64dc9423.eastbayprojects-designs.pages.dev` from `38f23ff`. Desktop/mobile checks passed; production deployment unchanged.

### Civic navigation and design alignment (September 13, 2026)

- Removed Civic from desktop and mobile primary navigation on the homepage, portfolio, contact, and Civic pages; added Civic & Campaigns to their footers.
- Civic now uses the production homepage's palette, blueprint hero, typography, buttons, fixed header, responsive menu, and footer. Existing Civic content and project links are preserved.
- Desktop and 390px phone checks passed, including menu toggle, work anchor, image loading, and overflow checks.
- Production release is staged from the existing live source `8a88235`, with this change's navigation patch and updated `civic.html`. This preserves the live homepage copy and contact behavior; later unreleased team/copy and conversion changes on main are not included.
- Deployed to `https://12667a46.eastbayprojects-1vq.pages.dev`. Verified the live `/civic` design and all four pages' footer navigation; Cloudflare applies its normal email-address obfuscation.

### Contact forms, site copy, and sitemap (September 13, 2026)

- Primary contact/project buttons now lead to the homepage form. `/contact` remains indexable and linked from the footer, with the homepage's design and mobile navigation.
- The homepage now submits to `/api/contact` and D1 instead of opening a mail draft. The handler supports JSON responses as well as the standalone form's existing redirect flow. Errors retain homepage form values for retry.
- Rewrote marketing copy across the homepage, portfolio, Civic, and contact pages to explain the services plainly and remove exaggerated promises. Added sitemap.xml, robots.txt, and matching canonical URLs.
- Updated AGENTS.md with design, navigation, copy, form verification, and isolated-browser requirements.
- Verification: isolated headless browser checks passed at 1440px and 390px; both forms saved local D1 records; homepage network failure/retry preserved entered values. Handler checks covered validation, timing, honeypot, JSON success/failure, and existing redirect behavior. Fixed pre-existing homepage grid overflow discovered during testing.
- Production staging uses current public marketing source/assets while retaining the live `8a88235` founder section and excluding the unpublished contact conversion-tag change. The separate team draft remains in repository source. Operational files and private state are excluded from deployment.
- Deployed to `https://740efb10.eastbayprojects-1vq.pages.dev`. Both live forms saved labeled test inquiries in production D1; the two test records were then removed. Sitemap, robots.txt, and all five canonical URLs were verified live.

### Google Search Console submission (September 13, 2026)

- Used the existing verified `sc-domain:eastbayprojects.com` property. Submitted `https://eastbayprojects.com/sitemap.xml`; Google reported Success and discovered all five pages.
- Requested homepage indexing; Google confirmed it was added to the priority crawl queue. The prior August 27 crawl had selected the www homepage as canonical; the newly deployed homepage declares the non-www canonical explicitly.
- Requested `/contact` indexing; Google also confirmed it was added to the priority crawl queue.
- Crawl requests are not confirmation that pages have been indexed.

### Approved design promotion (September 14, 2026)

- Nate approved the ivory/green preview at `4b150e4f.eastbayprojects-designs.pages.dev`. Its exact stylesheet is now shared by all five production pages.
- Retained the September 13 contact forms, footer navigation, plain copy, and SEO changes. The public builder preserves the published founder biography and analytics boundary.
- Added `scripts/build-public.py` to stage only marketing assets. Desktop and phone checks passed on all five routes with no overflow, missing images, or preview indexing restrictions.

### Vibe Code to Production landing page (September 14, 2026)

- Added `/vibe-code-to-production`: work directly with an East Bay Projects engineer to finish an existing app and deploy in client-controlled accounts. Adapted the supplied OWN copy to the existing brand and scoped engagement model.
- Uses the approved ivory/green design, an inquiry form with the service label, practical FAQs, and clear ownership, deployment, and handoff copy. Added homepage and footer links, contact service options, canonical/social metadata, and sitemap entry.
- Local verification passed at 1440, 390, and 320px: no overflow or JavaScript errors; menu, FAQ, CTA, failed-submission recovery, successful save, and reset checked. Confirmed service label and source URL in local D1. Existing homepage and contact form regression checks passed.
- Production design promotion completed at `https://0c86e761.eastbayprojects-1vq.pages.dev`; the public stylesheet hash matches the exact approved preview.

### Family business, careers, and landing page refinement (September 14, 2026)

- Removed founder photos and biographies from the homepage. Added `/about` for Nate and Josh, the family-led business, and its network of senior engineers across the U.S. and internationally. All primary About links now point there.
- Published `/careers` with the existing Forward-Deployed Engineer and Operations Expert roles plus Senior Backend Engineer, Senior DevOps Engineer, and Senior Product Engineer. Role links preselect the inquiry form, which saves through the existing D1 contact handler.
- Reworked `/vibe-code-to-production` around “We turn vibe-coded apps into production-quality software” and Nate’s opening about useful prototypes, enterprise tools, and not knowing what help is needed. Replaced the offset note layout with a full-width headline and three-stage overview.
- All eight public pages are included in the safe marketing build and sitemap. The builder no longer restores a founder section on the homepage.
- Local desktop, phone, and narrow-phone checks passed for the revised landing page, homepage, About, and Careers. Verified loaded portraits only on About, no overflow or JavaScript errors, and successful Careers inquiry storage.
- Earlier landing deployment `https://ee96eefc.eastbayprojects-1vq.pages.dev` passed live form failure/retry and storage checks. The single labeled live test record was verified and removed.

- Final deployment: `https://5223dd3b.eastbayprojects-1vq.pages.dev` from `cf70e7b`. After brief cache propagation, normal production URLs passed desktop/phone checks. Confirmed eight-page sitemap, homepage without portraits, and live Careers inquiry storage with correct role/source; removed the single synthetic application.

### Detailed senior role descriptions (September 14, 2026)

- Expanded all five Careers roles with ownership, relevant experience, delivery expectations, and role-specific work samples. Forward-Deployed Engineer includes direct customer discovery, implementation, integration, and launch responsibility.
- Added shared expectations for client judgment, dependable delivery, maintainable handoffs, and accountability for AI-assisted work. No unconfirmed compensation, benefits, or fixed experience thresholds were introduced.
- Added role jump links and retained application links that select the correct role in the existing inquiry form.

- Verified all five detailed descriptions on production at `https://e964fb77.eastbayprojects-1vq.pages.dev` (source `9973875`). Desktop and mobile layout and role-selection checks passed; form submission logic is unchanged.

### Editorial portfolio (September 14, 2026)

- Replaced text cards with full-width project features, paired image spreads, editorial captions, and the shared responsive navigation. The page keeps the ivory/green site identity while taking an image-led direction from Craig Fowler’s Howler portfolio.
- Added Droptics after Nate confirmed the collaboration with Craig; it opens the page with project artwork and explicitly credits Craig’s digital design/art direction. Added SailScan, Seamaphore, Recipeas, Nate’s Software, and Steven Brown’s campaign; retained the four existing projects. Prop Q is excluded.
- Added two short, sourced customer-review excerpts labeled “Former Customer,” explicitly identified as earlier Mayven engagements. Each links to its original review; provenance is recorded in `assets/portfolio/README.md`.
- Public project captures are optimized WebP files. Source credentials, profiles, and runtime state are excluded from the build.
- Desktop, phone, and narrow-phone checks passed: ten projects, all images decoded, source links, no overflow or JavaScript errors, and working mobile navigation. Homepage contact links and existing form handlers remain unchanged.

- Deployed the editorial portfolio to `https://1089716e.eastbayprojects-1vq.pages.dev` from `d8cf165`. Normal production URL confirms ten projects and Craig’s credit; live desktop/phone checks verified all imagery, navigation, and both review sources.

### Portfolio and biography corrections (September 14, 2026)

- Removed Austin’s Heating & AC after Nate identified it as an incorrect attribution, and removed his personal website from the portfolio.
- Kept the verified review excerpts and “Former Customer” labels; removed the review links and testimonial subheading at Nate’s request. Original provenance remains in local repository documentation.
- Limited public-site Mayven wording to one mention in Nate’s About biography: founder of award-winning engineering firm Mayven Studios. Removed it from Josh’s biography and recorded the copy rule in AGENTS.md.

- Nate also requested removal of Nate’s Software. The portfolio now contains seven projects; project numbering was updated.

- Replaced SailScan’s website preview with its published App Store results screen showing traced stripes and sail measurements. Updated portrait image layout and closed the grid gap left by removals.

- Corrections deployed to `https://88923df8.eastbayprojects-1vq.pages.dev` (source `f093d79`). Verified seven projects, the SailScan app image, removed entries/links/subheading, and one Mayven mention in Nate’s bio. Desktop and mobile layout checks passed.

## SailScan portfolio presentation — September 14, 2026

- Replaced the plain portrait screenshot with an ocean-blue, two-phone composition using the iOS marketing camera and results screens, with Droptics as the art-direction reference. Built-in image generation produced the device mockup; source roles and prompt are documented in `assets/portfolio/README.md`.
- The optimized 105 KB WebP fills the portfolio tile edge to edge. Verified production at 1440, 390, and 320 pixels: image loads, seven projects remain, no horizontal overflow or JavaScript errors, and mobile navigation works.
- Deployed source `b4d7160` to `https://9240a11c.eastbayprojects-1vq.pages.dev` and verified `eastbayprojects.com/portfolio`.

## Homepage headline — September 14, 2026

- Changed the hero headline to “SOFTWARE FOR YOUR BUSINESS” at Nate’s request. Public build and diff checks passed; verified the new headline on the live homepage. Deployment: `https://45cb0935.eastbayprojects-1vq.pages.dev`, source `b3cf512`.

## Custom software offer — September 14, 2026

- Homepage introduction now addresses slow websites, cluttered or broken internal tools, and expensive CRMs like Salesforce, offering custom software built with AI and deployed by experienced engineers.
- Added a prominent full-width “Custom Software, Built with AI” service at the top of the services grid, linking to Vibe Code to Production. Consolidated the former standalone promo into this service.
- Reduced finish/finishing language on the landing page to one call to action; other sections describe code review, integrations, testing, deployment, and ownership.
- Public build and diff checks passed. Checked the service card spans its grid, its destination, and both pages for horizontal overflow at 1440, 390, and 320 pixels. Contact form action is preserved. Verified deployed copy on both live routes.
- Deployment: `https://701dcc63.eastbayprojects-1vq.pages.dev`, source `4b0fbf1`.

## Copywriting and technical SEO — September 14, 2026

- Installed and applied Corey Haines’s Copywriting and Copy Editing skills. Aligned homepage problems with the custom software offer, clarified delivery and inquiry copy, and reduced generic wording across marketing pages. Approved headlines, quotes, prices, and founder credentials remain intact.
- Added public brand context in `.agents/product-marketing.md` and review notes in `docs/copy-review-2026-09-14.md`; neither is deployed.
- All eight indexable pages have unique titles/descriptions, canonical URLs, matching Open Graph/Twitter metadata, a shared 1200×630 social card, and favicon. Internal HTML links use canonical extensionless routes.
- Added a branded noindex `404.html`; missing root and nested URLs now return HTTP 404 instead of the homepage with HTTP 200.
- Sitemap already listed the correct eight canonical URLs; validated it against the actual build and verified robots.txt points to it. The 404 page is excluded.
- Added `python3 scripts/check-public-seo.py` to verify built metadata, local assets, links, anchors, sitemap completeness, and 404 indexing rules.
- Verification: build and SEO checker passed; all nine page layouts checked at 1440/390/320. Form actions remain `/api/contact`; handlers were not changed or resubmitted. Live checks passed for eight pages, robots, sitemap, social assets, and two missing paths. HTTP and .html URLs redirect correctly. The www host serves content with canonical tags pointing to the apex domain; no host redirect was configured.
- Deployment: `https://4b8e3ac3.eastbayprojects-1vq.pages.dev`, source `43494eb`.

## Grid-paper layers and homepage transition — September 14, 2026

- Added subtle torn graph-paper corners across hero sections and small paper-stack shadows to homepage panels. Preserved ivory/green styling and readable foreground content.
- Shared `paper-depth.js` adds decorative, aria-hidden layers and restrained desktop parallax (24px maximum). Scroll listeners are passive and updates are frame-scheduled. Touch devices and reduced-motion preferences use static layers; native touch scrolling is preserved, with no wheel/touch interception or scrolling library. Existing animated anchor handlers now respect reduced motion.
- Changed “The Problem” to “Where We Can Help,” with calm, concrete cards about usable websites, connected internal tools, and a CRM that fits the business.
- Verified nine page layouts at 1440/390/320; desktop parallax, touch static layers, and reduced-motion behavior passed. Build, SEO, and JavaScript syntax checks passed. Live homepage verified at desktop and mobile widths. Physical-device scroll feel was not measured.
- Deployment: `https://ff25cea0.eastbayprojects-1vq.pages.dev`, source `c98c24b`.

## Geographic positioning — September 14, 2026

- Replaced Austin/DC service-area copy in the homepage eyebrow, byline, contact details, and stamp with East Bay founding and service to American companies. Updated the civic service-area label and saved the preference in marketing context. Project locations remain factual.
- Public build, SEO checker, and live homepage copy verification passed. Deployment: `https://da378f23.eastbayprojects-1vq.pages.dev`, source `ded22db`.

## How We Work — September 14, 2026

- Replaced the technical-specification graphic with a three-step How We Work panel: free no-obligation consult, 30-minute review of current work, and a fixed-fee quote/timeline reviewed on a follow-up call. Added the conditional first-call preview note and a link to the homepage contact form.
- Build, SEO, and layout checks passed at 1440/390/320. Verified the panel and removal of the specification document on production. Deployment: `https://eef67710.eastbayprojects-1vq.pages.dev`, source `ac99323`.

## Grid revision and booking request — September 14, 2026

- Replaced small torn graph-paper scraps with broad fading grid fields behind the homepage hero, services, and Why Us, plus selected landing/portfolio intros. Lowered line opacity and removed rotated panel styling. Native touch scrolling and reduced-motion behavior remain intact.
- Added the requested italic hour-long conversation note after How We Work step 2.
- Build/SEO checks, nine-page layouts at 1440/390/320, desktop motion, reduced-motion and touch fallback checks passed. Visually reviewed the broad desktop grid. Live note and stylesheet verified.
- Deployed `edcc063`: `https://61b33161.eastbayprojects-1vq.pages.dev`.
- Pending: create Google appointment booking page and replace the How We Work contact CTA with Book a Call. Latest user direction is to use Nate’s calendar for now (originally Josh), 30 minutes, 9am–5pm every day, America/Chicago. The existing branded Workspace connector has Gmail scopes only; no Calendar/admin authorization is available. Google Calendar connection was suggested but not confirmed. The legacy auth tool opened a consent flow containing only Gmail scopes, so it does not resolve this. No booking calendar or URL has been created; existing contact CTA remains functional.


## Architectural paper treatment (September 14, 2026)

- Replaced flat CSS grids with an original 68 KB WebP texture: pale blue graph lines, soft creases, fibrous torn edges, and contact shadows inspired by Nate’s drafting-paper references. Broad, translucent placement in hero/introduction and How We Work sections; dark services section stays clear.
- Preserved native touch scrolling and reduced-motion support; subtle parallax is desktop-only. Checked all nine routes at 1440, 390, and 320 pixels with no horizontal overflow or browser errors, plus touch/reduced-motion behavior. Inspected desktop/mobile hero and How We Work screenshots.
- Public build, SEO/link/404 checks, and diff checks passed. Deployed source `28a3b68`; verified production CSS and texture bytes. Initial asset propagation returned a transient 404 before the new asset became available.
- Booking setup remains pending Calendar authorization as documented above; no appointment schedule has been created.

## Team page update (September 15, 2026)

- Removed Josh’s profile and references from About, including metadata. Adjusted Nate’s profile into a single-founder layout.
- Public build and SEO checks passed; inspected desktop and mobile profile layouts and verified no overflow. Production About confirms one profile and no Josh references. Deployed source `622910f`.

## Privacy and legal identity (September 15, 2026)

- Privacy notice now identifies McGuire LLC (DBA East Bay Projects), uses the shared site design/navigation, and covers project/career inquiries, stored request metadata, and the existing Google Ads tag. Added advertising preference and Google data-use links. Existing retention and inquiry rights wording retained.
- All nine public page footers identify McGuire LLC and link to /privacy. No separate terms page exists in the public build; archived design experiments and unrelated app policies were not changed. Privacy was already in the sitemap.
- Verified public build, SEO/local links, all nine footers at desktop and two mobile widths, and privacy appearance. Production privacy content confirmed after deployment of `4609df4`. This change does not certify jurisdiction-specific legal compliance.
