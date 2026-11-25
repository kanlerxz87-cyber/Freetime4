#!/usr/bin/env python3
"""Build calendar-site/data/*.json and calendar-site/*.html from the verified CSV inputs in calendar-site/src/.

Standard library only. Every data row keeps the official source URL it was
recorded with. Values that are not confirmed stay blank and are listed on the
Flagged for Review page. Nothing is estimated or filled in.
"""
import csv
import datetime as dt
import html
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "calendar-site"
SRC, DATA, DOCS = SITE / "src", SITE / "data", SITE
PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
BUILD_DATE = "2026-11-25"

# Average durations in minutes (see data/src/durations.csv)
DUR = {"MLB": 158, "NFL": 182, "NCAAF": 206}

RANGE_START = dt.date(2026, 11, 25)
RANGE_END = dt.date(2027, 9, 30)
MLB_ZERO_VERIFIED_END = dt.date(2027, 9, 26)  # feed covers through regular-season end
NFL_LOADED_END = dt.date(2027, 1, 10)         # last Westwood One NFL date fetched
NCAA_LOADED_END = dt.date(2026, 11, 28)       # last Stanford / Cal 2026 date fetched

# Official source URLs (all fetched during this session)
SRC_TEAMS = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
SRC_SEASON = "https://statsapi.mlb.com/api/v1/seasons/2027?sportId=1"
SRC_FEED = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027"
SRC_GIANTS = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&teamId=137"
SRC_ATH = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&teamId=133"
SRC_ALLSTAR = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2027-07-13"
SRC_2026 = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026"
            "&gameType=S,R,F,D,L,W&startDate=2026-11-01&endDate=2026-12-31")
SRC_2028 = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028"
SRC_WW = "https://www.westwoodonesports.com/nfl-schedule/"
SRC_WW_STATIONS = "https://www.westwoodonesports.com/station-finder/"
SRC_49 = "https://www.49ers.com/schedule/"
SRC_MLB_ATT = "https://www.mlb.com/news/mlb-increased-attendance-3rd-straight-season"
SRC_GS_SCHED = "https://gostanford.com/sports/football/schedule"
SRC_CAL_SCHED = "https://calbears.com/sports/football/schedule/2026"
SRC_SPORTSLEADER = "https://www.thesportsleader.com/stanfordfootball/"
SRC_INSIDERADIO = ("https://www.insideradio.com/free/stanford-football-taps-two-alumni-for-2026-radio-broadcasts/"
                   "article_1576291f-2466-42af-98a1-1c9676d60d46.html")
SRC_SACBEE = "https://www.sacbee.com/sports/article300334119.html"
SRC_VISUALFOODIE = "https://visualfoodie.com/complete-sf-giants-2026-broadcast-schedule/"
SRC_NFL_DUR = "https://nflanalytic.com/explainer-how-long-is-an-nfl-game.html"
SRC_NCAA_DUR = ("https://www.academicjobs.com/en-us/higher-education-news/"
                "how-long-is-a-college-football-game-average-326-explained-academicjobs-12610")
SRC_STANFORD_BOWL = "https://gostanford.com/news/2026/11/21/stanford-secures-bowl-berth-with-big-game-win"
SRC_LASB = "https://lasuperbowlhc.com/"


def esc(x):
    return html.escape("" if x is None else str(x))


