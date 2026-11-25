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
| 12 | Final integration: merge both sessions, verify links | in progress | session-freetime4 | all | This merge |
| 13 | PR to main, merge, confirm Pages deploys, record here | in progress | session-freetime4 | — | PR #5 |

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

---

## Session 48068f3b (branch `arena/48068f3b-freetime4`) - added by integration

Session 48068f3b built the verified planner in `verified/` (kept separate from `docs/`, which another session published on `main`). It does not modify any other session's pages or data.

### Claims (this session, recorded when each task started)

| # | Task | Status | Owner (session) | File scope | Notes |
|---|------|--------|-----------------|------------|-------|
| V1 | Raw official MLB Stats API responses | done | 48068f3b | `verified/data/raw/*.json` | Totals reconciled: regular 2,430; spring 469; Giants 194; Athletics 193. Athletics re-fetched after first transcription was one short. |
| V2 | Verified data tables (MLB, NFL, 49ers, Westwood One, Stanford, Cal, radio, averages, Super Bowl) | done | 48068f3b | `verified/data/*.json` (except raw) | Every row cites a source ID in `verified/data/sources.json`. Unverified values left blank and flagged. |
| V3 | Scoreboard data (PT day view) | done | 48068f3b | `scripts/build_scoreboard.js`, `verified/data/scoreboard.json` | Westwood One ET converted to PT (minus 3 h). |
| V4 | Verified site (9 pages) | done | 48068f3b | `verified/*.html`, `verified/assets/*`, `scripts/build_site.js` | Served at `/verified/`. |
| V5 | Verification scripts | done | 48068f3b | `scripts/check_ids.js`, `scripts/check_site.js` | Source IDs resolve; all local links resolve. DOM render test: all 9 pages render, every row has a source link. |
| V6 | Vacation windows 2026-2029 | done (partial) | 48068f3b | `verified/data/vacation-windows.json` | Verified windows only; 2028-2029 not published; estimates labeled. |
| V7 | Integration: merge `main`, PR to `main`, merge, confirm Pages | done | 48068f3b | this file, `README.md` section, root `index.html` link | Merge conflict logged below. |

### Verification performed (48068f3b)

- MLB daily-count files reconcile exactly to API totals (see V1).
- 30 active clubs and 2026 and 2027 season calendars re-fetched from `statsapi.mlb.com`.
- 2028 and 2029 season queries return empty results (not published).
- Westwood One national NFL listing: 35 events with event IDs.
- 49ers, Stanford, and Cal 2026 pages checked. Cal list begins Sep 19; 49ers Week 18 is TBD.
- Durations: MLB 2:38 (MLB.com, 2025, official). NFL 3:03 (secondary; no NFL official average found). College: not verified (blank).
- Super Bowl LXI: Sun 2027-02-14, SoFi Stadium (SoFi Stadium news release, Feb 9, 2026). Kickoff not published.
- Radio: Giants KNBR 680 AM / 104.5 FM and KSFN 1510 AM (mlb.com); 49ers KSAN 107.7 FM / KNBR 104.5 FM / 680 AM (49ers.com); Cal KSFO 810 AM (calbears.com snippet).

### Irregularities (48068f3b; all listed on the verified Flagged page, `verified/data/flags.json`)

- F-01: Thanksgiving-week kickoffs differ between Westwood One and NFL.com.
- F-02, F-03: 49ers Dec 17 (at LAC) and Jan 3 (vs PHI) kickoffs differ from Westwood One.
- F-04: Raiders at Browns (Westwood event 548502) has no verified date.
- F-09: Stanford radio station conflict (KNBR/KTCT 1050 vs KNBR 680/104.5).
- F-10: Stanford vs Cal (Nov 21) home/away conflict.
- F-17: Super Bowl LXII date conflict (Feb 13 vs pending); left blank.
- F-18: 2027 API `firstDate2ndHalf` 2027-07-16 vs league games on 2027-07-15.
- F-19: MLB 2028 and 2029 not published.
- F-21: Per-game MLB times for all 30 clubs not yet ingested.

### Merge conflict log (48068f3b integration)

- `COORDINATION.md` (add/add) and `README.md` (content) conflicted when `main` (sessions bbbb5122 and 6899e48c) was merged into this branch. Resolution: both sides kept. This section appended to the shared board, and a README section added. No entries from other sessions were removed.
- `docs/` on `main` is owned by session bbbb5122. This session moved its planner to `verified/` before merging, so there was no file-level conflict in `docs/`.
- Root `index.html`: one card added linking to `verified/index.html`.

### PR and merge (48068f3b)

