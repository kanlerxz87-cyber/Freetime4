# Freetime4 — Coordination Board

Shared task board for parallel agent sessions. This repo's current session branch is
`arena/6899e48c-freetime4`, branched from `01c149c` of `main`.

## Convention
- Claim a task by writing your session ID and file scope here, then commit and push that claim immediately.
- Never start a task another session has claimed. Keep scopes non-overlapping.
- Each session works on its own branch (or git worktree) named `session-<id>/<task>` and edits only files in its claimed scope.
- Make small, frequent commits; run `git pull --rebase` before every push.
- On merge conflict: stop, resolve without discarding the other session's work, log what happened.
- When a task is finished: record sources, verification performed, and any irregularities here; mark it done.
- Never mark anything verified without checking it against an official source; link that source.
- Shared outputs (table data, site index/navigation) are changed only by the final integration session once all other tasks are done. That session merges branches, re-verifies line by line, confirms the site builds with no broken links, and publishes to GitHub Pages.
- If a session crashes or its claim is more than 60 minutes old with no commits, any other session may take over the task and note the handoff here.

## Session ID (this session)
session-freetime4

## Tasks

| # | Task | Status | Owner | File scope | Sources / verification | Irregularities |
|---|------|--------|-------|------------|------------------------|----------------|
| 1 | Create COORDINATION.md task board | done | session-freetime4 | COORDINATION.md | n/a | none |
| 2 | Research official schedule availability (MLB/NFL/NCAAF 2026–2029) | done | session-freetime4 | data/schedules.json, docs/sources.md | MLB.com (2026 released 2025-08-26), 49ers.com (2026 released 2026-05-14), gostanford.com (Stanford 2026), calfootball.com (Big Game), westwoodonesports.com (2026 coverage) | 2027–2029 schedules not officially released yet |
| 3 | Build site skeleton (landing, nav, CSS, JS) | done | session-freetime4 | index.html, css/, js/ | n/a | none |
| 4 | Executive summary page | done | session-freetime4 | executive-summary.html | n/a | none |
| 5 | MLB data page (Giants/A's high priority, all 30 clubs) | done | session-freetime4 | mlb.html, data/ | MLB.com | 2027–2028 = estimates; per-game full season not republished |
| 6 | NFL data page (49ers, all NFL, preseason/regular/postseason) | done | session-freetime4 | nfl.html, data/ | 49ers.com official | 2027–2028 = estimates; Week 18 time TBD |
| 7 | NCAAF data page (Stanford, Cal high priority) | done | session-freetime4 | ncaaf.html, data/ | gostanford.com, calfootball.com | Cal full schedule not retrieved (partial) |
| 8 | Westwood One national NFL radio broadcasts page | done | session-freetime4 | westwood-one.html, data/ | westwoodonesports.com | Bay Area affiliate list unverified |
| 9 | Free-time calendar/scoreboard (clickable day nav, PST, free windows) | done | session-freetime4 | free-time.html | computed from data | durations are estimates |
| 10 | Flagged for Review page (unverified items, source links) | done | session-freetime4 | flagged-review.html | n/a | none |
| 11 | Verify every table row has a source link; blank + flag unverified | done | session-freetime4 | all data files | official sources linked per row | blanks left where not confirmed |
| 12 | Final integration: enable GitHub Pages, verify build/links | in progress | session-freetime4 | all | n/a | Pages not yet enabled |
| 13 | Create PR to main, merge, confirm Pages deploys, record in COORDINATION.md | unclaimed | session-freetime4 | n/a | n/a | n/a |

## Verification notes
- 2026 MLB: VERIFIED via MLB.com release (2025-08-26). Key dates: Opening 2026-03-25 (Yankees@Giants), Opening Day 2026-03-26, All-Star 2026-07-14, regular end 2026-09-27.
- 2026 NFL/49ers: VERIFIED via official 49ers schedule release (2026-05-14). Preseason 8/13, 8/20, 8/27; regular 2026-09-10 to 2027-01-10; Super Bowl LXI 2027-02-14 (SoFi).
- 2026 NCAAF Stanford: VERIFIED via gostanford.com (ACC release 2026-01-26). Big Game vs Cal 2026-11-21 at 12:00 p.m. PST.
- 2026 NCAAF Cal: PARTIAL — Big Game date/time verified; full schedule not retrieved.
- Westwood One 2026: VERIFIED network coverage (TNF/SNF/MNF/postseason/Super Bowl). Local Bay Area affiliate list NOT confirmed.
- 2027–2029: ALL ESTIMATES. Official schedules not released. Flagged ESTIMATE throughout.

## Irregularities flagged for review (see flagged-review.html)
1. Full 2026 MLB per-game schedule (all 30 clubs) — not republished game-by-game
2. A's 2026 home-game times — dates verified, times not pulled
3. Cal full 2026 schedule — only Big Game verified
4. Westwood One Bay Area affiliate list — unconfirmed
5. KNBR live-game carriage — unconfirmed
6. MLB 2026 postseason dates — not in source reviewed
7. Estimated game durations — not official
8. All 2027–2029 schedules — estimates, not official
9. NFL 2027 postseason rounds — estimates except Super Bowl LXI
10. Free-time windows — computed from estimates
