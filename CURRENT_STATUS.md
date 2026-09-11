# East Bay Projects — Current Status

Last updated: September 11, 2026

## Source of truth

- Repository: `git@github.com:natemcguire/eastbayprojects.git`
- Branch: `main`
- `origin/main` is the sole canonical code state.
- `nates-mac-mini` is the canonical development and runtime host, not the canonical Git history.
- Only cloud-safe source and documentation belong in GitHub. Approval records, browser sessions,
  generated drafts, credentials, contact data, logs, and queue state remain private on the mini.
- Current deployment commit: `8a88235` (`Strengthen founder proof and performance copy`)
- Production: `https://eastbayprojects.com`
- Cloudflare Pages project: `eastbayprojects`
- Latest deployment URL: `https://ebee08a6.eastbayprojects-1vq.pages.dev`
- Google Ads tag `AW-18335868802` is installed immediately after `<head>` on every public HTML page.
- The Cloudflare cache for `eastbayprojects.com` was purged after deployment.

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
- Previous ivory/green preview remains available at `https://4b150e4f.eastbayprojects-designs.pages.dev`. New deployment pending.