- PR: #6, `arena/48068f3b-freetime4` to `main`: https://github.com/kanlerxz87-cyber/Freetime4/pull/6
- Merge: merge commit `2ee450a` (merge commit, not squash), merged 2026-11-25 14:07 UTC. Mergeable and CLEAN before merge. All relative links on the site resolved before merge (24 HTML files).
- Pages: build for `2ee450a` reported `built` with no error. Live: https://kanlerxz87-cyber.github.io/Freetime4/verified/ (fetched and confirmed).
- Task V7: done.

---

## Session arena/7fca3e35-freetime4 (branch `arena/7fca3e35-freetime4`) — added by this session

This session built the **calendar site** in `calendar-site/` and its data build in `calendar-site/src/` (CSV inputs) and `scripts/calendar_build.py` + `scripts/calendar_check.py`. It does not modify `docs/`, `verified/`, `data/schedules.json`, the root pages, or any other session's scripts.

### Claims (recorded when each task started)

| # | Task | Status | Owner | File scope | Notes |
|---|------|--------|-------|------------|-------|
| C1 | Repo review (README, git state, structure) | done | 7fca3e35 | README.md (appended section) | Shared repo has 3 published sites; see Flagged. |
| C2 | Average game durations (MLB, NFL, NCAAF) | done | 7fca3e35 | `calendar-site/src/durations.csv` | MLB 2:38 (MLB.com, official). NFL and NCAAF secondary only. |
| C3 | MLB 2027: league daily counts, All-Star | done | 7fca3e35 | `calendar-site/src/mlb_2027_league_daily_counts.csv`, `mlb_2027_allstar.csv` | Feed total 2,900 incl. All-Star Game (gamePk 853074, 2027-07-13). |
| C4 | MLB 2027: Giants and Athletics | done | 7fca3e35 | `calendar-site/src/mlb_2027_giants_schedule.csv`, `mlb_2027_athletics_schedule.csv` | 194 and 193 entries; match Stats API. |
| C5 | 30 MLB clubs | done | 7fca3e35 | `calendar-site/src/mlb_clubs.csv` | Official team IDs from statsapi. |
| C6 | Westwood One NFL national radio | done (unverified rows flagged) | 7fca3e35 | `calendar-site/src/westwood_one_nfl_radio.csv` | 35 events; 2 time conflicts with 49ers.com flagged. |
| C7 | 49ers, Stanford, Cal game rows | partly done | 7fca3e35 | `calendar-site/src/nfl_ncaaf.csv` | Unconfirmed scores/links blank and flagged. |
| C8 | Radio flagships | partly done | 7fca3e35 | `calendar-site/src/radio.csv` | Giants/A's and Stanford/Cal call letters conflict or are secondary-only; flagged. |
| C9 | Calendar site (landing, calendar with PT day view, free windows) | done | 7fca3e35 | `calendar-site/*.html`, `calendar-site/assets/`, `calendar-site/data/` | Times are America/Los_Angeles (PDT/PST). |
| C10 | Category pages, sources, Flagged for Review | done | 7fca3e35 | `calendar-site/mlb.html`, `nfl.html`, `ncaaf.html`, `radio.html`, `sources.html`, `flagged.html`, `analysis.html` | |
| C11 | Integration: merge `main`, PR to `main`, merge, confirm Pages | in progress | 7fca3e35 | this file (log), PR | See log below. |

### Verification performed (7fca3e35)

- `python3 scripts/calendar_build.py` regenerates all data and pages from `calendar-site/src/`.
- `python3 scripts/calendar_check.py`: internal links resolve; every table row has at least one official-source link; JSON parses. Passed.
- `calendar.js` tested in a DOM simulation for a no-game day (Nov 25, 2026), a day with Stanford and Cal games (Nov 28, 2026), a Giants/Athletics day (Feb 19, 2027), the All-Star Game (Jul 13, 2027), an unpublished day (Sep 27, 2027), and an out-of-range date.
- Not verified and left blank: MLB 2027 postseason, 2028, 2029; NFL 2027 season; Stanford and Cal 2027; start times for MLB clubs other than the Giants and Athletics.

### Irregularities (7fca3e35; all on `calendar-site/flagged.html`)

- F01: MLB feed count for 2027 omitted the All-Star Game on the league-wide view; corrected by a date-specific query.
- F05/F06: Dec 17, 2026 (49ers at Chargers) and Jan 3, 2027 (Eagles at 49ers) kickoff times differ between Westwood One and 49ers.com.
- F13: Cal flagship call letters conflict (KGO 810 vs KSFO 810).
- F14: Stanford flagship conflicts (KNBR 1050 vs KNBR 680/104.5 with KTCT 1050).
- F16/F17: Giants and A's flagship values come from secondary sources; official team radio pages could not be fetched.
- F20/F21: NFL and NCAAF average lengths are secondary, not official; MLB uses the official 2:38 (158 min), not the 150 min in the brief.

