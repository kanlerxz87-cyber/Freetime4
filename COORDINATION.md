# Coordination board

Session: `arena/0452200e-freetime4` (active)

| Task | Status | Owner | File scope |
|---|---|---|---|
| Initial requirements audit, executive summary, static dashboard and flagged-items register | done | arena/0452200e-freetime4 | `index.html`, `styles.css`, `app.js`, `README.md`, `COORDINATION.md`, `.nojekyll` |

## Verification log

- Scope claim recorded 2026-11-25. Repository initially contained only `README.md`; no other claims or coordination board existed.
- Sources checked: MLB's official news page reporting publication of the 2027 regular-season schedule: https://www.mlb.com/news/mlb-2027-schedule-released (search excerpt on 2026-11-25). It states the regular-season date range and identifies a schedule link. This verifies publication/existence, not every individual game row or broadcast time.
- All 2027–2029 NFL/NCAAF schedules, MLB postseason details, radio carriage, station-by-station airings, and exact game durations remain unverified until linked to authoritative schedule/broadcast sources. No invented schedule rows or time estimates are published.
- Implementation review: HTML contains direct HTTPS source links for every competition-category row; date controls only alter the selected date and explicitly preserve an unknown availability state. The dashboard is plain static HTML/CSS/JS and requires no build tool.

## Irregularities / limitations

- A complete, line-by-line official event feed cannot be responsibly populated from the repository's initial contents. The dashboard explicitly distinguishes official schedule publication from verified per-game entries.
- 2028–2029 schedules and radio affiliations are not asserted as released/confirmed here. User's desired schedule horizon is not itself evidence that those schedules exist.
- “Free” is intentionally not concluded from missing data; unknown coverage is shown as unknown, not as a free window.

---

# Session arena/bbbb5122-freetime4 (Free Time Vacation planner, published from docs/)

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

- Merge note: main (PR #1, session arena/0452200e-freetime4) already had a root-level dashboard (index.html, app.js, styles.css). It was kept unchanged. This session's site is in docs/ and is the one published by GitHub Pages (main, /docs). The root dashboard is not deleted; it is noted as a separate page that the integration session may fold in later.

## Integration note (arena/bbbb5122-freetime4, final integration)

- GitHub Pages source is main, root (/). The integration token cannot change it to /docs (HTTP 403), so the root index.html now redirects to docs/index.html (the planner).
- The earlier root dashboard was COPIED (not deleted) to legacy-dashboard/ (index.html, styles.css, app.js). Its original files at root remain. The owning session (arena/0452200e-freetime4) should confirm this change.
- Live URL: https://kanlerxz87-cyber.github.io/Freetime4/ (redirects to /docs/).

## Merge and deploy record (arena/bbbb5122-freetime4)

- PR #2 "Free Time Vacation planner site + verified data": merged to main (merge commit 44a63de), 2026-11-25.
- PR #3 "Make planner the live landing page (root redirect to docs/)": merged to main (merge commit 08f851b), 2026-11-25.
- GitHub Pages: source main / (root); status "built" for commit 08f851b at 2026-11-25T13:54:06Z. Live URL: https://kanlerxz87-cyber.github.io/Freetime4/ (redirects to docs/index.html).
- Caveat: the sandbox cannot reach github.io, so the live page was not opened from here. The deploy status was confirmed via the GitHub Pages API only.
- Open items (not blocking, see Flagged for Review): full 30-club MLB schedule; full Giants and Athletics 2026-2027 schedules; radio carriage for Cal, Athletics, and most Westwood One games; 2028 and 2029 schedules once released.
