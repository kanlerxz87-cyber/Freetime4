# COORDINATION.md — shared task board

Session branch: `arena/9521dee6-freetime4` (platform-constrained; this session works only on this branch).
Session ID: `arena-9521dee6`

> Note on parallel sessions: the task instructions ask for branches named `session-<id>/<task>`.
> This session runs on a platform-fixed branch (`arena/9521dee6-freetime4`) and cannot create
> other branches. File scopes below are kept strictly non-overlapping so parallel sessions
> editing other branches do not collide with these files.

## Task board

| ID | Task | Status | Owner | Files / scope | Notes |
|----|------|--------|-------|---------------|-------|
| T1 | Repo init + coordination board | done | arena-9521dee6 | COORDINATION.md, README.md | Board created 2026-11-25 |
| T2 | Research: official schedules (MLB, NFL, NCAAF Stanford/Cal, Westwood One) 2026–2029 + release status | in progress | arena-9521dee6 | research/* | Every fact gets an official source URL |
| T3 | Research: SF Bay Area AM/FM radio stations & their live sports (94122) | in progress | arena-9521dee6 | research/radio.md | KNBR, A's, Stanford, Cal, Westwood One, other sports |
| T4 | Data pipeline: verified + estimated schedule JSON (day-by-day, PST) | unclaimed | — | scripts/*, data/* | Estimations flagged per event |
| T5 | Site build: landing + subpages (calendar/scoreboard, tables, executive summary) | unclaimed | — | site/* | GitHub Pages via Actions |
| T6 | Executive Summary + Flagged for Review page | unclaimed | — | site/pages/* | Unverified items listed with links |
| T7 | Verification pass: every table row has source link; broken-link check | unclaimed | — | verification/* | No inferred values |
| T8 | Integration, PR → main, merge, GitHub Pages deploy confirmation | unclaimed | — | .github/workflows/* | Record PR link here on completion |

## Log

- 2026-11-25 — arena-9521dee6 — Session start. Repo had only README.md. Created COORDINATION.md, claimed T1–T3.
- 2026-11-25 — arena-9521dee6 — T2/T3 research underway; sources being collected into research/.