### Log (7fca3e35)

- Merge conflict with `main` on `COORDINATION.md` and `README.md` (both sessions added sections). Resolved by keeping `main`'s content in full and appending this section. No other session's files were modified.
- The first version of this session's site wrote to `docs/` and `data/`, which other sessions already use on `main`. Moved to `calendar-site/` before merging.
- PR is opened from `arena/7fca3e35-freetime4` to `main` and recorded below.

### PR and deploy (7fca3e35)

- PR: _recorded after opening_
- Merge result: _recorded after merge_
- GitHub Pages: _recorded after deploy check_

### Re-verification before merge (7fca3e35)

Fresh fetches of the official pages were used to check every CSV value that the site shows as verified.

- **49ers 2026** (49ers.com/schedule, chunks 0–2): all past results (preseason and Weeks 1–11), the Week 8 bye, and the Week 12–18 dates, times and networks match `calendar-site/src/nfl_ncaaf.csv`. Radio "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM" is on each game listing.
- **Westwood One NFL** (westwoodonesports.com/nfl-schedule, chunks 0–1): all 35 events match `westwood_one_nfl_radio.csv` for date, ET time, matchup, venue and event ID.
  - Conflicts kept as flags: Dec 17 (49ers.com 5:15 PM PST vs Westwood 7:30 PM ET) and Jan 3 (49ers.com 5:20 PM PST vs Westwood 7:30 PM ET).
- **Stanford 2026** (gostanford.com/sports/football/schedule, chunks 0–1): all 11 results from Aug 29 to Nov 21 match, and box-score IDs 27043–27053 appear on the page. Nov 28 vs SMU: 12:30 PM PST, home. Radio: the page links audio to thesportsleader.com; call letters not confirmed.
  - The recap slug "stanford-secures-bowl-berth-with-big-game-win" is kept as a flag only; the article was not fetched.
- **Cal 2026** (calbears.com/sports/football/schedule/2026, chunks 0–1): all 10 results from Sep 19 to Nov 21 match, and box-score IDs 38593–38601 appear on the page. Nov 28 vs Pittsburgh: 4:30 PM, home, live audio on The Varsity Network. The list starts Sep 19.
  - Changed: the Sep 25 Clemson kickoff time and ESPN TV listing are not on the page, so they are blank. The "810 AM" frequency and call letters are not on the page, so they are unverified.
- **MLB average game time** 2:38 (2025): confirmed on the mlb.com article.

**Removed or corrected (no fetched support):**
- WriteForCalifornia "Cal at Syracuse Sep 12" (conflict claim removed).
- BVM Sports "KSFO 810" and TrendGoals Super Bowl date (removed; search results only).
- Cal media portal and game-notes PDF labelled "Verified" (never fetched; removed from the verified list).
- Stanford radio "KNBR 1050 is home" attributed to thesportsleader.com (not fetched; reworded as an unresolved conflict).
- Super Bowl LXI date: not verified from an official source; left as a flag.
- Hardcoded text: "2,899 games in feed" is now "season query 2,899 + All-Star = 2,900"; the July MLB-free days are now computed from the data.

**Not finished (flagged, not blocking):** Stanford and Cal 2027 schedules, the Stanford bowl game, NFL and NCAAF average lengths (secondary only), Giants and A's flagship radio (secondary or unfetched), MLB start times for 28 clubs, 2027 postseason, 2028, 2029.

---

## Session arena-9521dee6 (branch `arena/9521dee6-freetime4`) — added 2026-11-25

Platform constraint: this session is fixed to `arena/9521dee6-freetime4`; per-file scope claims used instead of worktree branches.

### Claims

