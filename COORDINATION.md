# COORDINATION — Shared Task Board (Freetime4)

Protocol: each task lists its status (`unclaimed`, `in progress`, `done`, `needs review`), the owning session, and the files it touches. Claims are committed and pushed immediately. `needs review` items are published on the **Flagged for Review** page and do not block anything.

**Branch note:** the platform fixes this session to one branch, `arena/7fca3e35-freetime4` (branched from `main` @ `01c149c`). The `session-<id>/<task>` branch convention cannot be used here, so every task below is handled by this single session on this branch. Owning session: `arena/7fca3e35-freetime4`.

**Scope note:** the sandbox can only reach GitHub, npm and PyPI directly. All official-source data (MLB Stats API, Westwood One, team sites) is reached through the fetch tool, so every value is transcribed by hand into `data/src/*.csv`. Each CSV row carries its official source URL. Anything not confirmed is left blank and flagged.

**Scope change (logged):** `data/src/`, `scripts/` and `README.md` were added to this session's file scope after the original claim. They are the raw inputs and the build that produces the outputs listed below.

| # | Task | Status | Owner | Files touched |
|---|------|--------|-------|---------------|
| T1 | Repo review (README, git state, structure) | done | arena/7fca3e35-freetime4 | README.md, docs/flagged.html (F23, F24) |
| T2 | Research: average game durations (MLB, NFL, NCAAF) | done | arena/7fca3e35-freetime4 | data/src/durations.csv, data/durations.json (F20, F21) |
| T3 | MLB data: league-wide daily game counts 2027 | done (correction F01) | arena/7fca3e35-freetime4 | data/src/mlb_2027_league_daily_counts.csv, data/src/mlb_2027_allstar.csv, data/mlb_daily_counts_2027.json |
| T4 | MLB data: Giants & Athletics game-level schedule 2027 | done | arena/7fca3e35-freetime4 | data/src/mlb_2027_giants_schedule.csv, data/src/mlb_2027_athletics_schedule.csv, data/mlb_giants_athletics_2027.json (F03) |
| T5 | MLB: all 30 clubs listed with official team IDs | done | arena/7fca3e35-freetime4 | data/src/mlb_clubs.csv, data/mlb_clubs.json |
| T6 | NFL: Westwood One national radio schedule (Nov 2026 – Jan 2027) | done (re-fetched and regenerated) | arena/7fca3e35-freetime4 | data/src/westwood_one_nfl_radio.csv, data/westwood_nfl_radio.json (F05, F06, F08, F09) |
| T7 | NFL/NCAAF: 49ers, Stanford, Cal game-level data (2026 remaining) | done | arena/7fca3e35-freetime4 | data/src/nfl_ncaaf.csv, data/nfl_ncaaf.json (F07, F11, F12, F15, F25) |
| T8 | Radio: flagship stations for each team / Westwood One | done (partial, see flags) | arena/7fca3e35-freetime4 | data/src/radio.csv, data/radio.json (F13 to F19) |
| T9 | Site: landing dashboard, scoreboard calendar, free-time engine | done | arena/7fca3e35-freetime4 | scripts/build.py, scripts/assets/calendar.js, docs/index.html, docs/calendar.html, docs/analysis.html, docs/data/calendar.json |
| T10 | Site: category subpages, sources, flagged-for-review page | done | arena/7fca3e35-freetime4 | docs/mlb.html, docs/nfl.html, docs/ncaaf.html, docs/radio.html, docs/sources.html, docs/flagged.html, docs/assets/site.css |
| T11 | GitHub Pages enablement, deploy verification, PR, merge | in progress | arena/7fca3e35-freetime4 | (repo settings, PR) |

## Log

- Session `arena/7fca3e35-freetime4` claimed T1–T11 on this branch. Starting with an empty repo (README only, no prior code or data).
- Pulled and checked the MLB Stats API for Giants (194 entries) and Athletics (193). Sum of 2027 league counts matched the API total (2,899). Head-to-head games agree across both team files.
- Re-fetched the Westwood One NFL page (2 chunks). Regenerated the 35-event list from the fetched text. Time conflicts with 49ers.com (Dec 17, Jan 3) are flagged, not resolved.
- Found that the feed count omitted the 2027 All-Star Game (gamePk 853074, gameType A, 2027-07-13). Added it from the date query. Correction recorded as F01. Season total becomes 2,900.
- Confirmed the 2027-07-12 and 2027-07-14 MLB-free days. Jul 13 is not free (All-Star).
- MLB Nov 2026 to Dec 2026 and Jan to Feb 18 2027 show zero games in the Stats API. Verified MLB-free window: Nov 25, 2026 to Feb 18, 2027 (86 days).
- Radio: the official Giants and A's radio pages could not be fetched. Those flagship values are secondary and flagged (F16, F17). Stanford flagship sources conflict (F14). Cal call letters conflict (F13).
- Build: `python3 scripts/build.py` produces all JSON and HTML. `python3 scripts/check_site.py` checks internal links, source links on every table row, and JSON validity. Both passed.
- Calendar tested in a DOM simulator on a no-game day, a Giants/Athletics day, the All-Star date, an unpublished date, and an out-of-range date. Output matched expectations.

## Sources (official unless marked)

Full list with status on the **Sources** page. Official sources used for verified values:

- MLB Stats API: `statsapi.mlb.com` (teams, seasons, 2027 schedule, team schedules, All-Star date query, 2026 Nov–Dec query, 2028 query).
- mlb.com 2025 average game time (2:38): https://www.mlb.com/news/mlb-increased-attendance-3rd-straight-season
- Westwood One NFL schedule: https://www.westwoodonesports.com/nfl-schedule/ and station finder: https://www.westwoodonesports.com/station-finder/
- 49ers schedule: https://www.49ers.com/schedule/
- Stanford football schedule: https://gostanford.com/sports/football/schedule
- Cal football schedule: https://calbears.com/sports/football/schedule/2026 and media portal: https://calbears.com/sports/2026/8/6/2026-california-football-media-portal and game notes: https://calbears.com/documents/download/2026/9/15/26FB_Cal-GameNotes_WAGNER.pdf

Secondary (labelled, never the only basis of a verified value): nflanalytic.com (NFL length), academicjobs.com (NCAAF length), insideradio.com (Stanford radio), sacbee.com (A's radio), visualfoodie.com (Giants radio), lasuperbowlhc.com (Super Bowl LXI).

## Pull request and deploy

- PR: https://github.com/kanlerxz87-cyber/Freetime4/pull/7 (arena/7fca3e35-freetime4 → main)
- Merge result: _pending_
- GitHub Pages: _pending_
