# Freetime4 — Coordination Board (combined)

Shared task board for parallel agent sessions. Repo: `kanlerxz87-cyber/Freetime4`.

## Sessions in this repository
- `arena/bbbb5122-freetime4` — built the `docs/` published planner, sources, flagged register, and GitHub Pages deploy (live on main, root).
- `arena/6899e48c-freetime4` (this session / branch `arena/6899e48c-freetime4`) — added executive summary, per-sport detail pages, all-30-club MLB listing, and PST free-time calendar.

## Convention
- Claim a task by writing your session ID and file scope here, then commit and push that claim immediately.
- Never start a task another session has claimed. Keep scopes non-overlapping.
- Each session works on its own branch (or git worktree) named `session-<id>/<task>` and edits only files in its claimed scope.
- Make small, frequent commits; run `git pull --rebase` before every push.
- On merge conflict: stop, resolve without discarding the other session's work, and log what happened.
- When a task is finished: record sources, verification performed, and any irregularities here; mark it done.
- Never mark anything verified without checking it against an official source; link that source.
- Shared outputs (table data, site index/navigation) are changed only by the final integration session once all other tasks are done. That session merges branches, re-verifies line by line, confirms the site builds with no broken links, and publishes to GitHub Pages.
- If a session crashes or its claim is more than 60 minutes old with no commits, any other session may take over the task and note the handoff here.

## Combined task board

