# COORDINATION.md — Shared Task Board

Multiple agent sessions may work on this repo. This file is the shared task board.
Claim a task by writing your session ID and file scope here, commit and push the
claim immediately, then work only inside that scope.

## Rules

- Never start a task another session has claimed.
- Keep scopes non-overlapping; log cross-file requests here instead of editing
  another session's files.
- Small, frequent commits; run `git pull --rebase` before every push.
- Record sources, verification performed, and irregularities here when a task is
  done. Never mark anything verified without checking an official source.
- Status values: `unclaimed`, `in progress`, `done`, `needs review`.
  `needs review` items are published on the site's "Flagged for Review" page and
  do not block anything.
- Shared outputs (table data, site index/navigation) change only in the final
  integration step, after all other tasks are done.
- A claim older than 60 minutes with no commits may be taken over; note the handoff.

## Platform constraint note

Arena sessions are bound to a single pre-assigned branch (this session: 
`arena/edb54633-freetime4`); the platform forbids creating/switching branches.
So the "session-<id>/<task>" branch naming is replaced by per-task scope claims
on this session branch, with all tasks done by the session that owns them.

## Session registry

| Session ID | Branch | Started (UTC) | Scope |
|---|---|---|---|
| arena-edb54633-freetime4 | arena/edb54633-freetime4 | 2026-11-25 | All tasks below (single-session build) |

## Task board

| # | Task | Status | Owner | Files touched |
|---|---|---|---|---|
| 1 | Coordination board setup | done | arena-edb54633-freetime4 | COORDINATION.md |
| 2 | Research: official 2026-27 NFL remaining schedule + 49ers + Westwood One radio slate | done | arena-edb54633-freetime4 | data/nfl/nfl_2026.csv, data/nfl.json |
| 3 | Research: official MLB 2027 schedule (day map, Giants, A's, spring training) from MLB stats API | done | arena-edb54633-freetime4 | tools/giants_2027.csv, tools/athletics_2027.csv, data/mlb_2027.json |
| 4 | Research: NCAAF Stanford/Cal 2026 results/bowls, 2027+ announced games, estimates | done | arena-edb54633-freetime4 | data/ncaaf.json |
| 5 | Research: Bay Area AM/FM radio stations receivable in 94122 (flagships + Westwood One affiliate) | done | arena-edb54633-freetime4 | data/radio.json |
| 6 | Research: average game durations (MLB/NFL/NCAAF) for free-time math | done | arena-edb54633-freetime4 | data/durations.json |
| 7 | Estimate schedules 2027-2029 where no official release exists (flagged, never presented as verified) | done | arena-edb54633-freetime4 | inside data/free_days.json (events with estimated=true) |
| 8 | Free-window analysis (1/2/3-week windows with zero games) 2026-2029 | done | arena-edb54633-freetime4 | data/free_days.json, data/vacation.json, vacation.html |
| 9 | Site build: landing page, scoreboard, category pages, flagged-for-review page | done | arena-edb54633-freetime4 | index.html + 6 subpages, assets/ |
| 10 | Verification pass: every table row has official source link; estimates flagged | in progress | arena-edb54633-freetime4 | data/, *.html |
| 11 | Final integration: re-verify combined data, link check, PR to main, merge, enable GitHub Pages, confirm deploy | unclaimed | arena-edb54633-freetime4 | all |

## Log

- 2026-11-25 arena-edb54633-freetime4: Repo was empty (initial commit 01c149c).
  Created board; claimed all tasks (no other sessions had claims at claim time).
- 2026-11-25 arena-edb54633-freetime4: Prior sites referenced by the user
  (buffedlizard55-lab GitHub Pages) are not publicly retrievable from this
  environment; building fresh from official sources.
- 2026-11-25 arena-edb54633-freetime4: Confirmed reachable official data sources:
  MLB stats API (statsapi.mlb.com) returns real 2027 MLB schedule (Opening Day
  2027-03-25 verified via API); westwoodonesports.com NFL schedule page returns
  the 2026-27 national radio slate. NFL schedules via nflverse/nfldata (open-data
  mirror of the official NFL schedule; will cite NFL.com for priority rows).

## Completion log (2026-11-25, session arena-edb54633-freetime4)

- Task 2 (NFL): 272 regular-season games transcribed from the official 2026 schedule
  (fixturedownload.com mirror of the NFL release; spot-verified vs NFL.com/schedules/2026/REG13
  and westwoodonesports.com). Machine checks: match numbers 1-272 complete, all 32 teams
  exactly 17 games, bye distribution sane. 26 of 27 WW1 broadcast entries auto-paired to feed
  games; 1 date mismatch (DEN@PIT feed 11/28 vs NFL.com+WW1 Fri 11/27) flagged. Week 16/17/18
  TBD-time anomalies flagged on site.
- Task 3 (MLB 2027): Giants and A's 162 regular games each, transcribed from statsapi.mlb.com
  team queries and machine-verified against the API's per-date lists (exact match, zero
  discrepancies - the previously suspected "Giants 160" anomaly was a hand-count error).
  Spring training 33 Giants / 31 A's games Feb 19-Mar 23; one home-id 105 unresolved flag.
  128 of 388 first-pitch times are league placeholders -> EST/TBD with typical-slot estimate.
- Task 4 (NCAAF): verified rows only (WW1 CFB, CFP dates, Cal 2027 non-conf, Stanford bowl TBD).
- Tasks 5/6 (radio, durations): data/radio.json + data/durations.json with sources.
- Tasks 7/8 (estimates + free windows): per-day busy intervals 2026-11-25..2029-12-31
  (1133 days) -> data/free_days.json; consecutive-free-day runs -> data/vacation.json
  (18 windows >= 3 days; prime 2-week candidates Feb 1-13 2027, Jan 31-Feb 12 2028,
  Jan 29-Feb 10 2029).
- Task 9 (site): index.html scoreboard + day navigator (yesterday/tomorrow/date picker,
  06:00-23:30 PT busy bar, exact free windows per day), mlb.html, nfl.html, ncaaf.html,
  radio.html, vacation.html, flagged.html - all vanilla JS over data/*.json, all rows
  carry source links. Headless render test passed (16/16 elements); local HTTP smoke test
  17/17 resources HTTP 200.
- Task 11 (integration): next - PR to main, merge, enable GitHub Pages, confirm deploy.
