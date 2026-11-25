# FreeTime4 — data build script
# Generates all data/*.json for the site from sources captured & verified 2026-11-25.
# Every embedded row carries its source. Estimates are explicitly marked ESTIMATE.
#
# Sources:
#  - MLB official stats API (statsapi.mlb.com/api/v1/schedule) — 2027 day map, Giants (137),
#    Athletics (133), team-ID map, spring training. Query URLs in SOURCES below.
#  - Westwood One Sports (westwoodonesports.com) — NFL national radio schedule page + events,
#    NCAA football broadcasts, station finder (Bay Area affiliates).
#  - NFL 2026 schedule mirror (fixturedownload.com/feed/json/nfl-2026) — cross-checked against
#    NFL.com weekly schedule page (fetched REG13) and Westwood One broadcast times.
#  - Official announcements: Super Bowl LXI (LA Host Committee), LXII/LXIII (NFL via NBC/CBS),
#    CFP 2026-27 dates, Cal 2027 opponents (calbears.com), Stanford radio (gostanford.com).
import csv, json, os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")
UTC = timezone.utc

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

GEN_AT = "2026-11-25"

# ---------------------------------------------------------------- MLB team IDs
# From https://statsapi.mlb.com/api/v1/teams?sportId=1&fields=teams,id,name,league (fetched 2026-11-25)
MLB_TEAMS = {
    108: "Los Angeles Angels", 109: "Arizona Diamondbacks", 110: "Baltimore Orioles",
    111: "Boston Red Sox", 112: "Chicago Cubs", 113: "Cincinnati Reds",
    114: "Cleveland Guardians", 115: "Colorado Rockies", 116: "Detroit Tigers",
    117: "Houston Astros", 118: "Kansas City Royals", 119: "Los Angeles Dodgers",
    120: "Washington Nationals", 121: "New York Mets", 133: "Athletics",
    134: "Pittsburgh Pirates", 135: "San Diego Padres", 136: "Seattle Mariners",
    137: "San Francisco Giants", 138: "St. Louis Cardinals", 139: "Tampa Bay Rays",
    140: "Texas Rangers", 141: "Toronto Blue Jays", 142: "Minnesota Twins",
    143: "Philadelphia Phillies", 144: "Atlanta Braves", 145: "Chicago White Sox",
    146: "Miami Marlins", 147: "New York Yankees", 158: "Milwaukee Brewers",
}
GIANTS, ATHLETICS = 137, 133
PACIFIC_TEAMS = {108, 109, 119, 133, 135, 136, 137, 140}  # PT-zone clubs (home parks)

MLB_SOURCE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={tid}&startDate=2027-02-01&endDate=2027-10-31&fields=dates,date,games,gameDate,teams,away,team,id,home,team,id"
MLB_DAYMAP_SOURCE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-01-01&endDate=2027-12-31&fields=dates,date,totalGames"

# ------------------------------------------------------- MLB 2027 league day map
# Per-day total games (spring + regular + specials), official MLB stats API, fetched 2026-11-25.
# Zero-game dates are absent from the API response: 2027 zero-game dates = Jul 12, Jul 14.
MLB_2027_DAYMAP = [
    ("2027-02-19",17),("2027-02-20",16),("2027-02-21",16),("2027-02-22",16),("2027-02-23",15),
    ("2027-02-24",16),("2027-02-25",15),("2027-02-26",16),("2027-02-27",16),("2027-02-28",16),
    ("2027-03-01",12),("2027-03-02",9),("2027-03-03",13),("2027-03-04",14),("2027-03-05",16),
    ("2027-03-06",16),("2027-03-07",16),("2027-03-08",13),("2027-03-09",13),("2027-03-10",13),
    ("2027-03-11",13),("2027-03-12",16),("2027-03-13",17),("2027-03-14",16),("2027-03-15",12),
    ("2027-03-16",12),("2027-03-17",15),("2027-03-18",13),("2027-03-19",16),("2027-03-20",16),
    ("2027-03-21",14),("2027-03-22",13),("2027-03-23",7),("2027-03-24",1),("2027-03-25",14),
    ("2027-03-26",6),("2027-03-27",15),("2027-03-28",11),("2027-03-29",15),("2027-03-30",14),
    ("2027-03-31",15),("2027-04-01",8),("2027-04-02",12),("2027-04-03",15),("2027-04-04",15),
    ("2027-04-05",13),("2027-04-06",15),("2027-04-07",15),("2027-04-08",5),("2027-04-09",15),
    ("2027-04-10",15),("2027-04-11",15),("2027-04-12",4),("2027-04-13",15),("2027-04-14",15),
    ("2027-04-15",15),("2027-04-16",15),("2027-04-17",15),("2027-04-18",15),("2027-04-19",9),
    ("2027-04-20",15),("2027-04-21",15),("2027-04-22",9),("2027-04-23",15),("2027-04-24",15),
    ("2027-04-25",15),("2027-04-26",11),("2027-04-27",15),("2027-04-28",15),("2027-04-29",6),
    ("2027-04-30",15),("2027-05-01",15),("2027-05-02",15),("2027-05-03",13),("2027-05-04",15),
    ("2027-05-05",15),("2027-05-06",10),("2027-05-07",15),("2027-05-08",15),("2027-05-09",15),
    ("2027-05-10",5),("2027-05-11",15),("2027-05-12",15),("2027-05-13",12),("2027-05-14",15),
    ("2027-05-15",15),("2027-05-16",15),("2027-05-17",10),("2027-05-18",15),("2027-05-19",15),
    ("2027-05-20",9),("2027-05-21",15),("2027-05-22",15),("2027-05-23",15),("2027-05-24",9),
    ("2027-05-25",15),("2027-05-26",15),("2027-05-27",8),("2027-05-28",15),("2027-05-29",15),
    ("2027-05-30",15),("2027-05-31",15),("2027-06-01",15),("2027-06-02",15),("2027-06-03",4),
    ("2027-06-04",15),("2027-06-05",15),("2027-06-06",14),("2027-06-07",11),("2027-06-08",15),
    ("2027-06-09",15),("2027-06-10",7),("2027-06-11",15),("2027-06-12",15),("2027-06-13",15),
    ("2027-06-14",12),("2027-06-15",15),("2027-06-16",15),("2027-06-17",6),("2027-06-18",15),
    ("2027-06-19",15),("2027-06-20",15),("2027-06-21",12),("2027-06-22",16),("2027-06-23",14),
    ("2027-06-24",7),("2027-06-25",15),("2027-06-26",15),("2027-06-27",15),("2027-06-28",9),
    ("2027-06-29",15),("2027-06-30",15),("2027-07-01",12),("2027-07-02",15),("2027-07-03",15),
    ("2027-07-04",15),("2027-07-05",5),("2027-07-06",15),("2027-07-07",15),("2027-07-08",14),
    ("2027-07-09",15),("2027-07-10",16),("2027-07-11",15),("2027-07-13",1),("2027-07-15",1),
    ("2027-07-16",14),("2027-07-17",15),("2027-07-18",15),("2027-07-19",15),("2027-07-20",15),
    ("2027-07-21",15),("2027-07-22",7),("2027-07-23",15),("2027-07-24",15),("2027-07-25",15),
    ("2027-07-26",12),("2027-07-27",15),("2027-07-28",15),("2027-07-29",10),("2027-07-30",15),
    ("2027-07-31",15),("2027-08-01",15),("2027-08-02",7),("2027-08-03",15),("2027-08-04",15),
    ("2027-08-05",9),("2027-08-06",15),("2027-08-07",15),("2027-08-08",15),("2027-08-09",12),
    ("2027-08-10",15),("2027-08-11",15),("2027-08-12",6),("2027-08-13",14),("2027-08-14",15),
    ("2027-08-15",15),("2027-08-16",12),("2027-08-17",15),("2027-08-18",15),("2027-08-19",8),
    ("2027-08-20",14),("2027-08-21",15),("2027-08-22",15),("2027-08-23",9),("2027-08-24",15),
    ("2027-08-25",15),("2027-08-26",7),("2027-08-27",15),("2027-08-28",15),("2027-08-29",15),
    ("2027-08-30",8),("2027-08-31",15),("2027-09-01",15),("2027-09-02",9),("2027-09-03",15),
    ("2027-09-04",15),("2027-09-05",15),("2027-09-06",15),("2027-09-07",15),("2027-09-08",15),
    ("2027-09-09",2),("2027-09-10",15),("2027-09-11",15),("2027-09-12",15),("2027-09-13",7),
    ("2027-09-14",15),("2027-09-15",15),("2027-09-16",14),("2027-09-17",15),("2027-09-18",15),
    ("2027-09-19",15),("2027-09-20",2),("2027-09-21",15),("2027-09-22",15),("2027-09-23",13),
    ("2027-09-24",15),("2027-09-25",15),("2027-09-26",15),
]

