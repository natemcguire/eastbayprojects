# Private ad review service

A small, dependency-free review application for East Bay Projects display and text ads. It binds
only to loopback, stores decisions locally in SQLite, and places only approved ads into an
idempotent sync queue. It does not call Google Ads.

## Runtime boundary

Source and schema are safe for Git. Private state stays on the Mac mini at:

```
~/.local/share/eastbayprojects/ad-review/
  review.sqlite3
  creatives/
  import/
  service.env
```

The default service URL is `http://127.0.0.1:8765`. The app intentionally has no public bind
option. Put Tailscale Serve in front of it; never use Funnel.

## Run

```sh
cd ~/Projects/eastbayprojects
./scripts/workspace-preflight.sh
python3 ad_review/app.py --seed
```

Open `http://127.0.0.1:8765/display`, `/text`, or `/queue`.

## Import private drafts

The importer accepts a top-level JSON array. Stable IDs make repeated imports safe: existing IDs
are skipped and approved/rejected records are never overwritten.

```sh
python3 ad_review/import_ads.py \
  ~/.local/share/eastbayprojects/ad-review/import/text-ads.json
```

Minimal item:

```json
{
  "id": "stable-text-id",
  "kind": "text",
  "title": "Internal label",
  "campaign": "GovCon websites",
  "region": "DMV",
  "aspect_ratio": "responsive search",
  "payload": {
    "headline": "Websites for Federal Firms",
    "description": "Credibility-first delivery without agency layers.",
    "display_url": "eastbayprojects.com/contact",
    "sitelinks": ["Meet Nate", "View Portfolio"]
  }
}
```

Display items use the same envelope and may add `creative_path`, relative to the private
`creatives/` directory. Their payload can include `headline`, `description`, and `badge`.

## ntfy

Notifications are sent only when a new ID is imported or created through the API. Put configuration
in the private `service.env`; do not commit it.

```sh
export NTFY_TOPIC_URL='https://ntfy.sh/private-topic-name'
export NTFY_TOKEN='optional-access-token'
export EASTBAY_REVIEW_BASE_URL='https://nates-mac-mini.YOUR-TAILNET.ts.net'
```

## LaunchAgent and Tailscale Serve

Install the checked-in plist template after replacing `__HOME__` and `__PROJECT_DIR__`:

```sh
mkdir -p ~/Library/LaunchAgents
sed -e "s|__HOME__|$HOME|g" \
    -e "s|__PROJECT_DIR__|$HOME/Projects/eastbayprojects|g" \
    ad_review/com.eastbayprojects.ad-review.plist.example \
    > ~/Library/LaunchAgents/com.eastbayprojects.ad-review.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.eastbayprojects.ad-review.plist
launchctl kickstart -k gui/$(id -u)/com.eastbayprojects.ad-review
curl http://127.0.0.1:8765/api/health
tailscale serve --bg --yes 8765
tailscale serve status
```

Tailscale Serve is tailnet-only. Do not substitute `tailscale funnel`.

## Environment

- `PORT`: loopback port, default `8765`
- `EASTBAY_AD_REVIEW_STATE`: private state directory
- `EASTBAY_REVIEW_BASE_URL`: Tailscale URL placed in ntfy review links
- `NTFY_TOPIC_URL`: complete private ntfy topic URL
- `NTFY_TOKEN`: optional bearer token

## Safety model

- The database trigger rejects queue inserts for ads that are not approved.
- Approvals are audited in `review_events`.
- Queue jobs use unique idempotency keys.
- There is no sync worker yet, so approval cannot mutate the Google Ads account.
- Browser profiles, credentials, generated assets, database files, logs, and notification secrets
  remain outside Git.

## Build a private sync plan

```sh
python3 ad_review/build_sync_plan.py
```

This writes `~/.local/share/eastbayprojects/ad-review/sync/plan.json` with mode
`PLAN_ONLY`. The planner reads only ads whose review status is `approved` and whose sync job is
`queued`. It proposes a PAUSED Search campaign with four category-based ad groups, deduplicates
RSA copy, enforces the 15-headline and 4-description caps, and preserves final URLs and sitelinks.
Approved display assets are grouped for the existing Performance Max target read from private
SQLite settings. Live customer, campaign, and asset-group identifiers are never committed to Git.

Building the plan makes no Google calls and changes no database status. Actual Google Ads syncing
is a separate, explicit future step.
