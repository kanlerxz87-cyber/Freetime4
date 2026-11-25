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
| 2 | Research: official 2026-27 NFL remaining schedule + 49ers + Westwood One radio slate | in progress | arena-edb54633-freetime4 | data/nfl_*.json, tools/ |
| 3 | Research: official MLB 2027 schedule (day map, Giants, A's, spring training) from MLB stats API | in progress | arena-edb54633-freetime4 | data/mlb_*.json, tools/ |
| 4 | Research: NCAAF Stanford/Cal 2026 results/bowls, 2027+ announced games, estimates | in progress | arena-edb54633-freetime4 | data/ncaaf_*.json |
| 5 | Research: Bay Area AM/FM radio stations receivable in 94122 (flagships + Westwood One affiliate) | in progress | arena-edb54633-freetime4 | data/radio_stations.json |
| 6 | Research: average game durations (MLB/NFL/NCAAF) for free-time math | in progress | arena-edb54633-freetime4 | data/meta.json |
| 7 | Estimate schedules 2027-2029 where no official release exists (flagged, never presented as verified) | unclaimed | arena-edb54633-freetime4 | data/estimates_*.json |
| 8 | Free-window analysis (1/2/3-week windows with zero games) 2026-2029 | unclaimed | arena-edb54633-freetime4 | data/windows.json, windows.html |
| 9 | Site build: landing page, scoreboard, category pages, flagged-for-review page | unclaimed | arena-edb54633-freetime4 | *.html, assets/ |
| 10 | Verification pass: every table row has official source link; estimates flagged | unclaimed | arena-edb54633-freetime4 | data/, *.html |
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
