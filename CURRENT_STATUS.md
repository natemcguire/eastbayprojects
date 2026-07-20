# East Bay Projects — Current Status

Last updated: July 20, 2026

## Source of truth

- Repository: `git@github.com:natemcguire/eastbayprojects.git`
- Branch: `main`
- `origin/main` is the sole canonical code state.
- `nates-mac-mini` is the canonical development and runtime host, not the canonical Git history.
- Only cloud-safe source and documentation belong in GitHub. Approval records, browser sessions,
  generated drafts, credentials, contact data, logs, and queue state remain private on the mini.
- Current deployment commit: `1ae4b6a` (`Install Google Ads site tag`)
- Production: `https://eastbayprojects.com`
- Cloudflare Pages project: `eastbayprojects`
- Latest deployment URL: `https://48e3e17d.eastbayprojects-1vq.pages.dev`
- Google Ads tag `AW-18335868802` is installed immediately after `<head>` on every public HTML page.
- The Cloudflare cache for `eastbayprojects.com` was purged after deployment.

After the July 20 handoff, development should continue from the Mac mini checkout at
`~/Projects/eastbayprojects`. Do not treat the laptop checkout as the active development
workspace unless a new handoff explicitly reverses this decision.

## Live site

- `/` — primary commercial site
- `/contact` — lead form and Google Ads landing page
- `/portfolio.html` — selected work
- `/civic.html` — civic and campaign work
- `/privacy.html` — privacy notice
- Contact form submissions are stored in the Cloudflare D1 database bound as `LEADS_DB`.

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

1. Verify the remote checkout and toolchain.
2. Start a persistent Playwright-controlled Chrome session on the mini and let Nate sign into
   Google Ads before further browser automation.
3. Choose a small local application stack and persistence layer appropriate for a single-owner
   Tailscale service.
4. Build the display-ad review page and text-ad review/preview page.
5. Add approval/rejection persistence and the queued-sync state machine.
6. Configure ntfy notifications with the private review URL.
7. Generate the regional creative families and place them into `pending_review`.
8. Integrate the approved queue with the authenticated Google Ads session/API, with dry-run and
   idempotency safeguards before any account mutation.

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
- SQLite records ads, audit events, and idempotent sync jobs. A database trigger prevents
  unapproved ads from entering the sync queue.
- Private state defaults to `~/.local/share/eastbayprojects/ad-review/`; it is not stored in Git.
- The importer accepts private JSON arrays with stable IDs and skips existing records.
- ntfy configuration is environment-only. Tailscale Serve should proxy port 8765; Funnel is
  prohibited.
- The Google Ads sync worker is intentionally not implemented yet, so review actions cannot change
  the live account.

### Runtime checkpoint (July 20, 2026)

- LaunchAgent `com.eastbayprojects.ad-review` is installed and serving successfully on loopback
  port 8765.
- Twelve private text-ad variants were imported with stable IDs and remain `pending_review`.
- Tailscale Serve could not be activated until Serve is enabled for this node in the tailnet admin
  flow. The application remains inaccessible off-host until that approval is completed.
- ntfy hooks are present but require private `service.env` values before notifications are sent.
