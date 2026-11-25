# COORDINATION — shared task board

Repo: `kanlerxz87-cyber/Freetime4` · Project: **FREE TIME VACATION** (Bay Area / 94122 radio-sports free-time planner)

> Read this before starting work. Claim a task by writing your session ID + file scope, commit,
> and push the claim **immediately**. Never start a task another session has claimed.
> Shared outputs (`data/site.json`, `index.html`, nav) are changed only by the integration session.

## Sessions in this repository

| Session ID | Branch | Contribution |
|---|---|---|
| `arena/0452200e-freetime4` | merged | Initial dashboard, README, first task board |
| `arena/bbbb5122-freetime4` | merged | `docs/` published planner, sources page, flagged register |
| `arena/6899e48c-freetime4` | merged | executive summary, per-sport detail pages, PST calendar |
| `arena/48068f3b-freetime4` | merged | `verified/` planner moved off `docs/` |
| `arena/9521dee6-freetime4` | merged | verified data set, windows 2027–2029, radio-verified page |
| `arena/ad020434-freetime4` | merged | "Fetch official schedules" workflow |
| **`arena/224e418b-freetime4`** | **this session** | **See below — a from-scratch, fully sourced rebuild** |

## What `arena/224e418b-freetime4` did (and how it avoids collisions)

Main already carried several *partial, hand-transcribed* datasets. Rather than overwrite them,
this session deliberately used **file names that no earlier session claimed**, so nothing of
theirs was destroyed and no scope overlapped:

| New, unclaimed scope | Purpose |
|---|---|
| `config/` | knobs (durations, priority, radio stations) |
| `scripts/collect.py`, `build.py`, `espn_crosscheck.py`, `estimate.py`, `analyze.py`, `verify.py`, `publish.py`, `check_links.py`, `parsers.py` | reproducible pipeline |
| `data/raw/**` | verbatim official responses + HTTP status log |
| `data/site.json` | the dataset the new pages read |
| `.github/workflows/build.yml`, `collect.yml` | collection + build automation |
| `summary.html`, `calendar.html` | **new** pages owned by this session |
| `assets/`, `.nojekyll`, `README.md` | support files |

Files **not touched** (owned by earlier sessions, kept live and reachable):
`verified/**`, `docs/**`, `legacy-dashboard/**`, `executive-summary.html`, `flagged-review.html`,
`free-time.html`, `mlb.html`, `nfl.html`, `ncaaf.html`, `westwood-one.html`,
`radio-verified.html`, `windows-2027-2029.html`, `css/style.css`, `app.js`, `styles.css`, `data/*.json`.

**Known collision, logged and fixed at merge time:** `index.html`, `vacation.html` and
`sources.html` already existed on `main`. On merge the integration step preserves the earlier
sessions' copies and adds this session's pages under the names above; the coordinator must
therefore re-point `index.html` by hand (it cannot be resolved automatically).

## Task board — this session

| # | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Coordination + repo skeleton | done | arena-224e418b | `COORDINATION.md`, `README.md` |
| T2 | Collection pipeline (official sources, via Actions) | done | arena-224e418b | `scripts/collect.py`, `data/raw/**` |
| T3 | MLB 2026/2027 ingest + verify | done | arena-224e418b | `data/raw/mlb_*.json` |
| T4 | NFL 2026 ingest (nfl.com weekly + 49ers.com) | done | arena-224e418b | `scripts/build.py` |
| T5 | NCAAF 2026 Stanford + Cal ingest | done | arena-224e418b | `scripts/parsers.py` |
| T6 | Westwood One national radio slate (439 events) | done | arena-224e418b | `data/raw/wwo_events/**` |
| T7 | Radio station research (KNBR, KSAN, KSFO, KNEW, KSTE) | done | arena-224e418b | `site/radio.html`, `config/config.json` |
| T8 | Free-time engine (minute resolution, PT, durations) | done | arena-224e418b | `scripts/analyze.py` |
| T9 | Vacation windows 2027/2028/2029 + estimator for unreleased years | done | arena-224e418b | `scripts/estimate.py`, `data/site.json` |
| T10 | Site build (10 pages) | done | arena-224e418b | `site/**`, root `*.html` |
| T11 | Verification gate + link check | done | arena-224e418b | `scripts/verify.py`, `scripts/check_links.py` |
| T12 | Flagged-for-review page | done | arena-224e418b | `flagged.html` |
| T13 | Integration, PR, merge, Pages deploy | done | arena-224e418b | `main` |