# ------------------------------------------------- MLB 2027 team game schedules
# Transcribed 2026-11-25 from the official MLB stats API (per-team queries, source above).
# CSV rows: gameDateUTC, awayTeamId, homeTeamId  (the API "date" bucket may differ from
# gameDate for late evening games; we bucket by PT date at build time).
GIANTS_2027_FILE = "giants_2027.csv"

ATHLETICS_2027_FILE = "athletics_2027.csv"

# ----------------------------- API per-date lists (ground truth, fetched 2026-11-25)
# From: schedule?sportId=1&teamId=137&startDate=2027-03-24&endDate=2027-09-27&fields=totalGames,dates,date,totalGames
GIANTS_API_DATES = """2027-03-25 2027-03-27 2027-03-28 2027-03-29 2027-03-30 2027-03-31
2027-04-02 2027-04-03 2027-04-04 2027-04-05 2027-04-06 2027-04-07 2027-04-08 2027-04-09 2027-04-10 2027-04-11
2027-04-13 2027-04-14 2027-04-15 2027-04-16 2027-04-17 2027-04-18 2027-04-20 2027-04-21 2027-04-22 2027-04-23
2027-04-24 2027-04-25 2027-04-26 2027-04-27 2027-04-28 2027-04-30
2027-05-01 2027-05-02 2027-05-03 2027-05-04 2027-05-05 2027-05-06 2027-05-07 2027-05-08 2027-05-09 2027-05-11
2027-05-12 2027-05-13 2027-05-14 2027-05-15 2027-05-16 2027-05-18 2027-05-19 2027-05-20 2027-05-21 2027-05-22
2027-05-23 2027-05-24 2027-05-25 2027-05-26 2027-05-27 2027-05-28 2027-05-29 2027-05-30 2027-05-31
2027-06-01 2027-06-02 2027-06-04 2027-06-05 2027-06-06 2027-06-07 2027-06-08 2027-06-09 2027-06-11 2027-06-12
2027-06-13 2027-06-14 2027-06-15 2027-06-16 2027-06-18 2027-06-19 2027-06-20 2027-06-21 2027-06-22 2027-06-23
2027-06-24 2027-06-25 2027-06-26 2027-06-27 2027-06-28 2027-06-29 2027-06-30
2027-07-01 2027-07-02 2027-07-03 2027-07-04 2027-07-06 2027-07-07 2027-07-08 2027-07-09 2027-07-10 2027-07-11
2027-07-16 2027-07-17 2027-07-18 2027-07-19 2027-07-20 2027-07-21 2027-07-22 2027-07-23 2027-07-24 2027-07-25
2027-07-26 2027-07-27 2027-07-28 2027-07-30 2027-07-31
2027-08-01 2027-08-02 2027-08-03 2027-08-04 2027-08-06 2027-08-07 2027-08-08 2027-08-09 2027-08-10 2027-08-11
2027-08-13 2027-08-14 2027-08-15 2027-08-17 2027-08-18 2027-08-19 2027-08-20 2027-08-21 2027-08-22 2027-08-24
2027-08-25 2027-08-26 2027-08-27 2027-08-28 2027-08-29 2027-08-30 2027-08-31
2027-09-01 2027-09-03 2027-09-04 2027-09-05 2027-09-06 2027-09-07 2027-09-08 2027-09-10 2027-09-11 2027-09-12
2027-09-13 2027-09-14 2027-09-15 2027-09-17 2027-09-18 2027-09-19 2027-09-21 2027-09-22 2027-09-23 2027-09-24
2027-09-25 2027-09-26""".split()

ATHLETICS_API_DATES = """2027-03-25 2027-03-26 2027-03-27 2027-03-29 2027-03-30 2027-03-31
2027-04-01 2027-04-02 2027-04-03 2027-04-04 2027-04-05 2027-04-06 2027-04-07 2027-04-09 2027-04-10 2027-04-11
2027-04-13 2027-04-14 2027-04-15 2027-04-16 2027-04-17 2027-04-18 2027-04-19 2027-04-20 2027-04-21 2027-04-22
2027-04-23 2027-04-24 2027-04-25 2027-04-27 2027-04-28 2027-04-29 2027-04-30
2027-05-01 2027-05-02 2027-05-03 2027-05-04 2027-05-05 2027-05-07 2027-05-08 2027-05-09 2027-05-11 2027-05-12
2027-05-13 2027-05-14 2027-05-15 2027-05-16 2027-05-17 2027-05-18 2027-05-19 2027-05-20 2027-05-21 2027-05-22
2027-05-23 2027-05-24 2027-05-25 2027-05-26 2027-05-28 2027-05-29 2027-05-30 2027-05-31
2027-06-01 2027-06-02 2027-06-03 2027-06-04 2027-06-05 2027-06-07 2027-06-08 2027-06-09 2027-06-11 2027-06-12
2027-06-13 2027-06-15 2027-06-16 2027-06-17 2027-06-18 2027-06-19 2027-06-20 2027-06-21 2027-06-22 2027-06-23
2027-06-25 2027-06-26 2027-06-27 2027-06-29 2027-06-30
2027-07-01 2027-07-02 2027-07-03 2027-07-04 2027-07-05 2027-07-06 2027-07-07 2027-07-08 2027-07-09 2027-07-10
2027-07-11 2027-07-16 2027-07-17 2027-07-18 2027-07-19 2027-07-20 2027-07-21 2027-07-22 2027-07-23 2027-07-24
2027-07-25 2027-07-27 2027-07-28 2027-07-29 2027-07-30 2027-07-31
2027-08-01 2027-08-03 2027-08-04 2027-08-05 2027-08-06 2027-08-07 2027-08-08 2027-08-10 2027-08-11 2027-08-12
2027-08-13 2027-08-14 2027-08-15 2027-08-16 2027-08-17 2027-08-18 2027-08-19 2027-08-20 2027-08-21 2027-08-22
2027-08-24 2027-08-25 2027-08-26 2027-08-27 2027-08-28 2027-08-29 2027-08-30 2027-08-31
2027-09-01 2027-09-03 2027-09-04 2027-09-05 2027-09-06 2027-09-07 2027-09-08 2027-09-10 2027-09-11 2027-09-12
2027-09-14 2027-09-15 2027-09-16 2027-09-17 2027-09-18 2027-09-19 2027-09-21 2027-09-22 2027-09-23 2027-09-24
2027-09-25 2027-09-26""".split()

# Spring training windows per API: spring gameType=S dates 2027-02-19 .. 2027-03-23.
SPRING_END = "2027-03-23"

