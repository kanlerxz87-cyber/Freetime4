#!/usr/bin/env python3
"""
Estimate builders for seasons whose schedules are NOT yet officially released
(confirmed empty from official sources on 2026-11-25: MLB 2028/2029, NFL 2027-2029,
NCAAF 2027-2029).

EVERY emitted row has: status="ESTIMATE", sourceUrl="" and an explanatory note.
This is deliberate: the user asked for estimates to plan vacations, and the site
marks them everywhere (tables, scoreboard, executive summary). Nothing estimated
is presented as verified.

Methods (all documented on the site's methodology page)
-------------------------------------------------------
MLB 2028/2029 : shift the OFFICIAL 2027 schedule forward 364 days (2028) /
                728 days (2029). 364 days = exactly 52 weeks, so weekday
                alignment, weekend series patterns, the All-Star break and
                holiday series are preserved. Postseason slots are estimated
                from the verified 2026 postseason spacing (relative to last
                regular-season day), since 2027 postseason dates are not yet
                announced.
MLB 2027 TBD  : games with official dates but MLB-API placeholder times get the
                home team's median 2026 start time for that weekday class
                (status ESTIMATED-TIME, date still officially verified).
NFL 2027-2029 : NFL season anchors (verified 2020-2026 pattern): Week 1 is the
                Thursday after Labor Day; Super Bowl = Week 1 Thursday + 157 days
                (held for 2023-2027 seasons; SB LXI Feb 14, 2027 verified).
                49ers: 3 preseason games + 17 regular games (one per week,
                rotating typical national/local windows), opponents TBD.
                Westwood One national windows follow the 2026 actual WW1
                broadcast pattern (TNF/SNF/MFN pregame times from the live page).
NCAAF 2027-29 : anchored on VERIFIED announced non-conference matchups
                (official/tracked announcements, links on site), then a standard
                12-game slate on consecutive autumn Saturdays; Big Game estimated
                on the Saturday before Thanksgiving with alternating venue
                (2026 verified at Cal; 129th meeting). Kickoffs estimated from
                each team's verified 2026 average kickoff.
"""
import json
import os
import statistics
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "site")
PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")

EST_STATUS = "ESTIMATE"


def est_row(**kw):
    row = {
        "id": kw["id"], "datePT": kw["datePT"], "startPT": kw["startPT"],
        "sport": kw["sport"], "category": kw["category"], "type": kw.get("type", ""),
        "matchup": kw["matchup"], "away": kw.get("away", "TBD"), "home": kw.get("home", "TBD"),
        "venue": kw.get("venue", "TBD"), "priority": kw.get("priority", "high"),
        "radio": kw.get("radio", ""), "blocks": kw.get("blocks", True),
        "status": EST_STATUS, "sourceUrl": "", "sourceNote": kw.get("note", "ESTIMATE — official schedule not yet released"),
    }
    if "week" in kw:
        row["week"] = kw["week"]
    return row


def load_raw(name):
    with open(os.path.join(RAW, name)) as f:
        return json.load(f)


def load_games(year):
    with open(os.path.join(OUT, f"games_{year}.json")) as f:
        return json.load(f)["games"]


def save_games(year, rows):
    rows.sort(key=lambda r: (r["datePT"], r["startPT"] or "99:99"))
    with open(os.path.join(OUT, f"games_{year}.json"), "w") as f:
        json.dump({"year": year, "count": len(rows), "games": rows}, f, separators=(",", ":"))


