# COORDINATION — Shared Task Board (Freetime4)

Protocol: each task lists its status (`unclaimed`, `in progress`, `done`, `needs review`), the owning session, and the files it touches. Claims are committed and pushed immediately. `needs review` items are published on the **Flagged for Review** page and do not block anything.

**Branch note:** the platform fixes this session to one branch, `arena/7fca3e35-freetime4` (branched from `main` @ `01c149c`). The `session-<id>/<task>` branch convention in the protocol cannot be used here, so every task below is handled by this single session on this branch. Owning session: `arena/7fca3e35-freetime4`.

**Scope note:** the sandbox can only reach GitHub, npm and PyPI directly. All official-source data (MLB Stats API, Westwood One, team sites) is reached through the fetch tool, so every data value has to be transcribed by hand. Anything not transcribed and verified is left blank and flagged.

| # | Task | Status | Owner | Files touched |
|---|------|--------|-------|---------------|
| T1 | Repo review (README, git state, structure) | in progress | arena/7fca3e35-freetime4 | COORDINATION.md, docs/flagged.html |
| T2 | Research: average game durations (MLB, NFL, NCAAF) | in progress | arena/7fca3e35-freetime4 | data/durations.json |
| T3 | MLB data: league-wide daily game counts 2027 (official MLB Stats API) | in progress | arena/7fca3e35-freetime4 | data/mlb_daily_counts_2027.json |
| T4 | MLB data: Giants & Athletics game-level schedule 2027 | in progress | arena/7fca3e35-freetime4 | data/mlb_giants_athletics_2027.json |
| T5 | MLB: all 30 clubs listed with official team IDs | in progress | arena/7fca3e35-freetime4 | data/mlb_clubs.json |
| T6 | NFL: Westwood One national radio schedule (Nov 2026 – Jan 2027) | in progress | arena/7fca3e35-freetime4 | data/westwood_nfl_radio.json |
| T7 | NFL/NCAAF: 49ers, Stanford, Cal game-level data (2026 remaining) | in progress | arena/7fca3e35-freetime4 | data/nfl_ncaaf.json |
| T8 | Radio: flagship stations for each team / Westwood One | in progress | arena/7fca3e35-freetime4 | data/radio.json |
| T9 | Site: landing dashboard, scoreboard calendar, free-time engine | in progress | arena/7fca3e35-freetime4 | docs/* |
| T10 | Site: category subpages, sources, flagged-for-review page | in progress | arena/7fca3e35-freetime4 | docs/* |
| T11 | GitHub Pages enablement, deploy verification, PR, merge | unclaimed | arena/7fca3e35-freetime4 | (repo settings, PR) |

## Log

- Session `arena/7fca3e35-freetime4` claimed T1–T11 on this branch. Starting with an empty repo (README only, no prior code or data).

## Sources (official unless marked)

Sources are recorded per task as work completes. See the Flagged for Review page for items that could not be verified.