def parse_team_csv(path, tid, api_dates):
    """Parse rows (PT-date, UTC first-pitch clock, awayId, homeId).
    Rule: first-pitch UTC datetime = (date + 1 day) if clock < 12:00Z else (date @ clock).
    The resulting PT date must equal the row's date. Returns list of game dicts."""
    from datetime import date as _date
    games, errors = [], []
    seen = {}
    for ln, raw in enumerate(open(os.path.join(os.path.dirname(__file__), path)), 1):
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(",")
        if len(parts) != 4:
            errors.append(f"{path}:{ln}: expected 4 fields, got {len(parts)}: {raw}")
            continue
        d, t, aw, hm = parts
        try:
            day = _date.fromisoformat(d)
            hh, mm = int(t[:2]), int(t[3:5])
            assert 0 <= hh <= 23 and 0 <= mm <= 59 and ":" in t
            aw_i, hm_i = int(aw), int(hm)
        except Exception as e:
            errors.append(f"{path}:{ln}: bad fields: {raw} ({e})")
            continue
        real_utc = datetime(day.year, day.month, day.day, hh, mm, tzinfo=UTC)
        if hh < 7:  # evening PT game: API stores next-day UTC gameDate
            real_utc += timedelta(days=1)
        # 07-11Z slots are the API's same-day placeholder slots for unannounced times
        pt_dt = real_utc.astimezone(PT)
        if pt_dt.date() != day:
            errors.append(f"{path}:{ln}: PT-date mismatch: {raw} -> PT {pt_dt}")
            continue
        seen[day.isoformat()] = seen.get(day.isoformat(), 0) + 1
        spring = d <= SPRING_END
        games.append({
            "pt_date": d, "pt_time": pt_dt.strftime("%H:%M"),
            "utc": real_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "away_id": aw_i, "home_id": hm_i, "type": "spring" if spring else "regular",
        })
    # Verify PT-date multiset vs API list (regular-season dates only)
    got_reg = {k: v for k, v in seen.items() if k > SPRING_END}
    want = {}
    for d in api_dates:
        want[d] = want.get(d, 0) + 1
    missing = sorted(set(want) - set(got_reg))
    extra = sorted(set(got_reg) - set(want))
    dupes = sorted(k for k, v in got_reg.items() if v > 1)
    if missing: errors.append(f"{path}: MISSING PT dates vs API: {missing}")
    if extra: errors.append(f"{path}: EXTRA PT dates vs API: {extra}")
    if dupes: errors.append(f"{path}: DUPLICATE PT dates: {dupes}")
    if got_reg and want and got_reg.keys() == want.keys():
        for k in want:
            if got_reg[k] != want[k]:
                errors.append(f"{path}: count mismatch {k}: got {got_reg[k]} want {want[k]}")
    return games, errors, len(want)

def game_to_row(g, team_id, team_name, radio, source, priority):
    aw, hm = g["away_id"], g["home_id"]
    aw_name = MLB_TEAMS.get(aw, f"Team #{aw} (unresolved ID)")
    hm_name = MLB_TEAMS.get(hm, f"Team #{hm} (unresolved ID)")
    home = hm == team_id
    opp = aw_name if home else hm_name
    t = g["pt_time"]
    # Plausibility gate: MLB API returns placeholder slots for unannounced times
    # (e.g. *T33:00Z patterns decoding to early-morning PT). Flag those as TBD.
    hh = int(t[:2])
    plausible = 8 <= hh <= 21
    return {
        "date": g["pt_date"], "time_pt": t if plausible else None,
        "time_est_pt": ("13:05" if home else None) if not plausible else None,
        "matchup": (f"{opp} at {team_name}" if home else f"{team_name} at {opp}"),
        "home": home, "type": g["type"], "radio": radio,
        "priority": priority, "source": source, "verified": bool(plausible),
        "time_status": "official" if plausible else "tbd_estimated",
    }

# Refined estimator: typical first pitch by home park time zone (PT display).
HOME_TZ_EST = {  # (away-game estimated PT first pitch) by home team's zone
    "eastern": "16:10", "central": "16:40", "mountain": "17:40", "pacific": "18:40", "hawaii": "18:10",
}
TEAM_TZ = {108:"pacific",109:"mountain",110:"eastern",111:"eastern",112:"central",113:"eastern",
    114:"eastern",115:"mountain",116:"eastern",117:"central",118:"central",119:"pacific",
    120:"eastern",121:"eastern",133:"pacific",134:"eastern",135:"pacific",136:"pacific",
    137:"pacific",138:"central",139:"eastern",140:"central",141:"eastern",142:"central",
    143:"eastern",144:"eastern",145:"central",146:"eastern",147:"eastern",158:"central"}

def game_to_row(g, team_id, team_name, radio, source, priority):  # noqa: F811 (refined)
    aw, hm = g["away_id"], g["home_id"]
    aw_name = MLB_TEAMS.get(aw, f"Team #{aw} (unresolved ID)")
    hm_name = MLB_TEAMS.get(hm, f"Team #{hm} (unresolved ID)")
    home = hm == team_id
    opp = aw_name if home else hm_name
    t = g["pt_time"]
    hh = int(t[:2])
    plausible = 8 <= hh <= 21
    est = "13:05" if home else HOME_TZ_EST.get(TEAM_TZ.get(hm if not home else aw, "pacific"), "17:05")
    return {
        "date": g["pt_date"], "time_pt": t if plausible else None, "time_est_pt": None if plausible else est,
        "matchup": (f"{opp} at {team_name}" if home else f"{team_name} at {opp}"),
        "home": home, "type": g["type"], "radio": radio, "priority": priority,
        "source": source, "verified": bool(plausible),
        "time_status": "official" if plausible else "tbd_estimated",
    }

GIANTS_SOURCE = MLB_SOURCE.format(tid=137)
ATHLETICS_SOURCE = MLB_SOURCE.format(tid=133)
GIANTS_RADIO = "KNBR 680 AM / 104.5 FM (KTCT 1050 AM on conflicts)"
ATHLETICS_RADIO = "KNEW 960 AM (Bay Area) / KSTE 650 AM Sacramento flagship / 'A's Cast' stream"