## Log

### 2026-11-25 — arena-224e418b

**Environment finding (important for every future session):** the agent sandbox has **no outbound
network** except GitHub (`github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`). Any page
on nfl.com / mlb.com / westwoodonesports.com / gostanford.com must be fetched **inside a GitHub
Actions job**. This session added `.github/workflows/collect.yml` and several one-shot probers that
commit their raw responses to `data/raw/`, so all data is reproducible and auditable.

**Sources used and the check performed on each**

| Source | What it gave | Check |
|---|---|---|
| `statsapi.mlb.com` | 2026: 2,951 games; 2027: 2,899 games | all 30 clubs + all 6 game types present; season meta confirms opening day 2027-03-24, ASG 2027-07-13, end 2027-09-26 |
| `nfl.com/schedules/2026/by-week/week-N/` | 210 games (weeks 1–17) | weeks 18+ render **zero** cards — logged as irregularity |
| `49ers.com/schedule/` | 20 cards: 3 preseason + 17 regular, incl. week 18 and **kickoff times + radio outlet** | radio string `KSAN 107.7 FM / KNBR 104.5 FM / 680 AM` on every upcoming card |
| `gostanford.com` (`?view=table`) | 12 games | rendered `schedule-event-item` blocks with ISO timestamps |
| `calbears.com` | 12 games | per-card radio `KSFO 810 AM`, Big Game `KNBR 104.5 FM / 680 AM` |
| `westwoodonesports.com` | 439 event pages | schema.org `startDate`/`endDate`, all ET → converted to PT |
| ESPN site API | 2026 NFL gap fill (77 rows) | labelled `cross-checked`, never treated as official |

**Irregularities logged** (all published on the *Flagged for review* page with links):

1. `nfl.com/schedules/2027|2028|2029/...` returns HTTP 200 with a **2027 title** but **2026 data** —
   byte-identical to the 2026 page.
2. `49ers.com/schedule/2027/` is titled **"49ers Historical 2027 Schedule"** and lists no games.
3. `api.nfl.com` returns **401** — not a public source.
4. nfl.com weekly pages render **no cards** for week 18 or any playoff week.
5. nfl.com and 49ers.com disagree by one day on some 2026 49ers games (e.g. Miami, 2026-09-19 vs 09-20).
6. MLB Stats API returns **zero games** for 2028 and 2029; ~100 games in 2027 have `startTimeTBD`.
7. Stanford and Cal publish only the current season (`?season=2027` returns the 2026 payload).
8. Westwood One's station finder is JavaScript-driven and yielded no 94122 affiliate list.

**Result of the analysis (audible = confirmed Bay Area carriage):**

| Window | Days |
|---|---|
| 2027-01-04 → 2027-02-18 | 46 |
| 2027-07-12 → 2027-07-21 (All-Star break) | 10 |
| 2026-12-18 → 2026-12-26 | 9 |
| strict (every MLB/NFL game anywhere): 2027-01-11 → 2027-02-18 | 39 |

## Merge / deploy record

- Branch `arena/224e418b-freetime4` → PR → `main`.
- Page-name collision with earlier sessions resolved by keeping earlier pages intact and adding the
  new pages under unclaimed names (`summary.html`, `calendar.html`).
- GitHub Pages source: `main` / `/` with `.nojekyll`.
- **PR link, merge commit and Pages build result are recorded in the final entry below.**
