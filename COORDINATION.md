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
| 2 | Research official schedule availability (MLB/NFL/NCAAF 2026–2029) | in progress | session-freetime4 | docs/sources.md | MLB.com, NFL.com, Stanford/Cal athletics, Westwood One | 2027–2029 schedules not officially released yet |
| 3 | Build site skeleton (landing, nav, CSS, JS) | unclaimed | session-freetime4 | index.html, css/, js/ | n/a | n/a |
| 4 | Executive summary page | unclaimed | session-freetime4 | executive-summary.html | n/a | n/a |
| 5 | MLB data page (Giants/A's high priority, all 30 clubs) | unclaimed | session-freetime4 | mlb.html, data/ | MLB.com | 2027–2028 = estimates |
| 6 | NFL data page (49ers, all NFL, preseason/regular/postseason) | unclaimed | session-freetime4 | nfl.html, data/ | NFL.com | 2027–2028 = estimates |
| 7 | NCAAF data page (Stanford, Cal high priority) | unclaimed | session-freetime4 | ncaaf.html, data/ | gostanford.com, calbears.com | 2027–2028 = estimates |
| 8 | Westwood One national NFL radio broadcasts page | unclaimed | session-freetime4 | westwood-one.html, data/ | westwoodonesports.com | TBD times = estimates |
| 9 | Free-time calendar/scoreboard (clickable day nav, PST, free windows) | unclaimed | session-freetime4 | free-time.html, js/ | computed from data | n/a |
| 10 | Flagged for Review page (unverified items, source links) | unclaimed | session-freetime4 | flagged-review.html | n/a | n/a |
| 11 | Verify every table row has a source link; blank + flag unverified | unclaimed | session-freetime4 | all data files | official sources | n/a |
| 12 | Final integration: merge, re-verify, build check, GitHub Pages deploy | unclaimed | session-freetime4 | all | n/a | n/a |
| 13 | Create PR to main, merge, confirm Pages deploys, record in COORDINATION.md | unclaimed | session-freetime4 | n/a | n/a | n/a |

## Notes
- Today's date (user local): 2026-11-25 (UTC). Official 2027/2028/2029 MLB and NFL schedules are NOT yet released; they must be estimated and clearly flagged as estimations, not verified released schedules.
- "Free" = no MLB, no NFL (49ers + all clubs), no Stanford NCAAF, no Cal NCAAF, no Westwood One national NFL radio broadcast on air.
- Times in PST. Estimated durations: MLB ~150–180 min; NFL ~180 min + halftime 12–15 min; NCAAF ~180 min + halftime ~20 min. Durations to be researched.