def build_mlb():
    errors = []
    g_games, e1, g_n = parse_team_csv(GIANTS_2027_FILE, 137, GIANTS_API_DATES)
    a_games, e2, a_n = parse_team_csv(ATHLETICS_2027_FILE, 133, ATHLETICS_API_DATES)
    errors += e1 + e2
    if errors:
        for e in errors: print("DATA ERROR:", e)
        raise SystemExit("MLB CSV verification failed - fix data before build")

    g_rows = [game_to_row(x, 137, "San Francisco Giants", GIANTS_RADIO, GIANTS_SOURCE, "high") for x in g_games]
    a_rows = [game_to_row(x, 133, "Athletics", ATHLETICS_RADIO, ATHLETICS_SOURCE, "high") for x in a_games]

    # Special MLB 2027 games (official stats API):
    mlb_source_day = MLB_DAYMAP_SOURCE
    specials = [
        {"date": "2027-03-24", "time_pt": "17:10", "time_est_pt": None, "matchup": "Boston Red Sox at Seattle Mariners (2027 Opening Night)",
         "home": False, "type": "special", "radio": "ESPN Radio (national); check local affiliate", "priority": "normal",
         "source": MLB_DAYMAP_SOURCE, "verified": True, "time_status": "official"},
        {"date": "2027-07-13", "time_pt": None, "time_est_pt": "17:00", "matchup": "MLB All-Star Game - American League at National League (Wrigley Field, Chicago)",
         "home": False, "type": "special", "radio": None, "priority": "normal",
         "source": MLB_DAYMAP_SOURCE, "verified": False, "time_status": "tbd_estimated"},
        {"date": "2027-07-15", "time_pt": None, "time_est_pt": "16:10", "matchup": "Atlanta Braves at Boston Red Sox (second-half single game)",
         "home": False, "type": "special", "radio": None, "priority": "normal",
         "source": MLB_DAYMAP_SOURCE, "verified": False, "time_status": "tbd_estimated"},
    ]
    daymap = [{"date": d, "games": n} for d, n in MLB_2027_DAYMAP]
    out = {
        "generated": GEN_AT,
        "source_daymap": MLB_DAYMAP_SOURCE,
        "source_teams": {"giants": GIANTS_SOURCE, "athletics": ATHLETICS_SOURCE,
                         "team_ids": "https://statsapi.mlb.com/api/v1/teams?sportId=1"},
        "note": ("Day map = total MLB games per day (spring training Feb 19-Mar 23, Opening Night Mar 24, "
                 "regular season Mar 25-Sep 26, All-Star Game Jul 13). Zero-game dates are absent from the "
                 "API response: the only 2027 zero-game dates are 2027-07-12 and 2027-07-14."),
        "zero_game_dates_2027": ["2027-07-12", "2027-07-14"],
        "daymap": daymap,
        "giants": {"count": len(g_rows), "games": g_rows},
        "athletics": {"count": len(a_rows), "games": a_rows},
        "specials": specials,
        "verified_counts": {"giants_regular_api_dates": g_n, "athletics_regular_api_dates": a_n},
        "flags": [
            "Giants spring game 2027-03-21 lists home team id 105, which is not one of the 30 active "
            "MLB team IDs in the API; shown as 'Team #105 (unresolved ID)'. Flagged for review.",
            "Many 2027 first-pitch times are not yet announced by MLB; the API returns placeholder "
            "slots (e.g. 10:33Z decoding to 03:33 PT). Those games show time TBD with an estimated "
            "typical slot and verified=false.",
        ],
    }
    with open(os.path.join(OUT, "mlb_2027.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"mlb_2027.json: daymap {len(daymap)} days; giants {len(g_rows)} games; athletics {len(a_rows)} games")
    return out

if __name__ == "__main__":
    build_mlb()

# ---------------------------------------------------------------- NFL 2026
NFL_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nfl", "nfl_2026.csv")
NFL_TEAM_NAMES = {"ARI":"Arizona Cardinals","ATL":"Atlanta Falcons","BAL":"Baltimore Ravens","BUF":"Buffalo Bills",
 "CAR":"Carolina Panthers","CHI":"Chicago Bears","CIN":"Cincinnati Bengals","CLE":"Cleveland Browns",
 "DAL":"Dallas Cowboys","DEN":"Denver Broncos","DET":"Detroit Lions","GB":"Green Bay Packers",
 "HOU":"Houston Texans","IND":"Indianapolis Colts","JAX":"Jacksonville Jaguars","KC":"Kansas City Chiefs",
 "LV":"Las Vegas Raiders","LAC":"Los Angeles Chargers","LAR":"Los Angeles Rams","MIA":"Miami Dolphins",
 "MIN":"Minnesota Vikings","NE":"New England Patriots","NO":"New Orleans Saints","NYG":"New York Giants",
 "NYJ":"New York Jets","PHI":"Philadelphia Eagles","PIT":"Pittsburgh Steelers","SF":"San Francisco 49ers",
 "SEA":"Seattle Seahawks","TB":"Tampa Bay Buccaneers","TEN":"Tennessee Titans","WAS":"Washington Commanders"}
NFL_SOURCE = "https://fixturedownload.com/results/nfl-2026 (mirror of the official 2026 NFL schedule; spot-verified against https://www.nfl.com/schedules/2026/REG13/)"
WW1_SOURCE = "https://www.westwoodonesports.com/nfl-schedule/"
NFL_RADIO_BAY = "KNBR 680 AM / 104.5 FM (Westwood One NFL radio; KTCT 1050 AM on conflicts)"

# Westwood One 2026-27 NFL broadcast slate (times ET, broadcast/on-air start).
# Format: (date, timeET or None, away, home or None, label)
WW1_NFL = [
 ("2026-11-25","19:30","GB","LAR","NFL TNF (Netflix)"),
 ("2026-11-26","12:30","CHI","DET","NFL Thanksgiving"),
 ("2026-11-26","16:15","PHI","DAL","NFL Thanksgiving"),
 ("2026-11-26","20:00","KC","BUF","NFL Thanksgiving"),
 ("2026-11-27","14:30","DEN","PIT","NFL Black Friday (Prime)"),
 ("2026-11-30","19:00","CAR","TB","NFL MNF"),
 ("2026-11-29","19:30","LV","CLE","NFL SNF"),
 ("2026-12-03","19:30","KC","LAR","NFL TNF"),
 ("2026-12-06","19:30","HOU","PIT","NFL SNF"),
 ("2026-12-07","19:00","DAL","SEA","NFL MNF"),
 ("2026-12-10","19:30","MIN","NE","NFL TNF"),
 ("2026-12-13","19:30","BUF","GB","NFL SNF"),
 ("2026-12-14","19:00","PIT","JAX","NFL MNF"),
 ("2026-12-17","19:30","SF","LAC","NFL TNF - 49ers"),
 ("2026-12-19","16:30","SEA","PHI","NFL Saturday"),
 ("2026-12-19","20:00","CHI","BUF","NFL Saturday"),
 ("2026-12-20","19:30","DET","MIN","NFL SNF"),
 ("2026-12-24","19:30","HOU","PHI","NFL TNF"),
 ("2026-12-25","12:30","GB","CHI","NFL Christmas"),
 ("2026-12-25","16:15","BUF","DEN","NFL Christmas"),
 ("2026-12-25","20:00","LAR","SEA","NFL Christmas"),
 ("2026-12-26",None,None,None,"NFL Week 16 Saturday doubleheader (teams & time TBA; WW1 lists 8:00 ET window)"),
 ("2026-12-27","19:30","JAX","DAL","NFL SNF"),
 ("2026-12-28","19:00","NYG","DET","NFL MNF"),
 ("2026-12-31","19:30","BAL","CIN","NFL TNF"),
 ("2027-01-02","16:00",None,None,"NFL Week 17 Saturday doubleheader (teams & time TBA; WW1 lists 4:00 ET window)"),
 ("2027-01-03","19:30","PHI","SF","NFL SNF - 49ers at Levi's Stadium"),
 ("2027-01-04","19:00","HOU","GB","NFL MNF"),
 ("2027-01-09","12:30",None,None,"NFL Week 18 Saturday games (matchups & times TBA; WW1 lists 12:30 & 8:00 ET)"),
 ("2027-01-09","20:00",None,None,"NFL Week 18 Saturday window 2"),
 ("2027-01-10","19:30",None,None,"NFL Week 18 Sunday night (season finale)"),
]

def parse_nfl():
    rows, errors = [], []
    from collections import Counter
    teams = Counter(); nums = []
    for r in csv.DictReader(open(NFL_CSV)):
        d, t = r["date_utc"], r["time_utc"]
        hh, mm = int(t[:2]), int(t[3:5])
        if t == "00:00":
            pt_date, pt_time, tbd = d, None, True  # midnight-UTC placeholder: day/time TBA
        else:
            u = datetime(int(d[:4]), int(d[5:7]), int(d[8:10]), hh, mm, tzinfo=UTC)
            p = u.astimezone(PT)
            pt_date, pt_time, tbd = p.date().isoformat(), p.strftime("%H:%M"), False
        nums.append(int(r["match_no"]))
        teams[r["home"]] += 1; teams[r["away"]] += 1
        rows.append({"match_no": int(r["match_no"]), "week": int(r["round"]),
            "date": pt_date, "time_pt": pt_time,
            "home_code": r["home"], "away_code": r["away"],
            "matchup": f"{NFL_TEAM_NAMES[r['away']]} at {NFL_TEAM_NAMES[r['home']]}",
            "sf": "SF" in (r["home"], r["away"]),
            "time_status": "tbd" if tbd else "official",
            "radio": NFL_RADIO_BAY, "source": NFL_SOURCE, "priority": "high" if "SF" in (r["home"], r["away"]) else "normal"})
    if nums != list(range(1, 273)): errors.append(f"NFL match numbers incomplete: {len(nums)} rows")
    bad = {t: c for t, c in teams.items() if c != 17}
    if bad: errors.append(f"NFL teams with != 17 games: {bad}")
    return rows, errors

def pair_ww1(nfl_rows):
    """Attach WW1 broadcast info to feed games by team pairing; report unpaired."""
    flags = []
    for w in WW1_NFL:
        date, tet, aw, hm, label = w
        if aw is None:
            continue
        hits = [g for g in nfl_rows if g["away_code"] == aw and g["home_code"] == hm]
        if len(hits) != 1:
            flags.append(f"WW1 entry {date} {aw}@{hm}: {len(hits)} matching feed games (expected 1)")
            continue
        g = hits[0]
        if g["date"] != date:
            flags.append(f"WW1 entry {date} {aw}@{hm} mismatches feed date {g['date']} "
                         f"({g['matchup']}); both dates treated as potentially busy")
        if tet is not None:
            # broadcast start ET -> PT; also keep kickoff from feed
            bh = int(tet[:2]) - 3  # ET->PT
            g["ww1_broadcast_pt"] = f"{bh:02d}:{tet[3:5]}"
            g["radio"] = NFL_RADIO_BAY
        g["ww1_label"] = label
    return flags

NFL_PLAYOFFS = [
 ("2027-01-16", "2027-01-18", "NFL Wild Card round - 6 games, days/matchups/times TBA",
  "https://en.wikipedia.org/wiki/2026%E2%80%9327_NFL_playoffs"),
 ("2027-01-23", "2027-01-24", "NFL Divisional round - 4 games, times TBA",
  "https://en.wikipedia.org/wiki/2026%E2%80%9327_NFL_playoffs"),
 ("2027-01-31", None, "NFL Conference championships - 2 games (AFC & NFC), times TBA",
  "https://en.wikipedia.org/wiki/2026%E2%80%9327_NFL_playoffs"),
 ("2027-02-14", None, "Super Bowl LXI - SoFi Stadium, Inglewood CA (Westwood One radio; ESPN/ABC TV)",
  "https://en.wikipedia.org/wiki/Super_Bowl_LXI"),
]

def build_nfl():
    rows, errors = parse_nfl()
    errors += pair_ww1(rows)
    for e in errors: print("NFL DATA WARNING:", e)
    playoff_rows = []
    for start, end, label, src in NFL_PLAYOFFS:
        days = [start] if not end else [ (datetime(int(start[:4]),int(start[5:7]),int(start[8:10])) + timedelta(days=i)).date().isoformat() for i in range((datetime.fromisoformat(end) - datetime.fromisoformat(start)).days + 1)]
        for d in days:
            playoff_rows.append({"date": d, "time_pt": None, "matchup": label,
                "sf": False, "time_status": "tbd", "radio": NFL_RADIO_BAY,
                "source": src, "priority": "normal"})
    out = {"generated": GEN_AT, "source": NFL_SOURCE, "ww1_source": WW1_SOURCE,
        "games": rows, "playoffs": playoff_rows,
        "counts": {"regular": len(rows), "sf": sum(1 for r in rows if r["sf"]), "playoff_days": len(playoff_rows)},
        "flags": [
            "fixturedownload DEN@PIT listed 2026-11-28 20:00Z; NFL.com (REG13 page) and Westwood One both place the Black Friday game on Fri Nov 27 (3:00 PM ET kickoff). Feed date used in data; Nov 27 is also busy via the WW1 broadcast entry.",
            "Weeks 16/17: fixturedownload shows ATL@TB, IND@CIN, MIN@WAS, PIT@CAR at 2026-12-29 00:00Z and JAX@WAS, LAC@KC, NE@DEN, TB@LAR at 2027-01-05 00:00Z (midnight-UTC = time TBA placeholder); Westwood One instead lists a Sat Dec 26 doubleheader and Sat Jan 2 doubleheader. Both date interpretations are shown; exact days/times flagged for review.",
            "Week 18: all 16 games listed at 2027-01-10 00:00Z (TBD). NFL Week 18 spans Sat Jan 9 - Sun Jan 10, 2027; Westwood One lists Saturday games 12:30/8:00 ET and SNF 7:30 ET. Both days treated as busy.",
            "Westwood One broadcast times are on-air start times (pregame), typically 15-30 min before kickoff.",
            "Postseason matchups/times are TBA until seeding is set (Jan 2027). Radio: Westwood One carries every playoff game.",
        ]}
    with open(os.path.join(OUT, "nfl.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"nfl.json: {len(rows)} regular games ({out['counts']['sf']} 49ers), {len(playoff_rows)} playoff days, "
          f"{sum(1 for r in rows if r.get('ww1_broadcast_pt'))} WW1-paired broadcasts")
    return out

if __name__ == "__main__":
    build_mlb()
    build_nfl()

# ---------------------------------------------------------------- NCAAF
# Verified (2026-11-25): Big Game Nov 21 2026 at Berkeley (Stanford 44-26); Stanford 6-5 bowl-eligible
# (one December bowl, date TBA); Cal 3-7 season complete. WW1 CFB & CFP dates from cited pages.
NCAAF_SOURCE_WW1 = "https://www.westwoodonesports.com/ncaa-football/"
NCAAF_SOURCE_BIGGAME = "https://cbssports.com (Big Game Nov 21, 2026: Stanford 44-26 at California) / calbears.com / gostanford.com"
CFP_SOURCE = "https://en.wikipedia.org/wiki/2026%E2%80%9327_College_Football_Playoff"
CAL_2027_SOURCE = "https://calbears.com (2027 opponents announced; dates TBD except non-conference)"
STANFORD_RADIO = "KNBR 680 AM / KTCT 1050 AM (Richardson PxP, Fisk color)"
CAL_RADIO = "KGO 810 AM (Allegri PxP, Pawlawski analyst; SiriusXM 81)"

def build_ncaaf():
    rows = []
    def add(date, time_pt, matchup, radio, source, kind="ncaaf", est=False, note=None, priority="normal"):
        rows.append({"date": date, "time_pt": time_pt, "matchup": matchup, "kind": kind,
                     "radio": radio, "source": source, "priority": priority,
                     "estimated": est, "time_status": "tbd_estimated" if est or time_pt is None else "official",
                     "note": note})
    # --- verified 2026-27 items
    add("2026-11-28", "08:30", "Michigan at Ohio State (WW1 national CFB, rivalry week)",
        "KNBR 680/104.5 + KTCT 1050", NCAAF_SOURCE_WW1)
    add("2026-12-05", "12:30", "SEC Championship Game (WW1 national CFB)",
        "KNBR 680/104.5 + KTCT 1050", NCAAF_SOURCE_WW1)
    add("2026-12-12", "11:00", "Army vs Navy (MetLife Stadium, WW1 national CFB)",
        "KNBR 680/104.5 + KTCT 1050", NCAAF_SOURCE_WW1)
    add("2026-12-18", None, "CFP first round (games Dec 18-19, campuses, times TBA)", "KTCT 1050 (ESPN Radio natl on some games)", CFP_SOURCE)
    add("2026-12-19", None, "CFP first round (games Dec 18-19, campuses, times TBA)", "KTCT 1050 (ESPN Radio natl on some games)", CFP_SOURCE)
    add("2026-12-30", None, "CFP quarterfinal (Dec 30 - Jan 1 bowl sites, times TBA)", "KTCT 1050 (ESPN Radio)", CFP_SOURCE)
    add("2026-12-31", None, "CFP quarterfinal (Dec 30 - Jan 1 bowl sites, times TBA)", "KTCT 1050 (ESPN Radio)", CFP_SOURCE)
    add("2027-01-01", None, "CFP quarterfinal (Dec 30 - Jan 1 bowl sites, times TBA)", "KTCT 1050 (ESPN Radio)", CFP_SOURCE)
    add("2027-01-14", None, "CFP semifinal - Orange Bowl (TNT)", "ESPN Radio natl (KTCT 1050 when carried)", CFP_SOURCE)
    add("2027-01-15", None, "CFP semifinal - Sugar Bowl (ABC/ESPN)", "ESPN Radio natl (KTCT 1050 when carried)", CFP_SOURCE)
    add("2027-01-25", None, "CFP National Championship - Allegiant Stadium, Las Vegas", "ESPN Radio natl (KTCT 1050)", CFP_SOURCE)
    add("2026-12-TBD", None, "Stanford bowl game (6-5 bowl-eligible; matchup/date TBA - December 2026)",
        STANFORD_RADIO, "https://gostanford.com (bowl announcement pending)", priority="high",
        note="Date not yet announced; every December 2026 Saturday flagged as potentially busy until announced")
    # estimated December-Saturday shading for the unannounced Stanford bowl
    for d in ("2026-12-05", "2026-12-12", "2026-12-19", "2026-12-26"):
        add(d, None, "Stanford bowl candidate window (date TBA)", STANFORD_RADIO,
            "https://gostanford.com", est=True, note="Potential bowl date - flagged, not a scheduled game")
    # --- Cal 2027 announced opponents (official, dates per calbears.com)
    for d, m in (("2027-08-28", "Sacramento State at California"), ("2027-09-04", "California at UCLA"),
                 ("2027-09-11", "Old Dominion at California")):
        add(d, None, m + " (2027 non-conference, time TBA)", CAL_RADIO, CAL_2027_SOURCE, priority="high")
    acc_home = ["Boston College", "Florida State", "Louisville", "SMU"]
    acc_away = ["Georgia Tech", "Miami", "Pittsburgh", "Stanford", "Wake Forest"]
    add("2027-SEP-TBD", None, "Cal ACC home 2027 (dates TBA): " + ", ".join(acc_home), CAL_RADIO, CAL_2027_SOURCE, est=True, priority="high")
    add("2027-SEP-TBD", None, "Cal ACC road 2027 (dates TBA): " + ", ".join(acc_away), CAL_RADIO, CAL_2027_SOURCE, est=True, priority="high")
    add("2027-11-TBD", None, "Big Game 2027 - California at Stanford (date TBA, typically mid/late November)",
        STANFORD_RADIO + " / " + CAL_RADIO, "https://gostanford.com", est=True, priority="high")
    # --- 2027-29 season-pattern estimates (labeled estimates, not schedules)
    est_rows = []
    def est_season(year):
        # NCAAF: Labor Day weekend start (~Sep 4) through Big Game (~Nov 20); CFP Dec round 1 (~Dec 18)
        for d in season_days(f"{year}-08-28", f"{year}-11-27", weekend_only=True):
            est_rows.append({"date": d, "time_pt": None,
                "matchup": "NCAAF game day (estimated pattern: college football Saturday)",
                "kind": "ncaaf_est", "radio": "KNBR/KTCT (WW1 national game of week, some games)",
                "source": "ESTIMATE - pattern-based, no official 2027+ NCAAF schedule released",
                "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    return rows, est_rows

def season_days(start, end, weekend_only=False):
    d0, d1 = datetime.fromisoformat(start), datetime.fromisoformat(end)
    out = []
    while d0 <= d1:
        if not weekend_only or d0.weekday() >= 4:  # Fri=4, Sat=5
            out.append(d0.date().isoformat())
        d0 += timedelta(days=1)
    return out

def build_mlb_estimate(year):
    """Estimated MLB day-busy map for a year without a released schedule."""
    st_start = f"{year}-02-19"
    st_end = f"{year}-03-21"
    od = f"{year}-03-25"
    end = f"{year}-09-26"
    asg = f"{year}-07-11"
    busy = set(season_days(st_start, end))
    for d in (asg, (datetime.fromisoformat(asg) + timedelta(days=1)).date().isoformat(),
              (datetime.fromisoformat(asg) + timedelta(days=2)).date().isoformat()):
        busy.discard(d)  # All-Star break estimate: 3 dark days
    rows = [{"date": d, "time_pt": None,
             "matchup": "MLB game day (estimated - 2028/29 schedule not released; SF clubs play nearly daily Feb-Sep)",
             "kind": "mlb_est", "radio": "KNBR 680/104.5 (Giants) / KNEW 960 (A's)",
             "source": "ESTIMATE - based on 2027 official season shape (Feb 19 ST start, Mar 25 OD, Sep 26 end, All-Star break Jul)",
             "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None}
            for d in sorted(busy)]
    return rows

def build_nfl_estimate(year):
    """Estimated NFL day-busy map for seasons without a released schedule."""
    lab = datetime(int(year), 9, 1)
    while lab.weekday() != 0: lab += timedelta(days=1)      # Labor Day
    tnF = lab + timedelta(days=3)                          # opener Thursday
    sb = {"2027": None, "2028": "2028-02-13", "2029": "2029-02-11"}.get(str(year))
    rows = []
    seas = season_days(tnF.date().isoformat(), f"{int(year)+1}-01-08")
    for d in seas:
        wd = datetime.fromisoformat(d).weekday()
        if wd == 6:   # Sunday
            rows.append({"date": d, "time_pt": None, "matchup": "NFL Sunday (estimated slate 10:00-21:00 PT)",
                "kind": "nfl_est", "radio": "KNBR 680/104.5 (WW1)", "source": "ESTIMATE - NFL pattern",
                "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
        elif wd == 3: # Thursday
            rows.append({"date": d, "time_pt": None, "matchup": "NFL Thursday night (estimated)",
                "kind": "nfl_est", "radio": "KNBR 680/104.5 (WW1)", "source": "ESTIMATE - NFL pattern",
                "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
        elif wd == 0: # Monday
            rows.append({"date": d, "time_pt": None, "matchup": "NFL Monday night (estimated)",
                "kind": "nfl_est", "radio": "KNBR 680/104.5 (WW1)", "source": "ESTIMATE - NFL pattern",
                "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    # playoffs Jan + SB of the FOLLOWING Jan/Feb handled in build_all
    return rows

def build_nfl_postseason_estimate(year_end):
    """Estimated playoff busy days for Jan-Feb of year_end+1."""
    y = year_end + 1
    rows = []
    for d in season_days(f"{y}-01-08", f"{y}-01-31", weekend_only=True):
        rows.append({"date": d, "time_pt": None, "matchup": "NFL playoff weekend (estimated)",
            "kind": "nfl_est", "radio": "KNBR 680/104.5 (WW1)", "source": "ESTIMATE - NFL playoff pattern",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    if y == 2028:
        rows.append({"date": "2028-02-13", "time_pt": None,
            "matchup": "Super Bowl LXII - Atlanta (CBS TV; WW1 radio) - OFFICIAL date/site",
            "kind": "nfl", "radio": "KNBR 680/104.5 (WW1)",
            "source": "https://en.wikipedia.org/wiki/Super_Bowl_LXII",
            "priority": "normal", "estimated": False, "time_status": "tbd_estimated", "note": None})
    if y == 2029:
        rows.append({"date": "2029-02-11", "time_pt": None,
            "matchup": "Super Bowl LXIII - Las Vegas (estimated 2nd-Sunday date; FOX TV; WW1 radio)",
            "kind": "nfl", "radio": "KNBR 680/104.5 (WW1)",
            "source": "https://en.wikipedia.org/wiki/Super_Bowl_LXIII (site verified; date estimated)",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    return rows

if __name__ == "__main__":
    build_mlb(); build_nfl()
    print("ncaaf/estimates functions loaded (emitted by build_all)")

# ---------------------------------------------------------------- radio / durations / free windows
RADIO_MAP = {
 "bay_area_stations": [
  {"station": "KNBR 680 AM / 104.5 FM", "carries": ["San Francisco Giants (flagship since 1979)", "San Francisco 49ers (Simms/Hartman-era extension Apr 2026)", "Stanford football (Richardson/Fisk)", "Westwood One NFL national broadcasts", "Westwood One NCAA Football national broadcasts"], "conflict_overflow": "KTCT 1050 AM / KNBR-FM", "source": "https://en.wikipedia.org/wiki/KNBR_(AM)"},
  {"station": "KTCT 1050 AM", "carries": ["KNBR overflow (Giants/49ers/Stanford conflicts)", "Westwood One NCAA Football", "Westwood One Soccer", "ESPN Radio national (CFP games when carried)"], "source": "https://www.westwoodonesports.com/station-finder/"},
  {"station": "KSAN 107.7 FM (The Bone)", "carries": ["San Francisco 49ers (flagship FM; Papa/Ryan)"], "source": "https://en.wikipedia.org/wiki/List_of_San_Francisco_49ers_broadcasters"},
  {"station": "KNEW 960 AM", "carries": ["Athletics (Bay Area iHeart affiliate)"], "source": "https://en.wikipedia.org/wiki/Oakland_Athletics_Radio_Network"},
  {"station": "KSTE 650 AM (Sacramento)", "carries": ["Athletics (flagship) - reachable in parts of Bay Area; 'A's Cast' stream statewide"], "source": "https://en.wikipedia.org/wiki/Oakland_Athletics_Radio_Network"},
  {"station": "KGO 810 AM", "carries": ["California Golden Bears football (Allegri/Pawlawski; SiriusXM 81)"], "source": "https://calbears.com"},
  {"station": "KGMZ 95.7 FM (The Game)", "carries": ["Golden State Warriors (flagship since 2016) - OPTIONAL monitoring, not in busy data"], "source": "https://en.wikipedia.org/wiki/KGMZ-FM"},
  {"station": "KFOX 98.5 FM (San Jose)", "carries": ["San Jose Sharks (flagship) - OPTIONAL monitoring, not in busy data"], "source": "wikipedia KUFX / 2016 reports"},
 ],
 "note": "Busy-day data covers Giants, A's, 49ers, Stanford, Cal, WW1 NFL/CFB, CFP, and MLB postseason (potential KNBR). Warriors/Sharks/Quakes were researched but NOT included in busy data (optional scope).",
 "flags": ["Warriors (95.7), Sharks (KFOX 98.5) and MLS Quakes broadcasts exist but are excluded from busy-day data per scope; flag for user decision."],
}
DURATIONS = {
 "mlb_regular_min": 165, "mlb_postseason_min": 180,
 "nfl_min": 195, "ncaaf_min": 205,
 "basis": {
  "mlb": "2026 MLB average game length ~2:42-2:44 (vertizesports/betmgm reports); postseason ~3:00. User suggested ~150 min; researched value slightly longer - researched values used.",
  "nfl": "NFL average ~3:03, median 3:01 (upintherafters/sportsgeardaily); user suggested ~180 min incl. halftime.",
  "ncaaf": "College football 2025 average ~3:26 (gamegistics/bellyupsports).",
 },
 "sources": ["https://vertizesports.com (MLB pace)", "https://www.betmgm.com/en/insights (MLB 2026 avg 2:42)", "https://upintherafters.com (NFL 3:03)", "https://www.gamegistics.com (CFB 3:26)"],
}
BUSY_BLOCK_TBD = ("12:00", "22:00")
LEAGUE_DURATION = {"mlb": 165, "mlb_post": 180, "nfl": 195, "ncaaf": 205}

def _interval(date, start, minutes, label, league, radio, source, estimated):
    d = datetime.fromisoformat(date)
    h, m = int(start[:2]), int(start[3:5])
    t0 = d + timedelta(hours=h, minutes=m)
    t1 = t0 + timedelta(minutes=minutes)
    def piece(a, b):
        return {"date": a.date().isoformat(), "start": a.strftime("%H:%M"), "end": b.strftime("%H:%M"),
                "label": label, "league": league, "radio": radio, "source": source, "estimated": estimated}
    if t1.date() == d.date():
        return [piece(t0, t1)]
    mid = d + timedelta(days=1, hours=0) - timedelta(seconds=1)
    mid = d + timedelta(days=1)
    return [piece(t0, datetime(t0.year, t0.month, t0.day, 23, 59)),
            piece(mid, datetime(mid.year, mid.month, mid.day, 0, 0) + (t1 - datetime(t0.year, t0.month, t0.day, 23, 59, 59) - timedelta(days=1)) + timedelta(seconds=59))]

def events_from_row(r, league, radio, src, estimated):
    if r.get("time_pt"):
        dur = LEAGUE_DURATION.get("mlb_post" if league == "mlb" and r.get("postseason") else league, 180)
        return _interval(r["date"], r["time_pt"], dur, r["matchup"], league, radio or r.get("radio"), src or r.get("source"), estimated)
    block = {"mlb_est": ("12:30", "21:45"), "nfl_est": ("10:00", "21:15"), "nfl_thu_est": ("17:00", "20:50"),
             "ncaaf_est": ("09:00", "20:00"), "ncaaf": ("09:00", "20:00")}.get(league, BUSY_BLOCK_TBD)
    return [{"date": r["date"], "start": block[0], "end": block[1], "label": r["matchup"],
             "league": league, "radio": radio or r.get("radio"), "source": src or r.get("source"), "estimated": True}]

def build_all():
    mlb = build_mlb(); nfl = build_nfl()
    ncaaf_rows, ncaaf_est = build_ncaaf()
    mlb28 = build_mlb_estimate(2028); mlb29 = build_mlb_estimate(2029)
    nfl27 = build_nfl_estimate(2027) + build_nfl_postseason_estimate(2027)
    nfl28 = build_nfl_estimate(2028) + build_nfl_postseason_estimate(2028)
    nfl29 = build_nfl_estimate(2029)
    ncaaf27 = ncaaf_est
    ncaaf28 = []
    for d in season_days("2028-08-26", "2028-11-25", weekend_only=True):
        ncaaf28.append({"date": d, "time_pt": None, "matchup": "NCAAF game day (estimated pattern)",
            "kind": "ncaaf_est", "radio": "KNBR/KTCT", "source": "ESTIMATE - pattern-based",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    # CFP 2027-28 & 2028-29 pattern estimates (Dec first rounds + title Mondays in Jan)
    for d in season_days("2027-12-18", "2027-12-19"):
        ncaaf28.append({"date": d, "time_pt": None, "matchup": "CFP first round (estimated)", "kind": "ncaaf_est",
            "radio": "ESPN Radio natl (KTCT 1050)", "source": "ESTIMATE - CFP pattern",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    for d in ("2028-01-24",):
        ncaaf28.append({"date": d, "time_pt": None, "matchup": "CFP National Championship (estimated date)", "kind": "ncaaf_est",
            "radio": "ESPN Radio natl (KTCT 1050)", "source": "ESTIMATE - CFP pattern",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    for d in season_days("2028-12-16", "2028-12-17") + season_days("2028-12-30", "2029-01-01", weekend_only=False):
        pass
    cfp2829 = []
    for d in season_days("2028-12-16", "2028-12-17") + season_days("2028-12-30", "2029-01-01"):
        cfp2829.append({"date": d, "time_pt": None, "matchup": "CFP first round / quarterfinal (estimated)", "kind": "ncaaf_est",
            "radio": "ESPN Radio natl (KTCT 1050)", "source": "ESTIMATE - CFP pattern",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    cfp2829.append({"date": "2029-01-22", "time_pt": None, "matchup": "CFP National Championship (estimated date)", "kind": "ncaaf_est",
        "radio": "ESPN Radio natl (KTCT 1050)", "source": "ESTIMATE - CFP pattern",
        "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    ncaaf29 = []
    for d in season_days("2029-08-25", "2029-11-24", weekend_only=True):
        ncaaf29.append({"date": d, "time_pt": None, "matchup": "NCAAF game day (estimated pattern)",
            "kind": "ncaaf_est", "radio": "KNBR/KTCT", "source": "ESTIMATE - pattern-based",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})
    cfp2930 = []
    for d in season_days("2029-12-15", "2029-12-16") + season_days("2029-12-29", "2029-12-31"):
        cfp2930.append({"date": d, "time_pt": None, "matchup": "CFP first round / quarterfinal (estimated)", "kind": "ncaaf_est",
            "radio": "ESPN Radio natl (KTCT 1050)", "source": "ESTIMATE - CFP pattern",
            "priority": "normal", "estimated": True, "time_status": "tbd_estimated", "note": None})

    with open(os.path.join(OUT, "ncaaf.json"), "w") as f:
        json.dump({"generated": GEN_AT, "verified_rows": ncaaf_rows, "estimate_rows": ncaaf_est,
                   "sources": {"ww1": NCAAF_SOURCE_WW1, "cfp": CFP_SOURCE, "cal2027": CAL_2027_SOURCE}}, f, indent=1)
    with open(os.path.join(OUT, "radio.json"), "w") as f: json.dump(RADIO_MAP, f, indent=1)
    with open(os.path.join(OUT, "durations.json"), "w") as f: json.dump(DURATIONS, f, indent=1)

    # ---------------- per-day busy intervals 2026-11-25 .. 2029-12-31
    buckets = {}
    def put(ev):
        buckets.setdefault(ev["date"], []).append(ev)
    for g in mlb["giants"]["games"] + mlb["athletics"]["games"]:
        lg = "mlb" if g["type"] == "regular" else "mlb"
        for ev in events_from_row(g, lg, g.get("radio"), g.get("source"), False):
            put(ev)
    for g in mlb["specials"]:
        for ev in events_from_row(g, "mlb_post", g.get("radio"), g.get("source"), False):
            put(ev)
    for g in nfl["games"]:
        r = dict(g)
        if g.get("ww1_broadcast_pt") and g.get("time_pt"):
            r["time_pt"] = min(g["time_pt"], g["ww1_broadcast_pt"])  # broadcast window starts earlier
        for ev in events_from_row(r, "nfl", r.get("radio"), r.get("source"), False):
            put(ev)
    for g in nfl["playoffs"]:
        for ev in events_from_row(g, "nfl", g.get("radio"), g.get("source"), False):
            put(ev)
    for g in ncaaf_rows:
        if g["date"].endswith("TBD"):
            continue  # dateless entries (Cal ACC list, Big Game 2027, Stanford bowl) -> flags only
        est = g.get("estimated", False)
        if "bowl candidate" in g["matchup"]:
            continue  # shading rows: shown on flagged page, not treated as games
        for ev in events_from_row(g, "ncaaf", g.get("radio"), g.get("source"), est):
            put(ev)
    for g in (mlb28 + mlb29):
        for ev in events_from_row(g, "mlb_est", None, g["source"], True):
            put(ev)
    for g in (nfl27 + nfl28 + nfl29):
        lg = "nfl_est" if g["kind"] == "nfl_est" else "nfl"
        blk = ("17:00", "20:50") if "Thursday" in g["matchup"] or "Monday night" in g["matchup"] else None
        evs = events_from_row(dict(g, time_pt=None), blk and "nfl_thu_est" or lg, None, g["source"], True) if lg == "nfl_est" else events_from_row(g, "nfl", g.get("radio"), g.get("source"), g.get("estimated", False))
        for ev in evs: put(ev)
    for g in (ncaaf27 + ncaaf28 + cfp2829 + ncaaf29 + cfp2930):
        lg = "ncaaf_est" if g["kind"] == "ncaaf_est" else "ncaaf"
        for ev in events_from_row(g, lg, None, g["source"], True):
            put(ev)

    days = []
    d = datetime(2026, 11, 25)
    end = datetime(2029, 12, 31)
    while d <= end:
        iso = d.date().isoformat()
        evs = sorted(buckets.get(iso, []), key=lambda x: x["start"])
        # free = complement of busy inside awake window 06:00-23:30
        busy = [(e["start"], e["end"]) for e in evs if e["start"] != e["end"]]
        merged = []
        for s, e in busy:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append([s, e]); merged[-1] = (merged[-1][0], e)
        free, cur = [], "06:00"
        for s, e in merged:
            if s > cur: free.append((cur, s))
            cur = max(cur, e)
        if cur < "23:30": free.append((cur, "23:30"))
        days.append({"date": iso, "busy": evs, "free": [{"start": s, "end": e} for s, e in free],
                     "free_day": not busy})
        d += timedelta(days=1)
    with open(os.path.join(OUT, "free_days.json"), "w") as f:
        json.dump({"generated": GEN_AT, "awake_window": "06:00-23:30 PT", "days": days}, f, indent=1)
    # vacation windows = consecutive free days >= 3
    runs, cur = [], None
    for day in days:
        if day["free_day"]:
            if cur is None: cur = [day["date"], day["date"]]
            else: cur[1] = day["date"]
        else:
            if cur: runs.append(cur)
            cur = None
    if cur: runs.append(cur)
    vac = []
    for a, b in runs:
        n = (datetime.fromisoformat(b) - datetime.fromisoformat(a)).days + 1
        if n >= 3:
            vac.append({"start": a, "end": b, "days": n,
                        "max_1wk": n >= 7, "max_2wk": n >= 14, "max_3wk": n >= 21,
                        "fit": {"1wk": n >= 7, "2wk": n >= 14, "3wk": n >= 21}})
    with open(os.path.join(OUT, "vacation.json"), "w") as f:
        json.dump({"generated": GEN_AT, "windows": vac,
                   "years": {y: [v for v in vac if v["start"].startswith(y)] for y in ("2027", "2028", "2029")}}, f, indent=1)
    flags = (["MLB"] + mlb.get("flags", []) + ["NFL"] + nfl.get("flags", []) + ["RADIO"] + RADIO_MAP.get("flags", []) +
             ["NCAAF", "Stanford December 2026 bowl date TBA; all Dec Saturdays flagged potentially busy until announced.",
              "Cal 2027 ACC game dates TBA (announced opponents only); Big Game 2027 date TBA.",
              "2028/2029 MLB, NFL, NCAAF busy maps are ESTIMATES from season patterns - no official schedules released yet (MLB 2028 confirmed not released via statsapi query 2026-11-25).",
              "Warriors (95.7), Sharks (KFOX 98.5), MLS Quakes broadcasts researched but excluded from busy data (optional scope - user decision).",
              "Super Bowl LXIII (2029) site verified Las Vegas; date assumed 2nd Sunday Feb 11, 2029 - estimate.",
              "Potential KNBR MLB postseason broadcasts Oct 2027/Oct 2028/Oct 2029 depend on Giants/A's qualifying - October days cannot be guaranteed free until standings known."]
             )
    with open(os.path.join(OUT, "flags.json"), "w") as f:
        json.dump({"generated": GEN_AT, "flags": flags}, f, indent=1)
    print(f"free_days: {len(days)} days; free-day runs >=3d: {len(vac)}; "
          f"2027 windows: {len([v for v in vac if v['start'].startswith('2027')])}, "
          f"2028: {len([v for v in vac if v['start'].startswith('2028')])}, "
          f"2029: {len([v for v in vac if v['start'].startswith('2029')])}")

if __name__ == "__main__":
    build_all()
