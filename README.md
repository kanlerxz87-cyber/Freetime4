# Freetime4 — Free Time Vacation Planner

Static, GitHub Pages-ready dashboard for planning Bay Area vacations around live sports that may be heard on AM/FM radio (San Francisco, outer sunset 94122).

A minute is **free** when none of these are on air:
- **MLB** — all 30 clubs, San Francisco Giants and Oakland Athletics flagged high priority
- **NFL** — San Francisco 49ers (preseason, regular season, postseason) high priority; all NFL
- **Stanford NCAAF** — high priority
- **Cal NCAAF** — high priority
- **Westwood One Sports national NFL radio broadcasts** (TNF, SNF, MNF, postseason)

## Site structure
- `index.html` — combined landing page (links to the `docs/` published planner and to this branch's detail pages)
- `docs/` — published GitHub Pages planner (scoreboard, games table, vacation windows, sources, flagged register): scoreboard.html, games.html, vacation.html, sources.html, flagged.html, data.json
- `legacy-dashboard/` — earlier root dashboard, copied here and preserved
- `executive-summary.html` — executive summary & best estimated vacation windows (2026–2029)
- `free-time.html` — PST free-time calendar with yesterday/today/tomorrow navigation
- `mlb.html` — MLB: all 30 clubs with official schedule links; Giants/A's high priority
- `nfl.html` — NFL: 49ers 2026 verified schedule + season windows
- `ncaaf.html` — NCAAF: Stanford 2026 verified + Cal
- `westwood-one.html` — Westwood One national NFL radio
- `flagged-review.html` — this branch's flagged/unverified items
- `css/style.css`, `data/schedules.json` — styles and canonical data
- `COORDINATION.md` — shared task board (both sessions)

## Publish with GitHub Pages
The repository is a plain static site. In GitHub, open **Settings → Pages**, select **Deploy from a branch**, choose `main` and `/ (root)`, then save. No build step is required.

## Accuracy / current limits
This implementation does **not** contain a complete verified game feed for every team. It intentionally shows missing data rather than translating missing rows into a "free" determination. The only year-specific announcement summarized is MLB's official 2026 regular-season schedule release. **2027–2029 schedules are not officially released** (as of 2026-11-25); those values are estimates, not verified schedules.

Radio carriage and reception in San Francisco's Outer Sunset must be checked independently from league schedules. See the Flagged for Review pages for gaps and caveats.

## Sessions
- `arena/bbbb5122-freetime4`: built the `docs/` planner, sources, flagged register, and GitHub Pages deploy (live).
- `arena/6899e48c-freetime4` (this branch): added the executive summary, per-sport detail pages, all-30-club MLB listing, and PST free-time calendar.

See COORDINATION.md for the shared task board, verification log, and merge/deploy record.