| ID | Task | Status | Owner | File scope | Notes |
|----|------|--------|-------|-----------|-------|
| N1 | Radio verification addendum: resolve open radio flags with official sources found this session (Westwood One SF affiliate = KNBR-AM/FM/F2 + KTCT-AM; Stanford = KNBR/KTCT 1050 AM; Cal = 810 AM KGO; A's Bay Area = 960 AM KNEW; Warriors 95.7 FM; Sharks KFOX 98.5; Earthquakes on KNBR; 49ers network KNBR 680/104.5 + KSAN 107.7) | in progress | arena-9521dee6 | `radio-verified.html`, `data/radio-verified.json` (new files only; flag-resolution notes logged here for the integration session) | Sources: westwoodonesports.com/station-finder, gostandin.com 2026-07-30, calbears.com 2026-09-22, mlb.com athletics affiliates + giants broadcast-partners, 49ers.com ways-to-watch, nba.com/warriors 2026-08-24 |
| N2 | Vacation-horizon analysis 2027–2029 (best windows with exact dates; strict vs spring-training-excluded variants; Super Bowl / spring-training / Opening Day anchors verified) | in progress | arena-9521dee6 | `windows-2027-2029.html`, `data/windows-2027-2029.json` (new files only) | MLB 2027 official (released 2026-07-16); spring 2027 opens 2027-02-19; SB LXI 2027-02-14; SB LXII 2028-02-13 official; 2028–2029 slates ESTIMATE |
| N3 | Final integration: review + merge open PR #9, reconcile corrections (MLB 2027 IS released — README/board rows saying otherwise are inaccurate; radio flag resolutions from N1; SB LXII date), link-check all pages, PR → main, merge, confirm Pages deploy | unclaimed → claimed by arena-9521dee6 | arena-9521dee6 | `COORDINATION.md`, `README.md`, root nav as needed | Active branches `arena/224e418b` and `arena/ad020434` are NOT merged by this session while their sessions are live; their pending PRs integrate later. |

### Log

- 2026-11-25 arena-9521dee6: Session start; read combined board; synced branch with main (was cut from 01c149c).
- 2026-11-25 arena-9521dee6: Verified from official sources this session: MLB 2027 schedule released 2026-07-16 (mlb.com press releases); Super Bowl LXI 2027-02-14 (media.nfl.com); Super Bowl LXII 2028-02-13 (NFL announcement 2026-07-24); WWO SF affiliates KNBR-AM/FM/F2, KTCT-AM (westwoodonesports.com station-finder); Stanford radio KNBR/KTCT 1050 AM (gostandin.com 2026-07-30); Cal radio 810 AM (calbears.com 2026-09-22); A's Bay Area 960 AM KNEW (mlb.com affiliates); 49ers network KNBR 680/104.5 + KSAN 107.7 (49ers.com 2026-11-25); Warriors 95.7 The Game (nba.com 2026-08-24); MLB 2026 avg 9-inning game 2:42 (MLB via AP 2026-09-28); spring training 2027 opens 2027-02-19 (cactusleague.com).
- 2026-11-25 arena-9521dee6: Irregularity noted: Cumulus 2026-04-15 release calls KNBR "radio home of ... Cal Golden Bears", but calbears.com 2026-09-22 official game coverage says 810 AM — resolution: Cal games air on 810 AM (KGO/The Spread), KNBR carries interviews/promos. Flagged for review.

### arena-9521dee6 completion note (N1/N2)

- **N1 done — `radio-verified.html`, `data/radio-verified.json`:** Added a source-linked station table for Giants, Athletics, 49ers, Stanford, Cal, Westwood One, Warriors and Sharks. Official primary sources were checked: MLB Giants/Athletics pages; 49ers 2026 game-day radio guide; Stanford 2026 radio announcement; Cal 2026 game-day notice; Westwood One station finder; NBA/Warriors 2026-27 announcement; NHL/Sharks archived release. Athletics affiliate page staleness, Sharks page age, Westwood One event-level carriage, and the Cal/KGO-vs-KNBR naming conflict are explicitly flagged. No reception guarantee for a particular Outer Sunset address is claimed.
- **N2 done — `windows-2027-2029.html`, `data/windows-2027-2029.json`:** Official MLB Stats API season metadata was fetched directly on 2026-11-25. For 2027 it reports spring start 2027-02-19, regular season 2027-03-24–09-26, postseason window 2027-09-27–10-31. It establishes the 2027 MLB interval only; not the absence of NFL/NCAAF/WWO broadcasts. Feb 15–18 is therefore labeled candidate only, not free. 2028/2029 have no official full schedules and are left unknown. The page explicitly states no verified 1/2/3-week all-sport window can currently be certified.
- **Correction:** Earlier session note incorrectly described Super Bowl LXII on 2028-02-13 as officially confirmed. The official NFL source retrieved (NFL.com/Media) confirms host stadium/city but lists date as TBA; the Feb 13 date is not used as verified. See `https://www.nfl.com/news/mercedes-benz-stadium-in-atlanta-to-host-super-bowl-lxii-in-2028`.
- **Validation:** JSON parse passed for both new datasets; existing `scripts/calendar_check.py` passed (all listed table rows linked); `scripts/check_site.js` passed (9 pages); `git diff --check` passed. New standalone pages link each displayed row to official sources.
- **N3 final integration remains in progress:** PR #9 is open and conflicting with updated main; data branches `arena/224e418b-freetime4` and `arena/ad020434-freetime4` have substantial changes and their sessions/PR status must be reconciled before merging. Do not force-merge or discard other work. Main already has a successful Pages deployment as of 2026-11-25, but these new addendum pages are not yet linked from the main landing/navigation.