# ------------------------------------------------------------------ MLB
def mlb_tbd_times_2027():
    """Official 2027 dates with placeholder times -> estimate start from the home
    team's verified 2026 median slot (weekday class: Mon-Thu / Fri-Sat / Sun)."""
    games = load_games(2027)
    raw26 = load_raw("mlb_2026.json")
    teams = {}
    for y in (2026, 2027):
        for t in load_raw(f"mlb_teams_{y}.json")["teams"]:
            teams[t["id"]] = t
    # 2026 verified median start (Pacific) per home team & weekday class
    med = {}
    buckets = {}
    for g in raw26["games"]:
        if g["type"] != "R" or not g["startUTC"] or (4 <= int(g["startUTC"][11:13]) <= 12):
            continue
        dt = datetime.fromisoformat(g["startUTC"].replace("Z", "+00:00")).astimezone(PT)
        h = teams.get(g["homeId"], {}).get("abbr", "?")
        cls = "fri-sat" if dt.weekday() in (4, 5) else ("sun" if dt.weekday() == 6 else "mon-thu")
        buckets.setdefault((h, cls), []).append(dt.hour * 60 + dt.minute)
    for k, v in buckets.items():
        med[k] = statistics.median(v)
    changed = 0
    for g in games:
        if g["sport"] == "MLB" and g["status"] == "ESTIMATED-TIME":
            dt = datetime.fromisoformat(g["datePT"]).date()
            cls = "fri-sat" if dt.weekday() in (4, 5) else ("sun" if dt.weekday() == 6 else "mon-thu")
            key = (g["home"], cls)
            if key not in med:
                key = (g["home"], "mon-thu")
            if key in med:
                mins = int(med[key])
                g["startPT"] = f"{mins // 60:02d}:{mins % 60:02d}"
                g["sourceNote"] = "Date VERIFIED via official MLB schedule (gameday link); start time ESTIMATED from the club's verified 2026 median first pitch for this weekday class (MLB has not announced this game's time)."
                changed += 1
            else:
                g["startPT"] = "19:05"
                g["sourceNote"] = "Date VERIFIED via official MLB schedule; time unknown and no 2026 anchor — 7:05 PM PT assumed. Flagged."
                changed += 1
    save_games(2027, games)
    print(f"MLB 2027 estimated times: {changed}")


def post_spacing():
    # 2026 verified postseason spacing (offset from final regular-season day)
    raw26 = load_raw("mlb_2026.json")
    r26 = sorted([g for g in raw26["games"] if g["type"] == "R"], key=lambda g: g["date"])
    last26 = date.fromisoformat(r26[-1]["date"])
    spacing = []
    for typ in ("F", "D", "L", "W"):
        days = sorted(g["date"] for g in raw26["games"] if g["type"] == typ)
        spacing.append((typ, (date.fromisoformat(days[0]) - last26).days, (date.fromisoformat(days[-1]) - last26).days))
    return spacing


