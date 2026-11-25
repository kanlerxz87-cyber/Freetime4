# Official-source audit & coverage notes

**Snapshot:** 2026-11-25 (UTC) · dashboard timezone: `America/Los_Angeles` · target radio market: San Francisco 94122.

This page records source decisions behind [`site/data/schedules.json`](../site/data/schedules.json). Links are to league, club, athletics, broadcaster, or primary schedule records. A source URL documents where a claim came from; it does not mean every date in a source is bundled into the dashboard.

## MLB

| Official source | Used for | Scope / caveat |
| --- | --- | --- |
| [MLB Stats API — 2027 schedule](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027) | 2027 regular-season game count and selected event/date checks | The checked annual response includes 2,430 regular-season games (2,905 across game types). The static site does **not** include the full slate or all Giants/Athletics games. The [Feb 19 spring-training query](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&date=2027-02-19&gameType=S) listed 17 games; only the day-level count is shown. 2028–29 regular-season queries returned zero rows at audit time; that is not evidence of an empty season. |
| [MLB future All-Star locations](https://www.mlb.com/all-star/future-locations) | 2027 All-Star host | Chicago / Wrigley Field is confirmed for July 13, 2027; start time remains TBD. |
| [MLB Field of Dreams announcement](https://www.mlb.com/press-release/release-mlb-to-return-to-field-of-dreams-in-2027) and [Stats API date query](https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&date=2027-08-12) | Red Sox–Royals special game | August 12, 2027; API lists 4:30 PM Pacific, MLB announced NBC Sports coverage. The location is Dyersville, Iowa. |
| [MLB 2028 All-Star announcement](https://www.mlb.com/news/release-mlb-awards-the-2028-all-star-game-presented-by-mastercard-to-the-san-francisco-giants) | San Francisco host status | Oracle Park is confirmed; the game date and start time were not confirmed in the checked source. |
| [How to watch every MLB team in 2026](https://www.mlb.com/news/how-to-watch-every-mlb-team-in-2026) | Current team broadcast and Athletics affiliate guide | Athletics list KSTE 650 AM (English) and KVMX 92.1/105.5 FM (Spanish); neither confirms a Bay Area English terrestrial affiliate. Do not reuse older KNEW/KTRB listings as current without a new official confirmation. |
| [Giants TV/radio](https://www.mlb.com/giants/schedule/tv) | Giants radio | Lists KNBR 680 AM / 104.5 FM and Spanish-language KSFN / KXZM frequencies. Affiliations can change by season. |
| [Athletics in-market streaming](https://www.mlb.com/athletics/fans/podcasts/in-market) | A's Cast / online option | Online audio is not a terrestrial AM/FM signal in 94122. |

## NFL & 49ers

| Official source | Used for | Scope / caveat |
| --- | --- | --- |
| [49ers 2026 schedule](https://www.49ers.com/schedule/2026/) | 2026 preseason/regular-season matchups, venues and official Pacific kickoff times where displayed | The reviewed page confirms the remaining 2026 schedule: Nov 29 Seattle (1:25 PM), Dec 6 at NY Giants (10 AM), Dec 13 Rams (1:25 PM), Dec 17 at Chargers (5:15 PM), Dec 27 at Chiefs (1:25 PM), Jan 3 Eagles (5:20 PM), and Week 18 at Arizona (date/time TBD). Completed-game kickoff times are left blank in the dashboard when not retained in the reviewed source extract. |
| [NFL 49ers team schedule](https://www.nfl.com/schedules/2026/by-team/san-francisco-49ers) and [NFL Week 18](https://www.nfl.com/schedules/2026/by-week/week-18) | Matchup cross-checks and Week 18 TBD | NFL week pages confirm matchup/date records; they do not supply a future 49ers Week 18 kickoff yet. |
| [NFL 2026–27 important dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates) | 2027 league postseason windows | Week 18 Jan 9–10; Wild Card Jan 16–18; Divisional Jan 23–24; Conference Championships Jan 31; Super Bowl LXI Feb 14 at SoFi Stadium. These are league-wide date windows, not 49ers fixtures or qualification claims. |
| [49ers TV/radio partners](https://www.49ers.com/fans/tv-radio) and [KNBR partnership](https://www.49ers.com/news/san-francisco-49ers-announce-multi-year-partnership-extension-with-cumulus-media-s-knbr) | 49ers radio | KNBR and KSAN 107.7 FM are listed for the 2026 season; re-check future seasons and game-by-game clearance. |
| [Westwood One NFL schedule](https://www.westwoodonesports.com/nfl-schedule/) | National NFL radio windows | Schedule time is ET network airtime converted to PT. It may precede kickoff; it is not a verified local start, station clearance, or end time. |
| [Westwood One 2025 NFL station finder](https://www.westwoodonesports.com/station-finder-source-nfl/) | Bay Area affiliate directory snapshot | KNBR/KTCT entries appear in a directory labeled 2025. Do not guarantee 2026–29 carriage or assume that every station carries every game. |

The official 2026 preseason game centers for [Titans–49ers](https://www.nfl.com/games/titans-at-49ers-2026-pre-1?tab=recap), [49ers–Chargers](https://www.nfl.com/games/49ers-at-chargers-2026-pre-2?tab=recap), and [49ers–Raiders](https://www.nfl.com/games/49ers-at-raiders-2026-pre-3?tab=recap), plus the [Rams–49ers opener](https://www.nfl.com/games/49ers-at-rams-2026-reg-1?tab=recap), were used to confirm final results and venues. Past kickoff values are not fabricated from the results.

The NFL 2027–29 schedule pages checked during research returned no team game rows. Opponent rotations and league calendar dates are not substitutes for a dated 49ers schedule.

## Stanford & Cal football

| Official source | Used for | Scope / caveat |
| --- | --- | --- |
| [Stanford 2026 football schedule](https://gostanford.com/sports/football/schedule) | 2026 matchups/results and Nov 28 game | Stanford is 6–5 as of the snapshot and hosts SMU Nov 28 at 12:30 PM Pacific. Bowl eligibility is not a bowl assignment. |
| [Cal 2026 football schedule](https://calbears.com/sports/football/schedule/2026) | 2026 matchups/results and Nov 28 game | Cal is 3–8 and hosts Pittsburgh Nov 28 at 4:30 PM Pacific. Cal lost the Nov 21 Big Game 44–28. |
| [Stanford 2027 ACC opponents](https://gostanford.com/news/2026/09/16/acc-announces-2027-conference-opponents) and [Cal 2027 ACC opponents](https://calbears.com/news/2026/9/16/california-football-announces-2027-conference-opponents) | 2027 conference opponent grids | Opponents/home-away are confirmed; most game dates and all kickoff times remain TBD. |
| [Cal 2027 nonconference announcement](https://calbears.com/news/2026/6/25/football-cal-announces-odu-sac-state.aspx) | Cal nonconference dates | Sacramento State Aug 28, Old Dominion Sep 11; Cal–UCLA Sep 4 is separately confirmed below. Times remain TBD. |
| [Cal–UCLA series dates](https://calbears.com/news/2024/7/10/football-cal-ucla-schedule-4-games-from-2026-29) | Four rivalry dates | Cal home Sep 5, 2026; at UCLA Sep 4, 2027; Cal home Sep 2, 2028; at UCLA Sep 15, 2029. Cal moved UNLV in 2026 and the Florida series was canceled. |
| [Stanford–Notre Dame dates](https://gostanford.com/news/2026/05/20/two-dates-added-to-notre-dame-rivalry) | Announced future games | Nov 27, 2027 at Stanford; Oct 14, 2028 at Notre Dame. Kickoff times remain TBD. |
| [Stanford–Boston College series](https://gostanford.com/news/2016/06/13/boston-college-series) | Historical series dates for review | The 2016 announcement listed Sep 2, 2028 at BC and Sep 15, 2029 at Stanford. These legacy dates conflict with or need revalidation against later ACC scheduling, so they are not used as confirmed calendar dates. |
| [2023 ACC grid — Cal](https://calbears.com/news/2023/10/30/acc-announces-conference-football-matchups-for-2024-30.aspx) and [2023 ACC grid — Stanford](https://gostanford.com/news/2023/10/30/acc-announces-football-schedule-model) | Provenance for old 2028–29 opponent grids | These were eight-game models; later ACC scheduling moved to nine conference games. They are displayed only as archived context, not current dated schedules. |
| [Stanford 2026 radio announcement](https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced) and [Cal 2026 football info guide](https://calbears.com/documents/download/2026/8/7/2026_Cal_Football_Info_Guide.pdf) | 2026 radio | Stanford: KNBR/KTCT 1050 AM. Cal: 810 AM and Varsity Network; call-sign branding conflicts with current Cal schedule pages, so frequency is retained with a warning. |

## Duration and station-clearing policy

- MLB's **2:38** is a 2025 average game-time reference, not a forecast for a specific 2027 game or an on-air end time. It is used only as a planning baseline.
- The NFL's **three-hour** value is a planning estimate with no verified official broadcast-duration average. A 60-minute regulation clock is not elapsed broadcast time.
- The 49ers advertise a three-hour pregame show and postgame coverage, but the reviewed source does not give a reliable postgame end time.
- Station pre-emption, network conflicts, signal reception in 94122, game overruns, and postgame sign-off are not guaranteed by the official schedules.

## Items explicitly not inferred

- No vacation window is called free or clear.
- No postseason appearance is assigned to the 49ers, Stanford, Cal, Giants, or Athletics.
- A zero-result future MLB API response is not treated as “no games.”
- A 2025 affiliate directory is not treated as a current contract.
- An opponent-only announcement is not given an invented date or kickoff.
- No broadcast end time is calculated as a fact from the planning baselines.
