# East Bay Projects working agreement

## Canonical state

- This agreement applies only to East Bay Projects. It does not authorize uploading other
  projects or data to any cloud service.
- `origin/main` on `git@github.com:natemcguire/eastbayprojects.git` is the sole canonical state
  for cloud-safe source code and documentation in this repository.
- `nates-mac-mini` is the canonical development and runtime host.
- The canonical checkout path on the Mac mini is `~/Projects/eastbayprojects`.
- The laptop checkout is a handoff/staging copy, not an active development workspace.
- Do not rsync `.git`. Move code between machines with Git commits, fetches, and fast-forward pulls.
- Persistent or private runtime state such as the review database, job queue, generated drafts,
  browser profile, Google session, logs, contact data, API credentials, and ntfy secrets lives on
  the Mac mini and must not be copied into Git or another cloud service.
- Before adding a new file class to Git, decide whether it is public source/documentation or
  private operational state. Default uncertain data to private and local-only.

## Required preflight

Before editing, building, running browser automation, or starting a service:

1. Run `./scripts/workspace-preflight.sh`.
2. If the checkout is dirty, ahead, or diverged, stop and reconcile it before new work.
3. If the checkout is clean but behind, the script fast-forwards it from `origin/main`.
4. Develop on the Mac mini unless Nate explicitly authorizes a temporary local exception.

For an explicitly authorized laptop exception, run:

```sh
EASTBAY_ALLOW_LOCAL=1 ./scripts/workspace-preflight.sh
```

Any exception work must be committed and pushed immediately, then pulled on the Mac mini before
runtime work resumes.

## Handoffs

- Keep `CURRENT_STATUS.md` current after material deployment, architecture, campaign, or runtime
  changes.
- Finish each coherent change with proportionate verification, a commit, and a push to `main`.
- After pushing, verify the Mac mini checkout is clean and matches `origin/main`.
- Never use blind directory overwrites to resolve Git divergence.

## Hosting boundary

- Public marketing pages deploy through the existing Cloudflare Pages project.
- The ad review/approval application is private and runs on the Mac mini behind Tailscale.
- Do not expose the approval application, browser-control endpoints, queue, or secrets publicly.

## Public site design and navigation

- The production homepage is the design reference for every marketing page. Match its approved ivory/green palette, DM Sans and Space Grotesk fonts, header, buttons, and footer using `/style.css`; do not introduce separate page themes.
- Primary Contact and Start a Project links lead to the homepage form (`/#contact`). Keep `/contact` as an indexable standalone page with the same design and a footer link.
- Civic belongs in the footer, not desktop or mobile primary navigation.
- Both contact forms must save through `/api/contact` and the existing `LEADS_DB` binding. Verify successful storage and failure behavior; opening an email draft is not a submitted inquiry.
- Keep `sitemap.xml` and its `robots.txt` reference current for public marketing pages. These files are public source; operational documents and private application state must not be deployed.
- Write plain, specific copy. Explain the work and terms; avoid formulaic conditional pitches, inflated promises, fear-based claims, and agency jargon.
- Use an isolated browser/profile for testing. Do not control Nate’s signed-in Chrome unless he explicitly requests it.