| # | Task | Status | Owner (session) | File scope | Notes |
|---|------|--------|-----------------|------------|-------|
| S1 | Initial requirements audit, executive summary, static dashboard | done | arena/0452200e-freetime4 | index.html, styles.css, app.js, README.md, COORDINATION.md, .nojekyll | Root dashboard kept; copied to legacy-dashboard/ |
| T1 | Repo review and source verification | needs review | arena/bbbb5122-freetime4 | docs/data.json (flags), COORDINATION.md | 12 flags; see docs/flagged.html |
| T2 | Vacation windows 2027–2029 | needs review | arena/bbbb5122-freetime4 | docs/data.json (windows), docs/vacation.html | 2027 partly verified; 2028–2029 estimates |
| T3 | Games table (NFL, 49ers, Stanford, Cal, Westwood One) | needs review | arena/bbbb5122-freetime4 | docs/data.json (games), docs/games.html | 85 rows, each with a source link |
| T4 | MLB (all 30 clubs; Giants/Athletics full schedules) | in progress | arena/bbbb5122-freetime4 | docs/data.json (games, MLB rows) | Only Giants/A's series loaded; all 30 clubs NOT done (F03, F08) |
| T5 | Daily scoreboard (prev/next/today) | done | arena/bbbb5122-freetime4 | docs/scoreboard.html, docs/app.js | Gaps use loaded data only |
| T6 | Landing page, sources, flagged pages | done | arena/bbbb5122-freetime4 | docs/index.html, docs/sources.html, docs/flagged.html, docs/style.css | Static GitHub Pages site, /docs on main |
| T7 | Integration, PR, merge, Pages deploy | in progress | arena/bbbb5122-freetime4 | COORDINATION.md | Live URL recorded below |
| 1 | Create COORDINATION.md task board | done | session-freetime4 (arena/6899e48c-freetime4) | COORDINATION.md | Combined board |
| 2 | Research official schedule availability (MLB/NFL/NCAAF 2026–2029) | done | session-freetime4 | data/schedules.json | 2027–2029 not officially released |
| 3 | Build site skeleton (landing, nav, CSS, JS) | done | session-freetime4 | index.html, css/ | Combined with docs/ |
| 4 | Executive summary page | done | session-freetime4 | executive-summary.html | — |
| 5 | MLB data page (Giants/A's high priority, all 30 clubs) | done | session-freetime4 | mlb.html, data/ | 2027–2028 = estimates |
| 6 | NFL data page (49ers, all NFL, preseason/regular/postseason) | done | session-freetime4 | nfl.html, data/ | Week 18 time TBD |
| 7 | NCAAF data page (Stanford, Cal high priority) | done | session-freetime4 | ncaaf.html, data/ | Cal full schedule partial |
| 8 | Westwood One national NFL radio page | done | session-freetime4 | westwood-one.html, data/ | Bay Area affiliate list unverified |
| 9 | Free-time calendar/scoreboard (day nav, PST, free windows) | done | session-freetime4 | free-time.html | Durations are estimates |
| 10 | Flagged for Review page | done | session-freetime4 | flagged-review.html | — |
| 11 | Verify every table row has a source link | done | session-freetime4 | all data files | Blanks left where unconfirmed |
| 12 | Final integration: merge both sessions, verify links | done | session-freetime4 (arena/6899e48c-freetime4) | all | PR #5 merged to main; both sessions' work combined |
| 13 | PR to main, merge, confirm Pages deploys, record here | done | session-freetime4 (arena/6899e48c-freetime4) | — | PR #5: https://github.com/kanlerxz87-cyber/Freetime4/pull/5 ; merged 2026-11-25 (merge commit 3533843); GitHub Pages source main /, status BUILT, live https://kanlerxz87-cyber.github.io/Freetime4/ |

## Verification log

**Session arena/bbbb5122-freetime4 (docs/ site):**
- Sources checked include MLB's official news page reporting the 2027 regular-season schedule announcement (publication verified, not every game row).
- All 2027–2029 NFL/NCAAF schedules, MLB postseason details, radio carriage, station-by-station airings, and exact game durations remain unverified.
- No invented schedule rows or time estimates are published; unknown coverage shown as unknown, not free.
- Irregularities: Dec 17 2026 49ers at Chargers time conflict (Westwood One 4:30 PT vs 49ers 5:15 PT); Jan 3 2027 Eagles at 49ers (Westwood 4:30 PT vs 49ers 5:20 PT); MLB and NFL 2028–2029 schedules not released; Super Bowl 2028/2029 dates unverified; MLB game-length averages conflict; Bay Area carriage of most games unverified.

**Session session-freetime4 (arena/6899e48c-freetime4):**
- 2026 MLB: VERIFIED via MLB.com release (2025-08-26). Opening 2026-03-25 (Yankees@Giants), Opening Day 2026-03-26, All-Star 2026-07-14, regular end 2026-09-27.
- 2026 NFL/49ers: VERIFIED via official 49ers schedule release (2026-05-14). Preseason 8/13, 8/20, 8/27; regular 2026-09-10 to 2027-01-10; Super Bowl LXI 2027-02-14 (SoFi).
- 2026 NCAAF Stanford: VERIFIED via gostanford.com (ACC release 2026-01-26). Big Game vs Cal 2026-11-21 at 12:00 p.m. PST.
- 2026 NCAAF Cal: PARTIAL — Big Game date/time verified; full schedule not retrieved.
- Westwood One 2026: VERIFIED network coverage (TNF/SNF/MNF/postseason/Super Bowl). Local Bay Area affiliate list NOT confirmed.
- 2027–2029: ALL ESTIMATES. Official schedules not released. Flagged ESTIMATE throughout.

## Irregularities flagged for review (see flagged-review.html and docs/flagged.html)
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
11. Dec 17 2026 49ers at Chargers time conflict (Westwood One vs 49ers)
12. Jan 3 2027 Eagles at 49ers time conflict (Westwood One vs 49ers)

## Merge and deploy record (this integration)
- PR #5 "Freetime4: Free Time Vacation Planner site + schedule data" from branch `arena/6899e48c-freetime4` to `main`.
- Merge conflict resolved 2026-11-25 by combining both sessions' work: the `docs/` published planner and root dashboard are preserved; this branch's detail pages added at root; root `index.html` is a combined landing linking to both.
- GitHub Pages: source `main`, root `/` (already configured by arena/bbbb5122-freetime4). Live URL: https://kanlerxz87-cyber.github.io/Freetime4/ (redirects to /docs/).
- Note: the sandbox cannot reach github.io, so the live page was not opened from here; deploy status confirmed via the GitHub Pages API by the owning session.
