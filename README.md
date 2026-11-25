# Bay Area Gameplan

A dependency-free, static schedule-and-radio dashboard for Bay Area sports fans. It brings together 49ers, Stanford and Cal football, selected MLB special events, and Westwood One NFL radio windows, with source links and explicit coverage gaps.

> **Research snapshot:** November 25, 2026 · Pacific Time · San Francisco 94122 context
>
> **Important:** This project does **not** currently establish a verified vacation/free-time window. The future schedules and station carriage are incomplete, and missing rows are not treated as days without sports.

## Run locally

The site fetches a local JSON file, so serve the repository over HTTP rather than opening `index.html` with a `file://` URL:

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

Open `http://localhost:8000`. No package install or build toolchain is required. In a hosted preview, bind to `0.0.0.0` and use the preview URL.

## Validate and build

```sh
python3 -m json.tool site/data/schedules.json >/dev/null
node --check site/assets/app.js
node --check site/assets/category.js
python3 scripts/build_site.py
git diff --check
```

The build script validates source URLs, date shapes, data sections and category-page assets, then copies the static site into the ignored `build/` directory. Do not commit generated build output.

## What is included

- **Dashboard:** month calendar/list view, sport filters, search, event source details, the next dated team game, and a Westwood One network-window strip.
- **Category pages:** [MLB](site/pages/mlb.html), [49ers](site/pages/nfl.html), [college football](site/pages/college.html), [radio](site/pages/radio.html), and the [source inventory](site/pages/sources.html).
- **League calendar:** NFL 2027 postseason date windows are listed separately from 49ers fixtures; no team qualification is inferred.
- **Radio map and station notes:** distinguishes Bay Area listings from Sacramento-market stations and online-only streams; 94122 coverage is not inferred from a frequency alone.
- **Review flags:** source conflicts, future-schedule gaps, network affiliate uncertainty, and duration assumptions.
- **No false all-clear:** the current source audit finds **zero verified all-clear vacation windows**.

## Dataset coverage and limits

The source-of-truth snapshot is [`site/data/schedules.json`](site/data/schedules.json); its source inventory and key findings are summarized in [`docs/source-audit.md`](docs/source-audit.md).

- The official 2027 MLB Stats API returned 2,430 regular-season games, but the checked-in static dashboard includes **selected event/date summaries only** (including a day-level Spring Training count), not a full Giants/Athletics or league game-by-game feed. Empty MLB dates are not meaningful.
- The 2026 49ers regular-season and preseason rows are recorded. Past kickoff times were left blank where the reviewed official page extract did not retain them. Week 18’s Arizona matchup has no assigned date or kickoff in this audit snapshot.
- Stanford and Cal’s 2026 football schedules and their announced 2027 opponent grids are listed. Conference dates/times not yet assigned are shown as opponent-only rows. Older 2028–29 ACC grids and historical Stanford series entries are clearly marked provisional or in need of revalidation.
- Westwood One entries are network airtime-start listings converted from ET to PT. They are not guaranteed kickoff times, local affiliate clearances, or on-air end times.
- Radio affiliations are dated snapshots, not guarantees. The 2026 Athletics guide identifies Sacramento stations; a Bay Area terrestrial A’s affiliate was not confirmed. Cal 810 AM call-sign branding conflicts across official 2026 materials.
- MLB’s 2:38 game-time figure is a 2025 mean and historical planning context. The three-hour football figure is an estimate only. Neither predicts an event’s end or station sign-off.

Keep unknown values `null` in the data and document any new estimate. Never convert a missing schedule row into a free-time recommendation.

## Source updates

1. Re-check the official schedule/affiliate pages listed in `site/data/schedules.json` and `docs/source-audit.md`.
2. Update the dataset and `asOf` date together. Preserve uncertainty notes and the source URL for every dated event.
3. Re-run the validation commands above, review the full mobile layout, and update source-audit notes.
4. Do not add inferred times, games, station carriage or vacation windows as facts.

## GitHub Pages

[`.github/workflows/validate.yml`](.github/workflows/validate.yml) runs the JSON, JavaScript and static-build checks for pull requests and `main`. [`.github/workflows/pages.yml`](.github/workflows/pages.yml) builds on `main` and deploys the `build/` artifact with GitHub Pages Actions. In repository settings, choose **Settings → Pages → Build and deployment → GitHub Actions**. The first Pages deployment runs after this branch is merged to `main` (or through manual workflow dispatch once Pages is enabled).

## Accessibility and privacy

The front end is plain HTML/CSS/JavaScript; it uses no analytics, cookies, trackers, or third-party runtime APIs. Keyboard users can tab through controls, open event details, and press `/` to focus schedule search. Reduced-motion preferences are respected. Google Fonts are a progressive enhancement; system font fallbacks are included.
