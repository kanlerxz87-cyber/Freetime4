# FREE TIME VACATION

When can you take a vacation and not miss a game you actually care about?

This repo answers that for **Outer Sunset, San Francisco (94122)** — a household where live
sport on an **AM/FM radio** is the thing worth staying home for.

**Live site:** https://kanlerxz87-cyber.github.io/Freetime4/

---

## What it does

* Tracks every broadcast that could be on a Bay Area radio dial:
  * **MLB** — all 30 clubs, spring training → World Series (Giants and Athletics flagged high priority)
  * **NFL** — every game, preseason → postseason (49ers high priority)
  * **NCAAF** — Stanford and California (both high priority)
  * **Westwood One** national radio — TNF, MNF, SNF, Thanksgiving, Christmas, Saturday
    doubleheaders, playoffs, plus their college football, soccer, baseball, lacrosse and golf
* Turns that into a **minute-resolution free/busy calendar** in Pacific time
* Finds the **longest stretches of clear days** — the actual vacation windows
* Answers “is a week / two weeks / three weeks possible?” for **2027, 2028 and 2029**
* Publishes a **day-by-day scoreboard** you can click through

## The headline result

| | Window | Days |
|---|---|---|
| **Audible** (what your radio hears) | 2027-01-04 → 2027-02-18 | **46** |
| **Strict** (every MLB/NFL game anywhere) | 2027-01-11 → 2027-02-18 | **39** |

The **January → mid-February dead zone** is the answer, and it repeats every year:
MLB spring training has not started, the NFL regular season is over, and college football
finished in early December. Outside it, the best you get is the 4–5 day **All-Star break**
or a 6-day gap between homestands.

## Two definitions of “busy”

| Mode | Counts |
|---|---|
| **Audible** | Only broadcasts an official page confirms on a 94122-receivable station: Giants (KNBR 680), Athletics (KNEW 960), 49ers (KSAN 107.7 / KNBR 104.5 / 680), Cal (KSFO 810 / KNBR). |
| **Strict** | Every MLB game (all 30 clubs), every NFL game, Stanford, Cal and every Westwood One national broadcast. Worst case. |

## Sources (all official; nothing invented)

| Source | Used for |
|---|---|
| [`statsapi.mlb.com`](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&gameTypes=R,F,D,L,W,P,S) | MLB 2026 + 2027 (2,951 / 2,196 games) |
| [`nfl.com/schedules`](https://www.nfl.com/schedules/2026/by-week/week-1/) | 2026 NFL weekly pages |
| [`49ers.com/schedule`](https://www.49ers.com/schedule/) | 49ers 2026 dates, kickoff times **and the radio outlet printed on each card** |
| [`gostanford.com`](https://gostanford.com/sports/football/schedule?season=2026&view=table) | Stanford 2026 |
| [`calbears.com`](https://calbears.com/sports/football/schedule) | Cal 2026 + per-game radio |
| [`westwoodonesports.com`](https://www.westwoodonesports.com/nfl-schedule/) | 439 national radio broadcasts with schema.org timestamps |
| ESPN site API | **cross-check only**, gap fill, labelled separately |

**2028 and 2029 are not released by anyone.** Those years appear as clearly-labelled
estimates (see the *Flagged for review* page). Opponents are never invented — a modelled
row only blocks the day it would occupy.

## Repo layout

```
config/config.json        knobs: durations, priority, radio stations (no code edits needed)
scripts/collect.py        fetches every official page (runs in GitHub Actions — the sandbox
                          has no outbound network except GitHub)
scripts/build.py          parses raw responses -> data/site.json
scripts/espn_crosscheck.py  fills 2026 NFL gaps, labels them "cross-checked"
scripts/estimate.py       models unreleased seasons, labels them "estimated"
scripts/analyze.py        free/busy minutes + vacation-window search
scripts/verify.py         build gate: fails on any invented or unsourced row
scripts/publish.py        copies the site to the repo root for GitHub Pages
data/raw/**               verbatim official responses + HTTP status log
site/**                   page sources (also published at the repo root)
*.html                    the published pages
```

## Rebuilding

```bash
python3 scripts/collect.py     # needs network; run in Actions
python3 scripts/build.py
python3 scripts/espn_crosscheck.py
python3 scripts/estimate.py
python3 scripts/analyze.py
python3 scripts/verify.py      # must print PASS
python3 scripts/publish.py
python3 scripts/check_links.py # must print PASS
```

`COORDINATION.md` is the shared task board for parallel agent sessions.

## Honest limitations

- Game lengths are **estimates** (MLB 165 min, NFL 192 min, NCAAF 206 min), cited on the site.
- **Stanford's 2026 radio outlet is blank** — the official page does not print one.
- **Westwood One's Bay Area affiliate is blank** — the station page is JavaScript-driven and
  returned no usable list, so national games only count in strict mode.
- Ticket-gated / streaming-only broadcasts are out of scope: this is about the radio.
