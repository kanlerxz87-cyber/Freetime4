# VERIFY.md — line-by-line verification record (T4, session arena-ad020434, 2026-11-25)

Standard applied (per brief): every table row on the site carries a source link to an official
league/team/broadcaster page; a row is marked `verified` only if its value was read on an official
source in this session; unconfirmed values are blank/TBD or labeled `est / unverified` and listed
on the Flagged for Review page. No value is inferred silently.

## What was verified line-by-line

| Dataset | Rows | Verification performed | Result |
|---|---|---|---|
| MLB 2027 (regular season) | 2,430 | Pulled game-by-game from MLB's official Stats API (the data behind mlb.com/schedule), per-month raw dumps preserved in `data/raw/mlb_2027_*.json`; release dates cross-checked against MLB's official release article (Opening Night 2027-03-24, Opening Day 2027-03-25, season end 2027-09-26, ASG 2027-07-13). Spot-checked 2027-04-01 row set directly against the API response (8 games: Toronto@Baltimore 17:35Z etc. — all match). | All rows `verified=true`; rows with `startTimeTBD` carry `timeEstimated=true` (F03) |
| MLB 2027 spring training | 469 | Same official API (gameType S); first spring dates 2027-02-19 present in official feed | `verified=true` |
| MLB 2027 All-Star + exhibitions | 6 | Official API (gameType A/E); Derby/ASG dates cross-checked vs MLB release | `verified=true` |
| MLB 2027 postseason | 8 window rows | MLB has not announced dates (release says TBA) → windows modeled on the 2026 postseason from the official API (`data/raw/mlb_2026_10.json`) | `verified=false`, labeled ESTIMATE (F02) |
| MLB 2028–2029 | 731 slate rows | Official API returns **empty** for these seasons (evidence in `data/raw/mlb_2028_*.json`, `mlb_2029_*.json`); daily slate rows modelled over estimated season spans — **no invented matchups** | `verified=false`, labeled ESTIMATE (F04) |
| NFL 2026 weeks 12–18 | 63 rows | Week 12 read row-by-row on nfl.com (official) — every game/time matches. Weeks 13–18 cross-checked against ESPN public scoreboard with the official nfl.com by-week page attached per row | Wk12 `verified=true`; Wk13–18 `verified=false` (F06) |
| NFL 2026–27 postseason | 16 window rows | Round dates cross-checked via ESPN scoreboard dump (WC 2027-01-16→18, Div 01-23→24, CC 01-31, SB 02-14); Super Bowl date/venue verified on the official LA host committee site | SB row `verified=true`; others window-estimated |
| Super Bowl LXI | 1 | lasuperbowlhc.com + LASEC official announcement: 2027-02-14, SoFi Stadium | `verified=true`; kickoff flagged est (not published) |
| Westwood One national windows (2026–27) | 35 rows | Read event-by-event on westwoodonesports.com/nfl-schedule (official) incl. event-page URLs; ET→PT conversion re-derived per row | `verified=true` (times are broadcast starts — F07) |
| Stanford NCAAF 2026 | 3 remaining rows | gostanford.com schedule page not machine-readable in this sandbox (bot protection) → ESPN cross-check + Big Game date previously verified on gostanford.com by session 6899e48c | `verified=false` (F09) |
| Cal NCAAF 2026 | 1 remaining row | calbears.com/sports/football/schedule/2026 read directly this session (Nov 28 vs Pittsburgh, 4:30 PM — official) | `verified=true` |
| Possible Stanford bowl | 1 row | Record-based possibility only | `verified=false`, `blocking=false` (F10) |
| Stanford/Cal 2027–2029 | 156 rows | Not released (ESPN returns empty schedules) → Saturdays marked “game likely” conservatively | `verified=false`, ESTIMATE (F16) |
| NFL 2027–2029 | 314 rows | Not released; ESPN future-season calls return 2026 fallbacks (validated and discarded) → weekly window model | `verified=false`, ESTIMATE (F05) |
| Radio carriage rows | 8 stations | KNBR/KNBR-FM/KTCT/KSFO/KSAN affiliations via official 49ers.com + Westwood One station finder + Wikipedia station pages; A's Bay Area carriage via Sacramento Bee/ABC10 (team-announced flagship); Warriors via nba.com | each row shows its own verified flag; Cal flagship unconfirmed (F11) |
| Durations | 7 values | Researched averages with source links (MLB 2:38 per MLB pace-of-play reporting; NFL 3:12; NCAAF 3:24) | published averages flagged where estimated (F14) |

## Checks performed on the built site
1. **Internal link check** — every `href`/`src` in every published `.html` resolved against the repo tree (script `scripts/check_links.py`); result recorded in the run log: 0 broken internal links.
2. **JSON schema check** — every event row contains `date`, `source`, `verified`, `label`, `durMin`; no row has an empty source (script asserts this).
3. **Spot re-verification** — 2027-04-01 MLB rows re-compared against a fresh Stats API response read on the official endpoint; all 8 games match (teams, venues, times).
4. **Estimate labeling audit** — grep confirms every non-verified row renders the `est / unverified` badge path (`verBadge`), and every `certain:false` row appears in the UI with "possible/est" treatment.

## Exceptions (nothing here is presented as verified)
- F01 MLB CBA/lockout risk (the big one) — 2027 schedule is official but contingent.
- F03 2027 MLB games with `startTimeTBD` — time values estimated, flagged per row.
- F06 NFL weeks 13–18 — cross-check only, official link per row.
- F09 Stanford 2026 rows — cross-check only.
- All 2027+ NFL/NCAAF and 2028+ MLB rows — estimates, permanently labeled.

## Prior-session claims inherited
- Session 6899e48c's verification of the 2026 Stanford Big Game date (gostanford.com) is carried into F09's note.
- Session bbbb5122's Westwood One vs 49ers.com time discrepancies are preserved as F07.
