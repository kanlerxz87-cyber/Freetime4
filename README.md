# Freetime4 — "Free Time" radio-sports calendar

A vacation-planning site for a Bay Area listener (outer Sunset, SF 94122) who wants to know when there is no live AM/FM sports broadcast to miss.

- **Tracked:** all 30 MLB clubs (Giants and Athletics high priority), NFL (49ers high priority; Westwood One national radio), Stanford and Cal football.
- **"Free"** means no tracked game on air. Times are Pacific (PST in winter, PDT in summer).
- **Verification rule:** every table row links an official source. Anything that cannot be confirmed is left blank and listed on the *Flagged for Review* page. Nothing is estimated or filled in.

## Layout

| Path | What it is |
|---|---|
| `data/src/*.csv` | Hand-transcribed source rows (each row has its official source URL). |
| `scripts/build.py` | Builds `data/*.json`, `docs/data/*.json` and all `docs/*.html`. Standard library only. |
| `scripts/check_site.py` | Checks internal links, that every table row has a source link, and that JSON parses. |
| `scripts/assets/` | Calendar script (`calendar.js`) and stylesheet (`site.css`), copied into `docs/assets/`. |
| `docs/` | The GitHub Pages site (served from `main` → `/docs`). |
| `COORDINATION.md` | Shared task board, log, and sources. |

## Rebuild

```bash
python3 scripts/build.py
python3 scripts/check_site.py
```

## Data sources

Official: MLB Stats API (`statsapi.mlb.com`), Westwood One (`westwoodonesports.com`), 49ers.com, gostanford.com, calbears.com, mlb.com. Secondary sources are labelled as such on the Sources page and are never the only basis for a verified value.
