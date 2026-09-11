# East Bay Projects test site

The active preview retains the existing East Bay Projects design and integrates civic
through the main homepage, services, portfolio, navigation, and inquiry flow. It also
includes careers and two prospective operations/growth studies. The initial ten
design explorations remain available as an archive.
This is a separate test site. The root marketing pages and production Cloudflare
Pages project are not part of this build or deployment.

Build: `python3 scripts/build-design-lab.py`

Preview: `python3 -m http.server 4322 --bind 127.0.0.1 --directory design-dist`

Deploy from this directory:

```sh
wrangler pages deploy ../design-dist --project-name eastbayprojects-designs --branch main
```

The active revision is `/` (also `/current/`). Careers are at `/current/careers.html`;
prospective studies are at `/current/case-studies.html`, with separate Kingstowne
and Straus pages. The research memos in `docs/research/` cite public sources and
separate facts from hypotheses; they are not copied into the deployment.

The archived gallery is `/directions.html`; individual directions use the IDs in `concepts.json`.
`/compare.html` shows two directions side by side, with desktop and phone views.
Preview forms, including the careers form, run entirely in the browser and do not
submit or store inquiries or applications. Forms are inert until their preview
handlers are attached.
There are no advertising tags, production database bindings, or email senders.
All routes are marked noindex, with an additional response header and robots file.

Public reference assets:

- Seamaphore: screenshot of `https://www.seamaphore.com/`, September 11, 2026.
- Brown for Austin: screenshot of `https://brownforaustind1.com/`, September 11, 2026.
- Austin Tax Rate Election: existing public project screenshot in this repository.
- Nate’s Software: public shopkeeper artwork from `https://nates-software.com/nate-portrait.png`, used within a typographic project illustration.
- Nate and Josh: public team portraits already present in this repository.

Only the explicit design-lab source files and these public assets are staged.
No source code, configuration, runtime data, or assets from the Seamaphore
repository are copied into this project.
