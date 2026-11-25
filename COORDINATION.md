# COORDINATION - shared task board

Status values: unclaimed, in progress, done, needs review.
A "needs review" item is published on the site's Flagged for Review page and does not block anything.

| Task | Status | Owner (session) | Branch | Files touched | Notes |
|---|---|---|---|---|---|
| T1 Repo review and source verification | needs review | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/data.json (flags), COORDINATION.md | 12 flags, see docs/flagged.html |
| T2 Vacation windows 2027-2029 | needs review | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/data.json (windows), docs/vacation.html | 2027 partly verified; 2028 and 2029 are estimates |
| T3 Games table (NFL, 49ers, Stanford, Cal, Westwood One) | needs review | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/data.json (games), docs/games.html | 85 rows, each with a source link |
| T4 MLB (all 30 clubs; Giants and Athletics full schedules) | in progress | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/data.json (games, MLB rows) | Only Giants/Athletics series in MLB.com releases loaded. All 30 clubs NOT done. Flagged F03, F08. |
| T5 Daily scoreboard (prev/next/today) | done | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/scoreboard.html, docs/app.js | Gaps use loaded data only; MLB not loaded, so no day is confirmed free |
| T6 Landing page, sources, flagged pages | done | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | docs/index.html, docs/sources.html, docs/flagged.html, docs/style.css | Static GitHub Pages site, /docs on main |
| T7 Integration, PR, merge, Pages deploy | in progress | arena/bbbb5122-freetime4 | arena/bbbb5122-freetime4 | COORDINATION.md | See log below |

## Session log

- 2026-11-25: Single session (arena/bbbb5122-freetime4) claimed all tasks. No conflicts with other sessions.
- Research sources are listed on the site's Sources page (26 entries; secondary sources labeled).
- Irregularities found (see Flagged for Review): Dec 17 2026 49ers at Chargers time conflict (Westwood One 4:30 PT vs 49ers 5:15 PT); Jan 3 2027 Eagles at 49ers (Westwood 4:30 PT vs 49ers 5:20 PT); MLB and NFL 2028-2029 schedules not released; Super Bowl 2028 and 2029 dates unverified; MLB game-length averages conflict; Bay Area carriage of most games unverified.
- Not completed: full 30-club MLB schedule, full Giants and Athletics 2026-2027 schedules, Cal and Athletics radio carriage. These are listed as open items.

## Merge and deploy

- PR, merge, and GitHub Pages deploy results are recorded below once completed.
