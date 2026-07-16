# ECO Club — Uttar Pradesh

A static dashboard tracking ECO Club notification uploads and the plantation drive across Government, Aided and Private secondary schools in Uttar Pradesh.

**Live site:** https://alokkmohan.github.io/ECO-Club/ (enable GitHub Pages on this repo, source: `main` branch, root)

## Pages

- `index.html` — landing page, state-wide headline numbers
- `summary.html` — every district, both reports, side by side
- `notification.html` — school-level notification upload status, filterable by district/category/status, searchable
- `plantation.html` — school-level plantation drive status + trees planted, filterable by district/category/status, searchable

Both report pages support a `?district=<Name>` URL parameter, so you can share a direct link to a single district's list (e.g. `notification.html?district=SHAHJAHANPUR`).

## Data

All data lives in `data/*.json`:

- `summary.json` — state-wide and per-district aggregates for both reports
- `notification.json` — one record per school: `{d: district, b: block, c: category (G/A/P), n: name, u: udise, s: status (0/1)}`
- `plantation.json` — same shape plus `t: trees planted`

These are generated from the ECO Club master school list (Government + Aided + Private secondary schools), matched by UDISE code against submitted notification and plantation records. Schools with a madarsa-pattern name are excluded. Private-school coverage is available for a subset of districts only.

To regenerate the data files, run the site-data build script against the current master workbook and drop the resulting JSON into `data/`.

## No backend

Everything here is static HTML/CSS/vanilla JS reading local JSON — no server, no build step. Any static host (GitHub Pages, Netlify, a custom domain) works.
