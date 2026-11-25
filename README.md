# Freetime4 — Free Time Vacation Planner

Plan your vacation around live sports on the radio in the San Francisco Bay Area (outer sunset, 94122).

A minute is **free** when none of these are on air:
- **MLB** — all 30 clubs, San Francisco Giants and Oakland Athletics flagged high priority
- **NFL** — San Francisco 49ers (preseason, regular season, postseason) high priority; all NFL
- **Stanford NCAAF** — high priority
- **Cal NCAAF** — high priority
- **Westwood One Sports national NFL radio broadcasts** (TNF, SNF, MNF, postseason)

## Site (GitHub Pages)
- `index.html` — landing page + executive summary
- `executive-summary.html` — detailed executive summary
- `free-time.html` — interactive free-time calendar / scoreboard (click yesterday/tomorrow, pick any date, PST free-time windows)
- `mlb.html` — MLB: all 30 clubs with official schedule links
- `nfl.html` — NFL: 49ers 2026 verified schedule + season windows
- `ncaaf.html` — NCAAF: Stanford 2026 verified + Cal
- `westwood-one.html` — Westwood One national NFL radio
- `flagged-review.html` — unverified items & estimates

## Data
- `data/schedules.json` — canonical schedule data with verification status and source links

## Verification
Every table row either links to an official source (MLB.com, 49ers.com, gostanford.com, calfootball.com, westwoodonesports.com) or is explicitly marked ESTIMATE / UNVERIFIED. 2027–2029 schedules are not officially released as of 2026-11-25; those values are estimates, not verified schedules.

See COORDINATION.md for the shared task board and status.