def mlb_postseason_estimates(year, reg_end):
    """Estimated postseason slots for a season whose playoff dates are not announced.
    Uses the verified 2026 spacing (Wild Card +2..+4, DS +6..+13, LCS +14..+22, WS +26..+31
    days after the final regular-season day)."""
    typemap = {"F": "Wild Card Series", "D": "Division Series", "L": "League Championship Series", "W": "World Series"}
    n_games = {"F": 3, "D": 5, "L": 7, "W": 7}
    rows = []
    seen = set()
    for typ, off0, off1 in post_spacing():
        d0 = reg_end + timedelta(days=off0)
        d1 = reg_end + timedelta(days=off1)
        span = max(1, (d1 - d0).days)
        step = max(1, span // n_games[typ])
        for i in range(n_games[typ]):
            dd = d0 + timedelta(days=min(i * step, span))
            key = (typ, dd.isoformat())
            if key in seen:
                continue
            seen.add(key)
            rows.append(est_row(
                id=f"mlb-post-{year}-{typ}-{i}",
                datePT=dd.isoformat(), startPT="17:07" if typ == "W" else "17:03",
                sport="MLB", category="MLB-other", type=typemap[typ],
                matchup=f"{typemap[typ]} game {i+1} - teams TBD",
                venue="TBD", priority="standard",
                radio="National radio; Westwood One carries select MLB postseason games (not confirmed for this round)",
                note=f"ESTIMATE - MLB postseason dates for {year} not announced (official API has no postseason for {year} as of 2026-11-25). Pattern estimate from VERIFIED 2026 spacing: {typemap[typ]} = +{off0}..+{off1} days after the final regular-season day ({reg_end.isoformat()})."))
    return rows


def mlb_shift(from_year=2027, to_years=(2028, 2029)):
    base = load_games(from_year)
    spacing = post_spacing()
    print("2026 postseason offsets from last regular day:", spacing)

    for to in to_years:
        shift = 364 * (to - from_year)
        rows = []
        for g in base:
            nd = (date.fromisoformat(g["datePT"]) + timedelta(days=shift)).isoformat()
            rows.append({**g,
                         "id": g["id"] + f"-e{to}",
                         "datePT": nd,
                         "status": EST_STATUS,
                         "sourceUrl": "",
                         "sourceNote": f"ESTIMATE — official {to} schedule not released (confirmed empty via official MLB API 2026-11-25). Date-shifted from the OFFICIAL {from_year} schedule by {shift} days (52-week cycle preserves weekday patterns, All-Star break, holiday series). Matchups/home-away may change when MLB releases the real {to} schedule."})
        reg_rows = [r for r in rows if r["sport"] == "MLB" and r["type"] == "Regular season"]
        last_day = max(date.fromisoformat(r["datePT"]) for r in reg_rows)
        rows += mlb_postseason_estimates(to, last_day)
        save_games(to, rows)
        print(f"MLB {to} estimate rows: {len(rows)}")


# ------------------------------------------------------------------ NFL
def labor_days():
    # US Labor Day = first Monday of September
    out = {}
    for y in (2026, 2027, 2028, 2029):
        d = date(y, 9, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        out[y] = d
    return out


def nfl_estimates():
    labor = labor_days()
    # verified anchors: 2026 wk1 Thu = Sep 10, 2026 (data) and Labor Day 2026 = Sep 7 -> wk1 = Labor Day + 3 days
    for season in (2027, 2028, 2029):
        wk1_thu = labor[season] + timedelta(days=3)
        rows = []
        radio_9 = "KNBR 680 AM / 104.5 FM (2026 flagship pattern)"
        # 49ers preseason (3 games, Thursday/Friday window, opponents TBD)
        for i, off in enumerate((-21, -14, -7)):
            d = wk1_thu + timedelta(days=off)
            rows.append(est_row(id=f"nfl-sf-pre-{season}-{i}", datePT=d.isoformat(), startPT="18:00",
                                sport="NFL", category="NFL-49ers", type="Preseason", week=0,
                                matchup=f"49ers preseason game {i+1} — opponent TBD",
                                venue="TBD (Levi's Stadium if home)", priority="high", radio=radio_9,
                                note=f"ESTIMATE — {season} NFL schedule not released (confirmed empty via ESPN/NFL 2026-11-25). Preseason pattern: 3 games, final one ~1 week before Week 1 (verified 2026 pattern)."))
        # 49ers regular season: one game per week, rotating typical windows
        slots = ["13:05", "13:25", "13:05", "13:25", "16:05", "13:25", "17:15", "13:05", "13:25", "16:25", "13:25", "13:05", "13:25", "13:25", "17:15", "13:25", "13:25"]
        sundays = [wk1_thu + timedelta(days=3 + 7 * i) for i in range(17)]
        # week 1 may be a special opener (2026: Melbourne Thursday night); keep Sunday generic
        for i, (d, s) in enumerate(zip(sundays, slots)):
            is_home = i % 2 == 0
            rows.append(est_row(id=f"nfl-sf-reg-{season}-{i+1}", datePT=d.isoformat(), startPT=s,
                                sport="NFL", category="NFL-49ers", type="Regular season", week=i + 1,
                                matchup=f"49ers Week {i+1} — opponent TBD",
                                venue="Levi's Stadium, Santa Clara (if home)" if is_home else "TBD (road)",
                                priority="high", radio=radio_9,
                                note=f"ESTIMATE — {season} NFL schedule not released. Pattern: 17 regular games, one per week (verified structure); window estimated from typical national/local slots. Opponent, exact date/day and window change when NFL releases the {season} schedule (typically May {season}."))
        # 49ers postseason placeholder windows (if qualified)
        wc0 = wk1_thu + timedelta(days=3 + 7 * 17 + 8)
        for name, off, note_off in (("Wild Card", 0, "+8d after Week 18"), ("Divisional", 7, "+15d"), ("Conference Championship", 14, "+22d")):
            d = wc0 + timedelta(days=off)
            rows.append(est_row(id=f"nfl-sf-post-{season}-{name.replace(' ', '')}", datePT=d.isoformat(), startPT="15:30",
                                sport="NFL", category="NFL-49ers", type="Postseason", week=None,
                                matchup=f"49ers playoff window — {name} (only if 49ers qualify)",
                                venue="TBD", priority="high", radio=radio_9,
                                note=f"ESTIMATE — {season} postseason windows ({note_off} pattern, verified 2020-2026). Only applies if 49ers qualify; treat as a possible busy window."))
        # Westwood One national weekly windows (pattern from live WW1 2026 page)
        ww1_radio = "Westwood One on KNBR 680 AM / 104.5 FM (Bay Area WW1 affiliate)"
        for w in range(18):
            thu = wk1_thu + timedelta(days=7 * w)
            sun = thu + timedelta(days=3)
            mon = thu + timedelta(days=4)
            rows.append(est_row(id=f"ww1-tnf-{season}-{w+1}", datePT=thu.isoformat(), startPT="16:30",
                                sport="NFL", category="WW1", type="Thursday Night Football (national radio)",
                                matchup=f"TNF Week {w+1} — teams TBD", venue="TBD", priority="high", radio=ww1_radio,
                                note="ESTIMATE — weekly WW1 TNF window; 2026 actuals show 7:30 PM ET broadcast start (16:30 PT) with kickoff ~8:15 PM ET."))
            rows.append(est_row(id=f"ww1-snf-{season}-{w+1}", datePT=sun.isoformat(), startPT="16:30",
                                sport="NFL", category="WW1", type="Sunday Night Football (national radio)",
                                matchup=f"SNF Week {w+1} — teams TBD", venue="TBD", priority="high", radio=ww1_radio,
                                note="ESTIMATE — weekly WW1 SNF window; 2026 actuals show 7:30 PM ET broadcast start, kickoff 8:20 PM ET."))
            rows.append(est_row(id=f"ww1-mnf-{season}-{w+1}", datePT=mon.isoformat(), startPT="16:00",
                                sport="NFL", category="WW1", type="Monday Night Football (national radio)",
                                matchup=f"MNF Week {w+1} — teams TBD", venue="TBD", priority="high", radio=ww1_radio,
                                note="ESTIMATE — weekly WW1 MNF window; 2026 actuals show 7:00 PM ET broadcast start, kickoff 8:15 PM ET."))
        # Super Bowl (WW1 national; SB LXI verified Feb 14 2027; later estimated)
        sb = wk1_thu + timedelta(days=157)
        rows.append(est_row(id=f"ww1-sb-{season}", datePT=sb.isoformat(), startPT="15:30",
                            sport="NFL", category="WW1", type="Super Bowl (national radio)",
                            matchup=f"Super Bowl {'LXII' if season==2027 else 'LXIII' if season==2028 else 'LXIV'} — teams TBD", venue="TBD", priority="high", radio=ww1_radio,
                            note="ESTIMATE for date via verified Week-1-Thursday + 157 days rule (held 2023-2027). Westwood One is the national radio home of the Super Bowl (verified for SB LXI)."))
        existing = load_games(season)
        existing += rows
        save_games(season, existing)
        print(f"NFL/WW1 {season} estimate rows: {len(rows)}; season total: {len(existing)}")


# ------------------------------------------------------------------ NCAAF
NCAAF_ANCHORS = [
    # verified announced matchups (season, date, matchup, venue, team, source)
    (2027, "2027-09-11", "Vanderbilt at Stanford", "Stanford Stadium, Stanford, CA", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2027, "2027-11-27", "Notre Dame at Stanford", "Stanford Stadium, Stanford, CA", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2027, "2027-09-04", "California at UCLA", "Rose Bowl, Pasadena, CA", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2028, "2028-09-02", "UCLA at California", "California Memorial Stadium, Berkeley, CA", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2028, "2028-09-09", "San Jose State at California", "California Memorial Stadium, Berkeley, CA", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2028, "2028-09-16", "California at Minnesota", "Hunting Bank Stadium, Minneapolis, MN", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2028, "2028-09-02", "Stanford at Fresno State", "Valley Children's Stadium, Fresno, CA", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2028, "2028-09-16", "Portland State at Stanford", "Stanford Stadium, Stanford, CA", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2028, "2028-10-14", "Stanford at Notre Dame", "Notre Dame Stadium, Notre Dame, IN", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2029, "2029-09-01", "Fresno State at Stanford", "Stanford Stadium, Stanford, CA", "Stanford", "https://fbschedules.com/ncaa/stanford/"),
    (2029, "2029-09-01", "Wisconsin at California", "California Memorial Stadium, Berkeley, CA", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2029, "2029-09-08", "California at Wyoming", "War Memorial Stadium, Laramie, WY", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
    (2029, "2029-09-15", "California at UCLA", "Rose Bowl, Pasadena, CA", "California", "https://superwestsports.com/future-nonconference-cfb-schedules-for-programs-in-west/"),
]


def ncaaf_estimates():
    for season in (2027, 2028, 2029):
        rows = []
        # kickoff anchors from verified 2026 actuals (median start per team)
        stats = {}
        for label in ("Stanford", "California"):
            d = load_raw(f"ncaaf_{label.lower()}_2026.json")
            times = []
            for e in d["events"]:
                dt = datetime.fromisoformat(e["dateUTC"].replace("Z", "+00:00")).astimezone(PT)
                times.append(dt.hour * 60 + dt.minute)
            stats[label] = int(statistics.median(times)) if times else 990  # 16:30

        def fmt(label):
            m = stats[label]
            return f"{m // 60:02d}:{m % 60:02d}"

        used_dates = set()
        for (s, dd, matchup, venue, label, src) in NCAAF_ANCHORS:
            if s != season:
                continue
            row = est_row(
                id=f"ncaaf-{label.lower()}-anchor-{dd}", datePT=dd, startPT=fmt(label),
                sport="NCAAF", category=f"NCAAF-{label}", type="Regular season (announced matchup)",
                matchup=matchup, venue=venue, priority="high",
                radio=("KNBR 680/104.5 (The Sports Leader)" if label == "Stanford" else "810 AM KSFO"),
            )
            row["sourceUrl"] = src
            row["sourceNote"] = ("Announced non-conference matchup (future-schedules tracking consistent with official "
                                 "team communications); DATE per tracker - kickoff time ESTIMATED from verified 2026 median. "
                                 "Subject to conference TV selection.")
            row["status"] = "PARTIAL-VERIFIED"
            rows.append(row)
            used_dates.add(dd)

        # Big Game estimate (Sat before Thanksgiving; venue alternates; 2026 verified at Cal = 129th)
        bg = {2027: (date(2027, 11, 20), "Stanford"),
              2028: (date(2028, 11, 18), "California"),
              2029: (date(2029, 11, 17), "Stanford")}
        d, label = bg[season]
        opp = "California" if label == "Stanford" else "Stanford"
        row = est_row(
            id=f"ncaaf-biggame-{season}", datePT=d.isoformat(), startPT="16:30",
            sport="NCAAF", category=f"NCAAF-{label}", type="Big Game (est. date)",
            matchup=f"{opp} at {label}", venue=("Stanford Stadium" if label == "Stanford" else "California Memorial Stadium"),
            priority="high",
            radio=("KNBR 680/104.5 (The Sports Leader)" if label == "Stanford" else "810 AM KSFO"),
            note="ESTIMATE - Big Game date/venue not yet scheduled. Estimated from verified pattern: Saturday before Thanksgiving, venue alternating (2026 verified at Cal, 129th meeting).",
        )
        rows.append(row)
        used_dates.add(d.isoformat())

        # fill to 12 games on consecutive Saturdays
        def first_saturday(y):
            return labor_days()[y] - timedelta(days=2)
        sat = first_saturday(season)
        anchored_per_team = {}
        for r in rows:
            anchored_per_team.setdefault(r["category"], set()).add(r["datePT"])
        gnum = 1
        while gnum <= 12:
            dd = sat.isoformat()
            for label in ("Stanford", "California"):
                n_have = sum(1 for r in rows if r["category"] == f"NCAAF-{label}")
                if n_have >= 12 or dd in anchored_per_team.get(f"NCAAF-{label}", set()):
                    continue
                home = (n_have % 2 == 0)
                rows.append(est_row(
                    id=f"ncaaf-{label.lower()}-{season}-{gnum}-{label}", datePT=dd,
                    startPT=fmt(label),
                    sport="NCAAF", category=f"NCAAF-{label}", type="Regular season (est.)",
                    matchup=("ACC/other opponent TBD (home)" if home else f"{label} at ACC/other opponent TBD (road)"),
                    venue=("Home stadium (opponent TBD)" if home else "TBD (road)"),
                    priority="high",
                    radio=("KNBR 680/104.5 (The Sports Leader)" if label == "Stanford" else "810 AM KSFO"),
                    note=f"ESTIMATE - {season} schedule not released. Standard 12-game slate on consecutive Saturdays (verified structure); date slot estimated, opponent and kickoff unknown.",
                ))
            gnum += 1
            sat += timedelta(days=7)
        existing = load_games(season)
        existing += rows
        save_games(season, existing)
        print(f"NCAAF {season} estimate rows: {len(rows)}; season total: {len(existing)}")


if __name__ == "__main__":
    mlb_tbd_times_2027()
    mlb_shift(2027, (2028, 2029))
    # 2027 postseason dates are not announced yet (official API: none). Add pattern estimates
    # so late Sept/Oct 2027 is conservatively marked busy, consistent with 2028/2029.
    g27 = load_games(2027)
    reg27 = [r for r in g27 if r["sport"] == "MLB" and r["type"] == "Regular season"]
    last27 = max(date.fromisoformat(r["datePT"]) for r in reg27)
    g27 += mlb_postseason_estimates(2027, last27)
    save_games(2027, g27)
    print(f"MLB 2027 postseason estimate rows appended; season total: {len(g27)}")
    nfl_estimates()
    ncaaf_estimates()
    print("ESTIMATES DONE")
