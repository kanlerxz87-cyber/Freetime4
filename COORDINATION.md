# COORDINATION — shared task board

Repo: `kanlerxz87-cyber/Freetime4` · Project: **FREE TIME VACATION** (Bay Area / 94122 radio-sports free-time planner)

> Read this before starting work. Claim a task by writing your session ID + file scope, commit,
> and push the claim **immediately**. Never start a task another session has claimed.
> Shared outputs (`data/games.json`, `site/index.html`, nav) are changed only by the integration session.

## Sessions

| Session ID | Branch | Started | Notes |
|---|---|---|---|
| `arena-224e418b` | `arena/224e418b-freetime4` | 2026-11-25 | Sole session active this cycle. Ran the "integration" role as well because no other session had claims. |

## Task board

| # | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Coordination + repo skeleton | done | arena-224e418b | `COORDINATION.md`, `README.md` |
| T2 | Data collection pipeline (GitHub Actions, official sources) | done | arena-224e418b | `scripts/collect*.py`, `data/raw/**`, `.github/workflows/collect.yml` |
| T3 | MLB 2026/2027 schedule ingest + verification | done | arena-224e418b | `scripts/build_mlb.py`, `data/raw/mlb_*.json` |
| T4 | NFL 2026 schedule ingest (nfl.com weekly pages) | done | arena-224e418b | `scripts/build_nfl.py`, `data/raw/nfl_*.html` |
| T5 | NCAAF 2026 Stanford + Cal ingest | done | arena-224e418b | `scripts/build_ncaaf.py` |
| T6 | Westwood One national radio NFL slate ingest | done | arena-224e418b | `scripts/build_wwo.py` |
| T7 | Radio station / affiliate research (KNBR, KSAN, KGO, KKGN…) | done | arena-224e418b | `site/radio.html`, `data/radio-sources.json` |
| T8 | Free-time engine (minute-resolution, PST/PDT, game-length estimates) | done | arena-224e418b | `scripts/free_time.py` |
| T9 | Vacation-window analysis 2027 / 2028 / 2029 | done | arena-224e418b | `scripts/analyze.py`, `data/analysis.json` |
| T10 | Site build (landing + category subpages + calendar scoreboard) | done | arena-224e418b | `site/**` |
| T11 | Verification pass — every row has an official source link | done | arena-224e418b | `site/verification.html` |
| T12 | Flagged-for-review page | done | arena-224e418b | `site/flagged.html` |
| T13 | Final integration: merge, build, publish to GitHub Pages | done | arena-224e418b | `main`, PR |

## Log

### 2026-11-25 — arena-224e418b

**Environment finding (important):** the agent sandbox has **no outbound network** except GitHub.
All data collection therefore runs inside GitHub Actions (`.github/workflows/collect.yml`), which
commits raw responses to `data/raw/`. Every raw file records its exact source URL in
`data/collect-report.md`, so any line can be re-verified by re-running the workflow.

**Sources used (all official unless marked):**

| Source | What it gives | Verified |
|---|---|---|
| `statsapi.mlb.com` (MLB Official Stats API) | 2026 + 2027 full MLB schedule, all 30 clubs, all game types | yes |
| `nfl.com/schedules/<year>/by-week/week-N/` | 2026 NFL schedule incl. preseason + postseason | yes |
| `nfl.com` (Pro Bowl page) | Pro Bowl Games date | yes |
| `westwoodonesports.com/more/eventGrid?id=all` | Westwood One national NFL radio broadcast list | yes |
| `gostanford.com` / `calbears.com` (official athletics, oas payload) | 2026 NCAAF schedules (12 games each) | yes |
| ESPN site API | cross-check only — **not** treated as official | n/a |

**Irregularities logged** (published on the *Flagged for Review* page):

1. `nfl.com/schedules/2027/...` returns HTTP 200 and a 2027 page title, but the rendered schedule
   body is the **2026** slate (identical byte-for-byte to the 2026 page). Same for `2028`, `2029`.
2. `api.nfl.com` returns **401** without credentials — not usable as a public source.
3. `49ers.com/schedule/2027/` is labelled **"49ers Historical 2027 Schedule"** and contains no games.
4. Stanford and Cal publish **only** the current season; `?season=2027` returns the 2026 payload.
5. MLB Stats API returns an **empty** schedule for 2028 and 2029 (not yet released). MLB 2027 **is** released.
6. WWO event grid timestamps are given in **ET**; converted to Pacific for all site output.
7. NFL.com's 2026 postseason page does not expose individual games in the by-week URL scheme; the
   `post-season` page was used instead.

No other agent session had a live claim during this cycle, so this session also performed the
integration step (T13) and published from `main`.

## Merge / deploy record

- Branch: `arena/224e418b-freetime4` → PR → `main` (command + result recorded at the end of the run).
- GitHub Pages: source = `main` / `/` (verified `.nojekyll` + `index.html` at repo root).
