# COORDINATION.md - shared task board

Repository: kanlerxz87-cyber/Freetime4
Session: 48068f3b (branch `arena/48068f3b-freetime4`, from `main` at 01c149c36e911e583fef4d91122586cb33d8b1e2)

Statuses: unclaimed / in progress / done / needs review.

Branch note: the request asks for per-task branches named `session-<id>/<task>`. Arena restricts this session to the branch above, so every task is committed to `arena/48068f3b-freetime4`. Only one session works in this repository, so there are no cross-session claim conflicts. Claims below are recorded for the audit trail and were written at the start of each task.

## Claims and status

| Task | Scope (files) | Session | Status | Notes |
|---|---|---|---|---|
| T1 Raw MLB data | `docs/data/raw/*.json` | 48068f3b | done | Official MLB Stats API responses. Totals reconciled (see below). |
| T2 Data tables and sources | `docs/data/*.json` (except raw) | 48068f3b | done | Every row cites a source ID in `sources.json`. Unverified values left blank. |
| T3 Scoreboard data | `scripts/build_scoreboard.js`, `docs/data/scoreboard.json` | 48068f3b | done | Westwood One ET converted to PT (-3h). |
| T4 Site build | `docs/*.html`, `docs/assets/*`, `scripts/build_site.js` | 48068f3b | done | GitHub Pages, source folder `/docs` on `main`. |
| T5 Verification | `scripts/check_ids.js`, `scripts/check_site.js` | 48068f3b | done | Source IDs resolve; all pages render (DOM test); all local links resolve. |
| T6 Vacation analysis | `docs/data/vacation-windows.json` | 48068f3b | done (partial) | Verified windows only; 2028-2029 not published. |
| T7 Integration, PR, merge, Pages confirm | this file, PR to `main` | 48068f3b | in progress | Integration session only. Result below. |

## Verification log

- MLB daily-count files: sums match API totals exactly. Regular season 2,430 (184 dates); spring training 469 (33 dates); Giants 194 (192 dates); Athletics 193 (192 dates, after re-fetch from the API; first transcription was one short).
- MLB clubs: 30 active clubs (`mlb-teams.json`), matches the API on re-fetch.
- 2027 season calendar re-fetched and stored (`mlb-seasons-2027.json`); 2026 calendar stored (`mlb-seasons-2026.json`).
- 2028 and 2029 season queries return empty results; not published.
- Westwood One national NFL events: 35 listed; Thanksgiving-week kickoffs differ from NFL.com (flagged F-01).
- 49ers, Stanford, Cal: official team pages checked for 2026 (partial: Cal list starts Sep 19; 49ers Week 18 TBD).
- Durations: MLB 2:38 (official, 2025). NFL 3:03 (secondary; no NFL official figure). College: unverified (blank).
- Super Bowl LXI: Feb 14, 2027, SoFi Stadium (SoFi news release). Kickoff not published.

## Irregularities (see Flagged for Review)

- F-18: API `firstDate2ndHalf` 2027-07-16 vs league games on 2027-07-15.
- F-02, F-03: 49ers kickoffs differ from Westwood One.
- F-10: Stanford vs Cal (Nov 21) home/away conflict.
- F-09: Stanford radio station conflict.
- F-17: Super Bowl LXII date conflict.

## Merge conflicts and handoffs

- Merge conflicts: none. This session did not work in parallel with another session.
- Handoffs: none. Remaining work is listed under "Open items".

## Open items (not blocking merge; flagged)

- Per-game times and opponents for all 30 MLB clubs (only daily counts ingested).
- 2027 NFL and college schedules (not published in the sources retrieved).
- NFL and college postseason and bowl dates for 2026-27.
- Radio coverage check at 94122 (FCC link provided).
- Athletics radio stations.

## PR and merge result

- PR: pending (recorded after creation).
- Merge: pending.
- Pages: pending.