def read(name):
    with (SRC / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pt_from_utc(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=UTC).astimezone(PT)


def pretty(hm):
    if not hm:
        return ""
    h, m = map(int, hm.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"


def daterange(a, b):
    for i in range((b - a).days + 1):
        yield a + dt.timedelta(i)


def link(url, text=None):
    if not url:
        return ""
    return f'<a href="{esc(url)}" rel="noopener">{esc(text or "source")}</a>'


def status_cell(text):
    cls = "ok" if text.startswith("Verified") else "flag"
    return f'<span class="pill {cls}">{esc(text)}</span>'


def table(headers, rows, cls=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


# ---------------------------------------------------------------- load inputs
teams = read("mlb_clubs.csv")
team = {int(t["teamId"]): t for t in teams}
HIGH_MLB = {137, 133}

daily = {}
for r in read("mlb_2027_league_daily_counts.csv"):
    daily[dt.date.fromisoformat(r["date"])] = int(r["mlb_games"])
allstar = read("mlb_2027_allstar.csv")
for a in allstar:
    d = dt.date.fromisoformat(a["officialDate"])
    daily[d] = daily.get(d, 0) + 1  # All-Star Game is missing from the regular feed count


def mlb_count(d):
    if d > MLB_ZERO_VERIFIED_END:
        return None  # not published
    return daily.get(d, 0)


ga_rows = []
for fname, src, club in [("mlb_2027_giants_schedule.csv", SRC_GIANTS, 137),
                         ("mlb_2027_athletics_schedule.csv", SRC_ATH, 133)]:
    for r in read(fname):
        p = pt_from_utc(r["gameDateUTC"])
        ga_rows.append({
            "club": team[club]["name"], "club_id": club,
            "gamePk": int(r["gamePk"]), "date_pt": p.date().isoformat(), "time_pt": p.strftime("%H:%M"),
            "utc": r["gameDateUTC"],
            "gameType": {"R": "Regular season", "S": "Spring training"}.get(r["gameType"], r["gameType"]),
            "away": team[int(r["awayId"])]["name"], "home": team[int(r["homeId"])]["name"],
            "source_url": src,
        })

events = []  # calendar events
seen_pk = set()
for g in ga_rows:
    if g["gamePk"] in seen_pk:
        continue
    seen_pk.add(g["gamePk"])
    events.append({
        "date": g["date_pt"], "group": "MLB", "subgroup": "Giants / Athletics (high priority)",
        "title": f'{g["away"]} at {g["home"]}', "start": g["time_pt"], "dur": DUR["MLB"], "tbd": False,
        "priority": "High", "url": g["source_url"],
        "note": f'gamePk {g["gamePk"]}; {g["gameType"]}; 2:38 average from mlb.com; start from gameDate (startTimeTBD flag not captured)',
    })

for a in allstar:
    events.append({
        "date": a["officialDate"], "group": "MLB", "subgroup": "All-Star Game",
        "title": "MLB All-Star Game (Wrigley Field, Chicago)", "start": None, "dur": DUR["MLB"], "tbd": True,
        "priority": "Standard", "url": a["source_url"],
        "note": "Game exists in the date query (gamePk 853074, gameType A) but is missing from the season count; start time TBD in feed",
    })

westwood = []
for r in read("westwood_one_nfl_radio.csv"):
    d = dt.date.fromisoformat(r["date_et"])
    tt = dt.time.fromisoformat(r["time_et"])
    p = dt.datetime.combine(d, tt, tzinfo=ET).astimezone(PT)
    westwood.append({
        "date_et": r["date_et"], "time_et": r["time_et"], "date_pt": p.date().isoformat(),
        "time_pt": p.strftime("%H:%M"), "matchup": r["matchup"], "venue": r["venue"], "tag": r["tag"],
        "event_id": r["event_id"], "url": f"https://www.westwoodonesports.com/events/{r['event_id']}",
        "conflict": "",
    })

ncaa = read("nfl_ncaaf.csv")

# 49ers entries with times; drop duplicates that conflict with a Westwood listing (flagged)
for r in ncaa:
    if r["league"] == "NFL" and r["team"] == "San Francisco 49ers" and r["date_pt"] and r["time_pt"]:
        dup = [w for w in westwood if w["date_pt"] == r["date_pt"] and "San Francisco 49ers" in w["matchup"]]
        if dup:
            dup[0]["conflict"] = f'49ers.com lists {pretty(r["time_pt"])} PT for this game; see Flagged for Review'
            continue
        events.append({
            "date": r["date_pt"], "group": "NFL", "subgroup": "49ers (high priority)",
            "title": f'49ers vs {r["opponent"]}' if r["home_away"] == "Home" else f'49ers at {r["opponent"]}',
            "start": r["time_pt"], "dur": DUR["NFL"], "tbd": False, "priority": "High", "url": r["source_url"],
            "note": f'{r["status"]}; {r["broadcast"]}',
        })

for w in westwood:
    events.append({
        "date": w["date_pt"], "group": "NFL", "subgroup": "National radio (Westwood One)",
        "title": w["matchup"] + (f" ({w['tag']})" if w["tag"] else ""),
        "start": w["time_pt"], "dur": DUR["NFL"], "tbd": False,
        "priority": "High" if "San Francisco 49ers" in w["matchup"] else "Standard",
        "url": w["url"],
        "note": f'Westwood One event {w["event_id"]}; listed {w["time_et"]} ET' +
                (f'; CONFLICT: {w["conflict"]}' if w["conflict"] else ""),
    })

for r in ncaa:
    if r["league"] == "NCAAF" and r["date_pt"] and r["time_pt"] and r["status"].startswith("Upcoming"):
        events.append({
            "date": r["date_pt"], "group": "NCAAF", "subgroup": r["team"],
            "title": f'{r["team"]} vs {r["opponent"]}' if r["home_away"] == "Home" else f'{r["team"]} at {r["opponent"]}',
            "start": r["time_pt"], "dur": DUR["NCAAF"], "tbd": False, "priority": "High",
            "url": r["source_url"], "note": r["broadcast"],
        })

for e in events:
    e.setdefault("note", "")

# ---------------------------------------------------------------- calendar
calendar_days = []
for d in daterange(RANGE_START, RANGE_END):
    n = mlb_count(d)
    st = "unpublished" if n is None else ("verified-none" if n == 0 else "has-games")
    evs = [e for e in events if e["date"] == d.isoformat()]
    evs.sort(key=lambda e: (e["start"] is None, e["start"] or ""))
    calendar_days.append({"date": d.isoformat(), "weekday": d.strftime("%A"),
                          "mlb": {"count": n, "status": st}, "events": evs})

# ---------------------------------------------------------------- windows
windows = []
cur = []
for d in daterange(RANGE_START, MLB_ZERO_VERIFIED_END):
    if mlb_count(d) == 0:
        cur.append(d)
    elif cur:
        windows.append(cur)
        cur = []
if cur:
    windows.append(cur)


def coverage_notes(d):
    notes = []
    if d <= NFL_LOADED_END:
        notes.append("NFL: national radio and 49ers only")
    else:
        notes.append("NFL: no schedule loaded")
    if d <= NCAA_LOADED_END:
        notes.append("NCAAF: Stanford and Cal only")
    else:
        notes.append("NCAAF: no schedule loaded (Stanford bowl game date not published)")
    return "; ".join(notes)


def loaded(d):
    return [e for e in events if e["date"] == d.isoformat() and e["group"] != "MLB"]


win_json = []
for w in windows:
    win_json.append({
        "start": w[0].isoformat(), "end": w[-1].isoformat(), "days": len(w),
        "mlb_verified": "No MLB games in Stats API feed for every day in window",
        "nfl_ncaaf_coverage": "; ".join(sorted({coverage_notes(w[0]), coverage_notes(w[-1])})),
        "loaded_nfl_ncaaf_events": sum(len(loaded(d)) for d in w),
    })

thresholds = [1, 7, 14, 21]
threshold_json = {str(t): [x for x in win_json if x["days"] >= t] for t in thresholds}

# ---------------------------------------------------------------- flagged items
FLAGS = [
    ("F01", "MLB", "All-Star Game 2027-07-13 (gamePk 853074)",
     "Daily total from the season feed omitted this game (gameType A). The date query shows it. Daily count and total corrected to include it; the season total becomes 2,900. Start time TBD in feed.",
     "Corrected", SRC_ALLSTAR),
    ("F02", "MLB", "2027 postseason (Sep 27 to Oct 31) and 2028 / 2029 schedules",
     "Not published. Feed shows 0 games for 2028. Free-day status is blank for these dates; no estimates were generated.",
     "Not published", SRC_2028),
    ("F03", "MLB", "Start times for Giants and Athletics games",
     "Times come from gameDate. The startTimeTBD flag was not captured during transcription, so some times may be placeholders.",
     "Unverified", SRC_GIANTS),
    ("F04", "MLB", "Start times and games for the other 28 clubs",
     "Only Giants and Athletics games are loaded with times. Hours on other MLB game days show Free time not available.",
     "Incomplete", SRC_FEED),
    ("F05", "NFL", "Westwood One vs 49ers.com: Dec 17, 2026 (49ers at Chargers)",
     "Westwood One lists 7:30 PM ET (4:30 PM PT). 49ers.com lists 5:15 PM PT. Both kept in source files; calendar uses Westwood time with a CONFLICT note.",
     "Conflict", SRC_49),
    ("F06", "NFL", "Westwood One vs 49ers.com: Jan 3, 2027 (Eagles at 49ers)",
     "Westwood One lists 7:30 PM ET (4:30 PM PT). 49ers.com lists 5:20 PM PT.",
     "Conflict", SRC_49),
    ("F07", "NFL", "49ers Week 18 at Arizona Cardinals",
     "Date and kickoff not published on the 49ers schedule page. Row left blank.",
     "Unverified", SRC_49),
    ("F08", "NFL", "NFL games other than national radio and 49ers",
     "Only Westwood One national games and 49ers games were loaded. Other NFL games for the same dates are not in the data, so NFL free-time claims are partial.",
     "Incomplete", SRC_WW),
    ("F09", "NFL", "2027 NFL regular season, preseason, and playoffs",
     "Not published in fetched sources. Westwood One list ends Jan 10, 2027.",
     "Not published", SRC_WW),
    ("F10", "NFL", "Super Bowl LXI date and venue (not verified)",
     "Not confirmed from an official NFL or Westwood One page in this build; the date appears only in secondary search results (not fetched). Not added to the calendar.",
     "Unverified", SRC_LASB),
    ("F11", "NCAAF", "Stanford bowl game",
     "The recap link on the fetched gostanford.com schedule page has a slug reading 'secures bowl berth'. The article was not fetched. Bowl opponent, date and time are not published in any fetched source, so Stanford Dec to Jan windows are not verified.",
     "Not published", SRC_STANFORD_BOWL),
    ("F13", "NCAAF", "Cal radio frequency and call letters",
     "The fetched calbears.com schedule page links live audio to The Varsity Network and gives no frequency. The 810 AM frequency and the call letters (KGO or KSFO) appear only in search results. Not used.",
     "Unverified", SRC_CAL_SCHED),
    ("F14", "NCAAF", "Stanford radio flagship",
     "A 2013 Stanford page (search result, not fetched) says KNBR 1050 AM. Inside Radio (search result, not fetched) says KNBR 680 AM / 104.5 FM and KTCT 1050 AM. Not resolved; thesportsleader.com (audio link on the fetched gostanford.com page) was not fetched.",
     "Conflict", SRC_INSIDERADIO),
    ("F15", "NCAAF", "Stanford and Cal 2027 schedules",
     "Not published. No 2027 college data in the repository.",
     "Not published", SRC_GS_SCHED),
    ("F16", "Radio", "Giants radio (KNBR 680 AM / 104.5 FM)",
     "Only secondary sources. The official mlb.com radio page could not be fetched.",
     "Unverified", SRC_VISUALFOODIE),
    ("F17", "Radio", "A's Bay Area radio (KNEW 960 AM)",
     "Sacramento Bee (2025) says KNEW 960 carries Bay Area games; a 2022 listing names Bloomberg 960. Secondary only.",
     "Unverified", SRC_SACBEE),
    ("F18", "Radio", "Station schedules for per-game verification",
     "Westwood One's station finder is market-level and does not publish per-game carriage. KNBR's schedule page was not reached. Per-game radio carriage cannot be verified from the sources in this repository.",
     "Unverified", SRC_WW_STATIONS),
    ("F19", "Radio", "Other sports on Bay Area radio",
     "Not researched in this pass.",
     "Unverified", SRC_WW_STATIONS),
    ("F20", "Durations", "MLB average game length",
     "Official figure is 2:38 (158 min). The brief assumed about 150 minutes; 158 is used.",
     "Verified", SRC_MLB_ATT),
    ("F21", "Durations", "NFL and NCAAF average game length",
     "NFL median is from a secondary analysis (3:02); the brief's 180 min plus 15 to 30 min halftime is not separately verified. NCAAF 3:26 is secondary.",
     "Unverified", SRC_NFL_DUR),
    ("F22", "Time zone", "PST requested",
     "Calendar uses America/Los_Angeles: PST in winter, PDT in summer. Times are labelled PT.",
     "Note", SRC_TEAMS),
    ("F23", "Prior work", "RADIOSF site, Vacation windows, ScheduleFreeTime",
     "RADIOSF fetch failed. The other sites were not fetched. None are used as sources.",
     "Not used", SRC_TEAMS),
    ("F24", "Repo review", "Repository state",
     "Repo contained only README.md. No prior schedule data or code. Data here is built from fetched sources only.",
     "Note", SRC_TEAMS),
    ("F25", "NFL", "49ers preseason and Week 1 to 11 kickoff times",
     "Kickoff times are not in the fetched text for these past games. Blank in the table.",
     "Unverified", SRC_49),
]

# ---------------------------------------------------------------- sources
SOURCES = [
    ("MLB Stats API: teams (30 clubs)", SRC_TEAMS, "Club IDs and names", "Verified"),
    ("MLB Stats API: 2027 season dates", SRC_SEASON, "Regular season, All-Star, postseason dates", "Verified"),
    ("MLB Stats API: 2027 schedule feed", SRC_FEED, "Season query 2,899 games; plus All-Star Game (date query) = 2,900", "Verified"),
    ("MLB Stats API: Giants 2027", SRC_GIANTS, "194 entries", "Verified"),
    ("MLB Stats API: Athletics 2027", SRC_ATH, "193 entries", "Verified"),
    ("MLB Stats API: All-Star date query", SRC_ALLSTAR, "2027-07-13 All-Star Game", "Verified"),
    ("MLB Stats API: 2026 Nov to Dec", SRC_2026, "Zero MLB games in Nov and Dec 2026", "Verified"),
    ("MLB Stats API: 2028 season", SRC_2028, "0 games (not published)", "Verified (empty)"),
    ("mlb.com: 2025 average game time 2:38", SRC_MLB_ATT, "MLB game length", "Verified"),
    ("Westwood One NFL schedule", SRC_WW, "35 national NFL radio events", "Verified"),
    ("Westwood One station finder", SRC_WW_STATIONS, "NFL SF stations", "Verified (market level)"),
    ("49ers.com schedule", SRC_49, "49ers 2026 games and radio stations", "Verified"),
    ("Stanford football schedule", SRC_GS_SCHED, "Stanford 2026 games and results", "Verified"),
    ("Cal football schedule 2026", SRC_CAL_SCHED, "Cal 2026 games and results", "Verified"),
    ("thesportsleader.com Stanford page (link on gostanford.com)", SRC_SPORTSLEADER, "Audio link only; page not fetched", "Link only"),
    ("Inside Radio: Stanford 2026 radio", SRC_INSIDERADIO, "Stanford radio (secondary)", "Secondary"),
    ("Sacramento Bee: A's radio", SRC_SACBEE, "A's Bay Area station (secondary)", "Secondary"),
    ("visualfoodie: Giants broadcast 2026", SRC_VISUALFOODIE, "Giants KNBR (secondary)", "Secondary"),
    ("nflanalytic: NFL game length", SRC_NFL_DUR, "NFL median 3:02 (secondary)", "Secondary"),
    ("academicjobs: college football length", SRC_NCAA_DUR, "NCAAF 3:26 (secondary)", "Secondary"),
    ("Stanford recap link slug (Nov 21, 2026)", SRC_STANFORD_BOWL, "Link slug on gostanford.com schedule page reads bowl berth; article not fetched", "Secondary"),
    ("Super Bowl LXI page (search result only)", SRC_LASB, "Not fetched; not used", "Not used"),
    ("RADIOSF prior-work site", "https://buffedlizard55-lab.github.io/RADIOSF/#2026-09-27", "Not used", "Fetch failed"),
    ("mlb.com Giants radio page", "https://www.mlb.com/giants/fans/radio", "Not used", "Fetch failed"),
    ("mlb.com A's radio page", "https://www.mlb.com/athletics/fans/radio", "Not used", "Fetch failed"),
]

# ---------------------------------------------------------------- write data
DATA.mkdir(exist_ok=True)
(DOCS / "assets").mkdir(parents=True, exist_ok=True)
(DOCS / "data").mkdir(parents=True, exist_ok=True)


def write_json(name, obj):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    (DATA / name).write_text(text + "\n", encoding="utf-8")
    (DOCS / "data" / name).write_text(text + "\n", encoding="utf-8")


write_json("mlb_clubs.json", [
    {"teamId": int(t["teamId"]), "name": t["name"], "abbreviation": t["abbreviation"], "league": t["league"],
     "division": t["division"], "location": t["locationName"],
     "priority": "High" if int(t["teamId"]) in HIGH_MLB else "Standard", "source": SRC_TEAMS}
    for t in teams])

write_json("mlb_daily_counts_2027.json", [
    {"date": d.isoformat(), "mlb_games": mlb_count(d), "status": calendar_days[(d - RANGE_START).days]["mlb"]["status"],
     "source": SRC_FEED if d >= dt.date(2027, 1, 1) else SRC_2026}
    for d in daterange(RANGE_START, MLB_ZERO_VERIFIED_END)])

write_json("mlb_giants_athletics_2027.json", [
    {"club": g["club"], "gamePk": g["gamePk"], "date_pt": g["date_pt"], "time_pt": g["time_pt"],
     "gameDateUTC": g["utc"], "gameType": g["gameType"], "away": g["away"], "home": g["home"],
     "source": g["source_url"]} for g in ga_rows])

write_json("westwood_nfl_radio.json", [
    {k: w[k] for k in ("date_et", "time_et", "date_pt", "time_pt", "matchup", "venue", "tag", "event_id", "url", "conflict")}
    for w in westwood])

write_json("nfl_ncaaf.json", [
    {"league": r["league"], "team": r["team"], "date_pt": r["date_pt"], "time_pt": r["time_pt"],
     "opponent": r["opponent"], "home_away": r["home_away"], "result": r["result"], "status": r["status"],
     "broadcast": r["broadcast"], "venue": r["venue"], "source": r["source_url"], "notes": r["notes"]}
    for r in ncaa])

write_json("radio.json", [
    {"entity": r["entity"], "network_or_station": r["network_or_station"], "call_letters": r["call_letters"],
     "band": r["band"], "role": r["role"], "source": r["source_url"], "status": r["status"], "notes": r["notes"]}
    for r in read("radio.csv")])

write_json("durations.json", [
    {"sport": r["sport"], "metric": r["metric"], "minutes": int(r["minutes"]) if r["minutes"] else None,
     "label": r["label"], "source": r["source_url"], "status": r["status"], "notes": r["notes"]}
    for r in read("durations.csv")])

write_json("free_windows.json", {
    "method": ("A day is MLB-free only if the MLB Stats API feed has zero games for it (all 30 clubs). "
               "Free-window tables use MLB only. NFL and NCAAF coverage is partial, so windows are not "
               "fully verified across all tracked sports."),
    "mlb_verified_range": [RANGE_START.isoformat(), MLB_ZERO_VERIFIED_END.isoformat()],
    "windows": win_json,
    "thresholds": threshold_json,
    "not_published": ["2027-09-27 to 2027-10-31 (postseason)", "2028 season (feed returns 0 games)",
                      "2029 season (not queried; no schedule published)",
                      "NFL 2027 season and playoffs after 2027-01-10", "Stanford and Cal 2027 schedules"],
})

write_json("calendar.json", {"generated": BUILD_DATE, "range": [RANGE_START.isoformat(), RANGE_END.isoformat()],
                             "durations_min": DUR, "days": calendar_days})

write_json("flagged.json", [{"id": f[0], "area": f[1], "item": f[2], "issue": f[3], "status": f[4], "source": f[5]}
                            for f in FLAGS])
write_json("sources.json", [{"source": s[0], "url": s[1], "used_for": s[2], "status": s[3]} for s in SOURCES])

# ---------------------------------------------------------------- site
CSS_HREF = "assets/site.css"
NAV = [("index.html", "Home"), ("calendar.html", "Calendar"), ("analysis.html", "Free windows"),
       ("mlb.html", "MLB"), ("nfl.html", "NFL"), ("ncaaf.html", "NCAAF"), ("radio.html", "Radio"),
       ("flagged.html", "Flagged for Review"), ("sources.html", "Sources")]


def page(title, active, body, head_extra=""):
    nav = "".join(f'<a href="{h}"{" class=on" if h == active else ""}>{esc(lbl)}</a>' for h, lbl in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Free Time</title><link rel="stylesheet" href="{CSS_HREF}">{head_extra}</head>
<body><header><div class="brand">Free Time <small>Bay Area (94122) · when AM/FM sports are off the air</small></div>
<nav>{nav}</nav></header>
<main>{body}</main>
<footer>Times are Pacific (PT: PST in winter, PDT in summer). Built {BUILD_DATE}. Blank cells are unverified and listed on <a href="flagged.html">Flagged for Review</a>. Every row links its official source.</footer>
</body></html>
"""


def write_page(name, title, active, body, head_extra=""):
    (DOCS / name).write_text(page(title, active, body, head_extra), encoding="utf-8")


n_zero_mlb = sum(len(w) for w in windows)
n_2027_zero = sum(1 for d in daterange(dt.date(2027, 1, 1), MLB_ZERO_VERIFIED_END) if mlb_count(d) == 0)
n_2027_games = sum(v for d, v in daily.items() if d.year == 2027)
longest = max(windows, key=len)
two_seven = [w for w in windows if w[0].year == 2027 and len(w) >= 1]
jul_days = [w[0].isoformat() for w in windows if w[0].year == 2027 and w[0].month == 7]

# Index
index_body = f"""
<section class="hero">
<h1>When are you free from live sports on Bay Area radio?</h1>
<p>Tracks all 30 MLB clubs (Giants and Athletics high priority), NFL (49ers high priority, national Westwood One radio), Stanford and Cal football, and the Bay Area radio stations that carry them. Built from official sources. Unverified items are blank and listed on the <a href="flagged.html">Flagged for Review</a> page.</p>
</section>
<section class="exec">
<h2>Executive summary</h2>
<div class="cards">
<div class="card ok"><div class="big">{len(longest)} days</div><b>Longest MLB-free stretch verified</b><p>No MLB game on any day from <b>{longest[0].strftime('%b %-d, %Y')}</b> to <b>{longest[-1].strftime('%b %-d, %Y')}</b> (all 30 clubs; Stats API). NFL national radio games fall inside this span until Jan 10, 2027, so it is not NFL-free.</p></div>
<div class="card warn"><div class="big">{len(jul_days)} single days</div><b>In-season MLB-free days in July 2027</b><p>Only <b>{' and '.join(dt.date.fromisoformat(d).strftime('%b %-d') for d in jul_days)}</b>, 2027. Jul 13 has the All-Star Game.</p></div>
<div class="card flag"><div class="big">Not published</div><b>2027 postseason, 2028, 2029</b><p>No official schedule. Free-day status is left blank rather than estimated.</p></div>
</div>
<p class="note">MLB 2027 feed: {n_2027_games:,} games (season total {sum(daily.values()):,} including the All-Star Game). Days with zero games: {n_zero_mlb} (Nov 25, 2026 to Sep 26, 2027, all verified).</p>
</section>
<section>
<h2>Where to go next</h2>
<div class="links">
<a class="tile" href="calendar.html"><b>Calendar</b><span>Day-by-day scoreboard, Pacific time, hour-by-hour free time</span></a>
<a class="tile" href="analysis.html"><b>Free windows</b><span>1, 7, 14, 21-day windows and every MLB-free day</span></a>
<a class="tile" href="mlb.html"><b>MLB</b><span>30 clubs, Giants and Athletics 2027 schedules, daily counts</span></a>
<a class="tile" href="nfl.html"><b>NFL</b><span>49ers 2026 games and national Westwood One radio list</span></a>
<a class="tile" href="ncaaf.html"><b>Stanford and Cal</b><span>2026 results and remaining games</span></a>
<a class="tile" href="radio.html"><b>Radio</b><span>Flagship stations and what can and cannot be verified</span></a>
<a class="tile flagtile" href="flagged.html"><b>Flagged for Review</b><span>{len(FLAGS)} items: conflicts, gaps, unverified values</span></a>
<a class="tile" href="sources.html"><b>Sources</b><span>Every source with its verification status</span></a>
</div></section>
"""
write_page("index.html", "Home", "index.html", index_body)

# Calendar shell (JS renders)
cal_body = """
<section><h1>Calendar (Pacific time)</h1>
<p class="note">Hour-by-hour free time for each day. MLB days show the Giants and Athletics times that are loaded; other clubs' times are not loaded, so those hours read <b>Free time not available</b>. NFL and college entries are the national Westwood One list, 49ers, Stanford and Cal only.</p>
<div class="controls">
<button id="prev" type="button">&larr; Previous day</button>
<input id="dayInput" type="date" aria-label="Choose a day">
<button id="next" type="button">Next day &rarr;</button>
<button id="today" type="button">Today (PT)</button>
</div>
<div id="out"></div>
<p class="note">Average durations (blocks on the grid): MLB 2:38 (158 min, mlb.com 2025 average). NFL 3:02 (182 min, 2025 median including halftime; secondary source). NCAAF FBS 3:26 (206 min, secondary).</p>
</section>
<script src="assets/calendar.js"></script>
"""
write_page("calendar.html", "Calendar", "calendar.html", cal_body)

# Analysis
thr_rows = []
for t in thresholds:
    items = threshold_json[str(t)]
    txt = "<br>".join(f'{esc(x["start"])} to {esc(x["end"])} ({x["days"]} days)' for x in items) or "None"
    thr_rows.append([f"{t} day{'s' if t > 1 else ''}", txt, str(len(items)),
                     link(SRC_FEED, "MLB feed") + " " + link(SRC_WW, "NFL list")])
analysis_days = []
for d in daterange(RANGE_START, MLB_ZERO_VERIFIED_END):
    if mlb_count(d) != 0:
        continue
    lo = loaded(d)
    analysis_days.append([d.isoformat(), d.strftime("%a"), "0 MLB games",
                          "; ".join(esc(e["title"]) + (" " + pretty(e["start"]) if e["start"] else "") for e in lo) or "None loaded",
                          esc(coverage_notes(d)), link(SRC_2026 if d < dt.date(2027, 1, 1) else SRC_FEED, "MLB feed")])
analysis_body = f"""
<section><h1>Free windows</h1>
<p class="note">A day counts as MLB-free only when the MLB Stats API feed lists zero games for all 30 clubs. NFL and college coverage is partial (see the coverage column), so no window is fully verified across every tracked sport.</p>
<h2>Windows by length (MLB-verified)</h2>
{table(["Length", "Windows found (Nov 2026 to Sep 2027)", "Count", "Sources"], thr_rows)}
<h2>Every MLB-free day (Nov 25, 2026 to Sep 26, 2027)</h2>
{table(["Date (PT)", "Day", "MLB games", "NFL / college loaded for this day", "Coverage", "Source"], analysis_days)}
<h2>Years without official schedules</h2>
{table(["Year", "MLB", "NFL", "NCAAF", "Free windows", "Source"], [
    ["2026 (reference)", "Nov 25 to Dec 31 verified zero", "Nov 25, 2026 to Jan 10, 2027 national list", "Stanford and Cal to Nov 28", "See MLB-free table", link(SRC_2026, "MLB feed")],
    ["2027", f"{n_2027_games:,} games (incl. All-Star)", "Not published after Jan 10, 2027", "Not published", "Only verified MLB-free days listed above", link(SRC_FEED, "MLB feed")],
    ["2028", "Feed returns 0 games (not published)", "Not published", "Not published", "Blank: not estimated", link(SRC_2028, "MLB feed")],
])}
<p class="note">2029: no schedule is published in any source checked, and no MLB 2029 query was returned. Free-window cells are left blank rather than estimated (see Flagged for Review, F02).</p>
<h2>Average game durations used in the calendar</h2>
{table(["Sport", "Metric", "Minutes", "Label", "Status", "Source"], [
    [esc(r["sport"]), esc(r["metric"]), str(r["minutes"]), esc(r["label"]), status_cell(r["status"]), link(r["source_url"])]
    for r in read("durations.csv")])}
<p class="note">NFL halftime is 14 min median (secondary). The brief asked for 15 to 30 min; not separately verified.</p>
</section>
"""
write_page("analysis.html", "Free windows", "analysis.html", analysis_body)

# MLB
club_rows = [[str(t["teamId"]), esc(t["name"]), esc(t["abbreviation"]), esc(t["league"]), esc(t["division"]),
              esc(t["locationName"]), "High" if int(t["teamId"]) in HIGH_MLB else "", link(SRC_TEAMS, "MLB Stats API")]
             for t in teams]
ga_table = [[esc(g["club"]), g["date_pt"], pretty(g["time_pt"]), esc(g["gameType"]),
             esc(f'{g["away"]} at {g["home"]}'), str(g["gamePk"]), link(g["source_url"], "Stats API")]
            for g in ga_rows]
dc_rows = [[d.isoformat(), d.strftime("%a"), str(mlb_count(d)), link(SRC_FEED if d >= dt.date(2027, 1, 1) else SRC_2026, "Stats API")]
           for d in daterange(RANGE_START, MLB_ZERO_VERIFIED_END)]
mlb_body = f"""
<section><h1>MLB, 2027</h1>
<p class="note">Clubs: all 30 from the official Stats API. Giants (SF) and Athletics (ATH) are high priority. The table shows the teams' schedules; shared games appear in both teams' lists. Start times are Pacific (converted from gameDate).</p>
<h2>All 30 clubs</h2>
{table(["Team ID", "Club", "Abbr", "League", "Division", "Location", "Priority", "Source"], club_rows)}
<h2>Giants and Athletics 2027 (all entries)</h2>
{table(["Club", "Date (PT)", "Start (PT)", "Type", "Matchup", "gamePk", "Source"], ga_table)}
<h2>Daily MLB games, all clubs (Nov 25, 2026 to Sep 26, 2027)</h2>
<p class="note">Zero-game days are verified from the feed. The All-Star Game (Jul 13) is added from a date query. Dates after Sep 26, 2027 are not published.</p>
{table(["Date (PT)", "Day", "MLB games", "Source"], dc_rows)}
</section>
"""
write_page("mlb.html", "MLB", "mlb.html", mlb_body)

# NFL
ww_table = []
for w in westwood:
    conflict_cell = f'<span class="pill flag">{esc(w["conflict"])}</span>' if w["conflict"] else ""
    ww_table.append([w["date_pt"], pretty(w["time_pt"]), esc(w["matchup"]), esc(w["tag"]), esc(w["venue"]),
                     esc(w["time_et"] + " ET"), conflict_cell, link(w["url"], "Westwood One")])
sf_rows = [[esc(r["team"]), r["date_pt"], pretty(r["time_pt"]), esc(r["home_away"]), esc(r["opponent"]),
            esc(r["result"]), esc(r["status"]), esc(r["broadcast"]), esc(r["venue"]), esc(r["notes"]), link(r["source_url"], "49ers.com" if "49ers" in r["source_url"] else "Source")]
           for r in ncaa if r["league"] == "NFL"]
nfl_body = f"""
<section><h1>NFL</h1>
<p class="note">49ers (high priority) and the Westwood One national NFL radio list, Nov 25, 2026 to Jan 10, 2027. Westwood times are converted from ET to PT. Conflicts are marked and listed on <a href="flagged.html">Flagged for Review</a>. 2027 season dates are not published.</p>
<h2>San Francisco 49ers, 2026</h2>
{table(["Team", "Date (PT)", "Kickoff (PT)", "Home/Away", "Opponent", "Result", "Status", "Broadcast / radio", "Venue", "Notes", "Source"], sf_rows)}
<h2>Westwood One national NFL radio (all 35 events)</h2>
{table(["Date (PT)", "Time (PT)", "Matchup", "Tag", "Venue", "Listed time", "Conflict", "Source"], ww_table)}
</section>
"""
write_page("nfl.html", "NFL", "nfl.html", nfl_body)

# NCAAF
def ncaa_rows(team_name):
    out = []
    for r in ncaa:
        if r["league"] == "NCAAF" and r["team"] == team_name:
            out.append([r["date_pt"], pretty(r["time_pt"]), esc(r["home_away"]), esc(r["opponent"]), esc(r["result"]),
                        esc(r["status"]), esc(r["broadcast"]), esc(r["venue"]), link(r["source_url"], "Official")])
    return out


ncaaf_body = f"""
<section><h1>Stanford and California football</h1>
<p class="note">2026 season, from the official school sites. Results show our side first where the source does. 2027 schedules are not published. Stanford's bowl game is not yet scheduled in these sources.</p>
<h2>Stanford (Cardinal)</h2>
{table(["Date (PT)", "Kickoff (PT)", "Home/Away", "Opponent", "Result", "Status", "Radio / TV", "Venue", "Source"], ncaa_rows("Stanford"))}
<h2>California (Golden Bears)</h2>
{table(["Date (PT)", "Kickoff (PT)", "Home/Away", "Opponent", "Result", "Status", "Radio / TV", "Venue", "Source"], ncaa_rows("California"))}
</section>
"""
write_page("ncaaf.html", "NCAAF", "ncaaf.html", ncaaf_body)

# Radio
radio_rows = [[esc(r["entity"]), esc(r["network_or_station"]), esc(r["call_letters"]), esc(r["band"]),
               esc(r["role"]), status_cell(r["status"]), esc(r["notes"]), link(r["source_url"])]
              for r in read("radio.csv")]
radio_body = f"""
<section><h1>Radio</h1>
<p class="note">Question: can each game be verified through station schedules? <b>No, not from the sources in this repository.</b> The 49ers publish per-game carriage on their official schedule page. Westwood One publishes a market-level station list, not per-game carriage. KNBR's own schedule was not reached. Flagship conflicts are listed below.</p>
{table(["Entity", "Network / station", "Call letters", "Band", "Role", "Status", "Notes", "Source"], radio_rows)}
</section>
"""
write_page("radio.html", "Radio", "radio.html", radio_body)

# Flagged
flag_rows = [[esc(f[0]), esc(f[1]), esc(f[2]), esc(f[3]), status_cell(f[4]), link(f[5], "Source")] for f in FLAGS]
flagged_body = f"""
<section><h1>Flagged for Review</h1>
<p class="note">These items do not block publication. Each is shown with its status and source. Blank values in the tables are unverified.</p>
{table(["ID", "Area", "Item", "Issue", "Status", "Source"], flag_rows)}
</section>
"""
write_page("flagged.html", "Flagged for Review", "flagged.html", flagged_body)

# Sources
src_rows = [[esc(s[0]), link(s[1], s[1]), esc(s[2]), status_cell(s[3])] for s in SOURCES]
sources_body = f"""
<section><h1>Sources</h1>
<p class="note">Official sources are the MLB Stats API, westwoodonesports.com, 49ers.com, gostanford.com and calbears.com. Secondary sources are labelled and never used alone for a verified value.</p>
{table(["Source", "URL", "Used for", "Status"], src_rows)}
</section>
"""
write_page("sources.html", "Sources", "sources.html", sources_body)

# Static assets (CSS and JS are maintained as files)
# assets live in calendar-site/assets and are used in place

print("built:", len(calendar_days), "calendar days;", len(events), "events;", len(windows), "MLB-free windows;",
      "MLB feed total", sum(daily.values()))
