#!/usr/bin/env python3
"""
build_data.py — FREE TIME VACATION dataset builder (session arena-ad020434)

Reads the raw schedule dumps in data/raw/ (fetched from MLB's official Stats API
and ESPN's public site API as a cross-check source — see research/sources.md),
plus the hand-verified Westwood One event list, and produces the site datasets:

  data/games-2026.json … data/games-2029.json   per-event rows (source per row)
  data/summary.json                             vacation-window analysis
  data/radio.json                               Bay Area AM/FM carriage
  data/durations.json                           duration assumptions
  data/flags.json                               flagged-for-review register

Every row carries:
  verified      true  = read on an official source this session
                false = cross-check / estimate (never presented as verified)
  source        official URL for manual re-check
  timeEstimated true  = start time is a modelled value (TBD in the official feed)

Scope definitions (see research/sources.md):
  core      = all MLB + all NFL + Stanford/Cal NCAAF + Westwood One national NFL
  no-st     = core minus MLB spring training / exhibitions
  sf-radio  = only games broadcast on SF Bay Area AM/FM (Giants, A's, 49ers,
              Stanford, Cal, Westwood One national NFL)
"""

import json
import os
import re
from datetime import datetime, date, time, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data")
TODAY = date(2026, 11, 25)          # session date; rows are future-facing
PT = timezone(timedelta(hours=-8))  # nominal; DST handled by utc_to_pt()

# ---------------------------------------------------------------- durations
DURATIONS = {
    "mlb_regular": 158,     # 2:38 — MLB 2025 pace-of-play report
    "mlb_spring": 150,      # estimate
    "mlb_exhibition": 150,  # estimate
    "mlb_allstar": 180,     # estimate
    "mlb_postseason": 184,  # 3:04 — postseason medians
    "nfl_regular": 192,     # 3:12 incl. 12-min halftime
    "nfl_preseason": 185,   # estimate
    "nfl_playoffs": 198,    # estimate
    "nfl_superbowl": 240,   # extended halftime
    "nfl_probowl": 150,     # flag format
    "cfb": 204,             # 3:24 incl. 20-min halftime
}

# ------------------------------------------------- Pacific time conversion
def _nth_weekday(year, month, weekday, n):
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)

def utc_to_pt(iso_utc):
    """'2027-04-01T17:35:00Z' -> (date(2027,4,1), '10:35') in PST/PDT."""
    s = iso_utc.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s).astimezone(timezone.utc)
    y = dt.year
    dst_start = datetime.combine(_nth_weekday(y, 3, 6, 2), time(2), tzinfo=timezone.utc) - timedelta(hours=8)
    dst_end = datetime.combine(_nth_weekday(y, 11, 6, 1), time(2), tzinfo=timezone.utc) - timedelta(hours=7)
    off = -7 if dst_start <= dt.replace(tzinfo=timezone.utc) < dst_end else -8
    local = dt.replace(tzinfo=timezone.utc) + timedelta(hours=off)
    return local.date(), f"{local.hour:02d}:{local.minute:02d}"

# ---------------------------------------------------------------- helpers
def load_raw(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def new_id(prefix, n):
    return f"{prefix}-{n}"

events = []          # master list
flag_items = []      # flagged-for-review register (id, title, detail, source)

def add(ev):
    events.append(ev)

# ================================================================ MLB 2027
# Official game-by-game slate from MLB Stats API (verified). Per-row source:
# mlb.com/gameday/<gamePk> (official game page).
MLB_SRC = "https://www.mlb.com/gameday/{pk}"
MLB_DATE_SRC = "https://www.mlb.com/schedule/{d}"
GIANTS = "San Francisco Giants"
ATHLETICS = "Athletics"

def mlb_radio(home, away):
    """SF Bay Area AM/FM carriage we can assert from official team/network info."""
    if home == GIANTS or away == GIANTS:
        return "KNBR 680 AM / 104.5 FM (Giants flagship)"
    if home == ATHLETICS or away == ATHLETICS:
        return "iHeart Sports 960 AM / KNEW (A's Bay Area)"
    return None

def build_mlb_2027():
    seen = set()
    n = 0
    for m in ["02", "03", "04", "05", "06", "07", "08", "09", "10", "11"]:
        raw = load_raw(f"mlb_2027_{m}.json")
        for d in raw.get("dates", []):
            for g in d.get("games", []):
                pk = g.get("gamePk")
                if pk in seen:
                    continue
                seen.add(pk)
                n += 1
                gd = g.get("gameDate", "")
                tbd = g.get("status", {}).get("startTimeTBD", False)
                pdate, ptime = utc_to_pt(gd) if gd else (date.fromisoformat(g.get("officialDate", "2027-01-01")), None)
                away = g["teams"]["away"]["team"]["name"]
                home = g["teams"]["home"]["team"]["name"]
                gt = g.get("gameType", "R")
                cat = {"S": "spring", "R": "regular", "A": "allstar", "E": "exhibition",
                       "F": "postseason", "D": "postseason", "L": "postseason", "W": "postseason"}.get(gt, "regular")
                dur = {"spring": DURATIONS["mlb_spring"], "regular": DURATIONS["mlb_regular"],
                       "allstar": DURATIONS["mlb_allstar"], "exhibition": DURATIONS["mlb_exhibition"],
                       "postseason": DURATIONS["mlb_postseason"]}[cat]
                radio = mlb_radio(home, away)
                add({
                    "id": f"mlb-{pk}",
                    "sport": "MLB",
                    "date": pdate.isoformat(),
                    "time": ptime,
                    "timeEstimated": bool(tbd),
                    "durMin": dur,
                    "category": cat,
                    "label": f"{away} at {home}",
                    "away": away, "home": home,
                    "venue": g.get("venue", {}).get("name"),
                    "priority": home in (GIANTS, ATHLETICS) or away in (GIANTS, ATHLETICS),
                    "radio": radio,
                    "sfRadio": radio is not None,
                    "westwoodOne": False,
                    "scope": "core",
                    "certain": True,
                    "verified": True,
                    "source": MLB_SRC.format(pk=pk),
                    "note": "Official MLB schedule (Stats API). Start time estimated." if tbd else "",
                })

# --- MLB 2027 postseason + special events (dates TBA -> estimated, flagged)
def est_mlb_special_2027():
    rows = [
        ("2027-07-12", "17:00", 180, "MLB Home Run Derby (Wrigley Field)", "special", True,
         "https://www.mlb.com/news/mlb-2027-schedule-released",
         "Date verified by MLB release; start time estimated."),
        ("2027-07-13", "19:00", 180, "MLB All-Star Game (Wrigley Field)", "allstar", True,
         "https://www.mlb.com/news/mlb-2027-schedule-released",
         "Date verified by MLB release; start time estimated."),
    ]
    for i, (d, t, dur, label, cat, ver, src, note) in enumerate(rows):
        add({"id": f"mlb27-special-{i}", "sport": "MLB", "date": d, "time": t,
             "timeEstimated": True, "durMin": dur, "category": cat, "label": label,
             "venue": "Wrigley Field", "priority": False, "radio": None, "sfRadio": False,
             "westwoodOne": False, "scope": "core", "certain": True, "verified": ver,
             "source": src, "note": note})
    # Postseason window (dates TBA). Modelled on the 2026 postseason pattern
    # (official API data/raw/mlb_2026_10.json). Whole window is ESTIMATED.
    win = [
        ("2027-09-28", "2027-10-04", "MLB Wild Card Series (dates TBA — estimated window)", 184),
        ("2027-10-05", "2027-10-11", "MLB Division Series (dates TBA — estimated window)", 184),
        ("2027-10-12", "2027-10-21", "MLB League Championship Series (dates TBA — estimated window)", 184),
        ("2027-10-22", "2027-11-03", "MLB World Series (dates TBA — estimated window)", 184),
    ]
    for i, (d1, d2, label, dur) in enumerate(win):
        add({"id": f"mlb27-post-{i}", "sport": "MLB", "date": d1, "time": "17:00",
             "timeEstimated": True, "durMin": dur, "category": "postseason", "label": label,
             "dateEnd": d2, "venue": None, "priority": False, "radio": None, "sfRadio": False,
             "westwoodOne": False, "scope": "core", "certain": False, "verified": False,
             "source": "https://www.mlb.com/schedule",
             "note": "MLB has not announced 2027 postseason dates; modelled on 2026 pattern. ESTIMATE."})

# --- MLB 2028 / 2029: no schedule released (official API returns empty — kept
# as evidence). Daily slate rows over estimated season spans. ESTIMATES.
def est_mlb_slate(year, st_start, st_end, reg_start, reg_end, asg_day, post_start, post_end):
    d = date.fromisoformat(st_start)
    end = date.fromisoformat(reg_end)
    while d <= end:
        if d < date.fromisoformat(reg_start):
            cat, dur, label = "spring", DURATIONS["mlb_spring"], f"MLB spring training slate (~{year}, games TBA)"
        else:
            cat, dur, label = "regular", DURATIONS["mlb_regular"] + 165, f"MLB regular-season slate ({year} Openers TBA)"
        add({"id": f"mlb{year}-{d.isoformat()}", "sport": "MLB", "date": d.isoformat(),
             "time": "10:05" if cat == "regular" else "11:05", "timeEstimated": True,
             "durMin": 745 if cat == "regular" else 480, "category": cat, "label": label + " — ESTIMATE, matchups not released",
             "priority": False, "radio": None, "sfRadio": True, "westwoodOne": False,
             "scope": "core", "certain": False, "blocking": True, "verified": False,
             "source": f"https://www.mlb.com/schedule",
             "note": "No MLB schedule released for this season. Daily slate modelled on season structure. ESTIMATE."})
        d += timedelta(days=1)
    # All-Star break + postseason windows
    add({"id": f"mlb{year}-asg", "sport": "MLB", "date": asg_day, "time": "19:00",
         "timeEstimated": True, "durMin": DURATIONS["mlb_allstar"], "category": "allstar",
         "label": f"MLB All-Star Game {year} (site/date TBA — estimated)", "priority": False,
         "radio": None, "sfRadio": False, "westwoodOne": False, "scope": "core",
         "certain": False, "verified": False, "source": "https://www.mlb.com/schedule",
         "note": "ESTIMATE. All-Star site/date not announced."})
    d = date.fromisoformat(post_start)
    end = date.fromisoformat(post_end)
    while d <= end:
        add({"id": f"mlb{year}-post-{d.isoformat()}", "sport": "MLB", "date": d.isoformat(),
             "time": "17:00", "timeEstimated": True, "durMin": DURATIONS["mlb_postseason"],
             "category": "postseason", "label": f"MLB postseason slate {year} (window — ESTIMATE)",
             "priority": False, "radio": None, "sfRadio": False, "westwoodOne": False,
             "scope": "core", "certain": False, "verified": False,
             "source": "https://www.mlb.com/schedule",
             "note": "Postseason window modelled on recent seasons. ESTIMATE."})
        d += timedelta(days=1)

# ================================================================ NFL 2026
# Cross-check source: ESPN public scoreboard dump. Official source link per row:
# nfl.com by-week pages (Week 12 verified directly against nfl.com this session;
# other weeks flagged cross-check). Times from ESPN feed, converted to PT.
def build_nfl_2026():
    off_src = "https://www.nfl.com/schedules/2026/by-week/week-{w}"
    ww_labels = {lbl for _d, _t, lbl, _w, _e in WW_EVENTS if "TBA" not in lbl}
    for w in range(12, 19):
        raw = load_raw(f"nfl_2026_reg_w{w}.json")
        for e in raw.get("events", []):
            name = e.get("name", "")
            gd = e.get("date", "")
            if not gd:
                continue
            pdate, ptime = utc_to_pt(gd)
            if pdate < TODAY:
                continue
            comp = e.get("competitions", [{}])[0]
            venue = None
            try:
                venue = comp.get("venue", {}).get("fullName")
            except Exception:
                pass
            is49 = "San Francisco 49ers" in name
            on_ww = name in ww_labels
            add({"id": f"nfl-2026-{w}-{e.get('id', pdate.isoformat())}", "sport": "NFL",
                 "date": pdate.isoformat(), "time": ptime, "timeEstimated": False,
                 "durMin": DURATIONS["nfl_regular"], "category": "regular",
                 "label": name, "venue": venue,
                 "priority": is49,
                 "radio": "KNBR 680 AM / 104.5 FM, KSAN 107.7 FM (49ers Radio Network)" if is49
                          else ("Westwood One national (SF: KNBR 680/104.5, KTCT 1050)" if on_ww else None),
                 "sfRadio": is49 or on_ww,
                 "westwoodOne": on_ww,
                 "scope": "core", "certain": True,
                 "verified": w == 12,
                 "source": off_src.format(w=w),
                 "note": "" if w == 12 else "Cross-checked via ESPN public scoreboard; verify at official link. See flagged.html."})
    # Postseason rounds (dates from ESPN; official hub linked). Teams TBD.
    rounds = [
        (1, "2027-01-16", "2027-01-18", "NFL Wild Card", 6),
        (2, "2027-01-23", "2027-01-24", "NFL Divisional Playoff", 4),
        (3, "2027-01-31", "2027-01-31", "NFL Conference Championships", 2),
        (4, "2027-02-14", "2027-02-14", "Super Bowl LXI (SoFi Stadium)", 1),
    ]
    for w, d1, d2, label, ngames in rounds:
        is_sb = w == 4
        d = date.fromisoformat(d1)
        end = date.fromisoformat(d2)
        k = 0
        while d <= end:
            k += 1
            slots = [(("15:30" if is_sb else "13:00"), DURATIONS["nfl_superbowl"] if is_sb else DURATIONS["nfl_playoffs"])]
            if not is_sb:
                slots.append(("17:20", DURATIONS["nfl_playoffs"]))
            for t, dur in slots:
                add({"id": f"nfl-2026-post-w{w}-{d.isoformat()}-{t}", "sport": "NFL",
                     "date": d.isoformat(),
                     "time": t,
                     "timeEstimated": True,
                     "durMin": dur,
                     "category": "postseason", "label": label + (" (kickoff ≈3:30 PM PT — EST)" if is_sb else " (games TBA)"),
                     "priority": False,
                     "radio": "Westwood One national (SF: KNBR 680/104.5, KTCT 1050)",
                     "sfRadio": True, "westwoodOne": True,
                     "scope": "core", "certain": True,
                     "verified": is_sb,
                     "source": "https://lasuperbowlhc.com/" if is_sb else "https://www.nfl.com/schedules",
                     "note": "Round dates set; teams/times TBA (est.)" if not is_sb
                             else "Date/venue verified (LA host committee + NFL). Kickoff not published — estimated 3:30 PM PT."})
            d += timedelta(days=1)
    add({"id": "nfl-2027-probowl", "sport": "NFL", "date": "2027-02-06", "time": "12:00",
         "timeEstimated": True, "durMin": DURATIONS["nfl_probowl"], "category": "special",
         "label": "NFL Pro Bowl Games 2027 (week before Super Bowl — ESTIMATE)", "priority": False,
         "radio": None, "sfRadio": False, "westwoodOne": False, "scope": "core",
         "certain": False, "verified": False, "source": "https://www.nfl.com/schedules",
         "note": "Pro Bowl week assumed the Saturday before Super Bowl LXI. ESTIMATE."})

# ================================================================ NFL 2027-2029 (est)
def est_nfl_season(year):
    """Weekly window rows: schedule not released. Kickoff = Thursday after Labor Day."""
    labor = _nth_weekday(year, 9, 0, 1)          # first Monday of September
    kickoff = labor + timedelta(days=3)           # Thursday
    pre_start = kickoff - timedelta(weeks=4)      # Hall of Fame week (est.)
    # Preseason: 3 weeks of Thu-Sun windows
    for wk in range(0, 4):
        base = pre_start + timedelta(weeks=wk)
        days = [0, 1, 2, 3] if wk > 0 else [0]   # Thu-Sun; HOF game Thursday (est.)
        for dow in days:
            d = base + timedelta(days=dow)
            if d >= kickoff:
                continue
            label = ("NFL/Hall of Fame Game (est.)" if wk == 0 else
                     f"NFL preseason Week {wk} — games TBA (est.)")
            add({"id": f"nfl{year}-pre-{d.isoformat()}", "sport": "NFL", "date": d.isoformat(),
                 "time": "17:00", "timeEstimated": True, "durMin": DURATIONS["nfl_preseason"],
                 "category": "preseason", "label": label, "priority": False,
                 "radio": "Westwood One/local flags (est.)", "sfRadio": True,
                 "westwoodOne": wk == 0, "scope": "core", "certain": False, "verified": False,
                 "source": "https://www.nfl.com/schedules",
                 "note": "NFL schedule not released for this season. Window ESTIMATE."})
    # Regular season: 18 weeks; windows Thu/Sat/Sun/Mon
    for wk in range(1, 19):
        thu = kickoff + timedelta(weeks=wk - 1)
        windows = [(thu, "17:15", f"NFL {year} Week {wk} — Thursday Night Football (teams TBA, est.)", True)]
        sat = thu + timedelta(days=2)
        sun = thu + timedelta(days=3)
        mon = thu + timedelta(days=4)
        if wk >= 16:
            windows.append((sat, "13:00", f"NFL {year} Week {wk} — Saturday games (teams TBA, est.)", False))
        windows.append((sun, "10:00", f"NFL {year} Week {wk} — Sunday early window (teams TBA, est.)", False))
        windows.append((sun, "13:05", f"NFL {year} Week {wk} — Sunday late window (teams TBA, est.)", False))
        windows.append((sun, "17:20", f"NFL {year} Week {wk} — Sunday Night Football (teams TBA, est.)", True))
        windows.append((mon, "17:15", f"NFL {year} Week {wk} — Monday Night Football (teams TBA, est.)", True))
        for d, t, label, w1 in windows:
            add({"id": f"nfl{year}-w{wk}-{d.isoformat()}-{t}", "sport": "NFL",
                 "date": d.isoformat(), "time": t, "timeEstimated": True,
                 "durMin": DURATIONS["nfl_regular"], "category": "regular",
                 "label": label, "priority": False,
                 "radio": "Westwood One national (SF: KNBR 680/104.5, KTCT 1050)" if w1 else None,
                 "sfRadio": True, "westwoodOne": w1,
                 "scope": "core", "certain": False, "verified": False,
                 "source": "https://www.nfl.com/schedules",
                 "note": "Window ESTIMATE — official schedule not released."})
    # Postseason + Super Bowl (2nd Sunday of February, following year)
    sb_year = year + 1
    feb = date(sb_year, 2, 1)
    first_sun = feb + timedelta(days=(6 - feb.weekday()) % 7)
    sb = first_sun + timedelta(weeks=1)
    post = [
        (sb - timedelta(days=28), "NFL Wild Card (est. window)"),
        (sb - timedelta(days=21), "NFL Divisional (est. window)"),
        (sb - timedelta(days=14), "NFL Conference Championships (est. window)"),
    ]
    for d, label in post:
        for off, t in ((0, "13:00"), (1, "17:20")):
            dd = d + timedelta(days=off)
            add({"id": f"nfl{year}-post-{dd.isoformat()}-{t}", "sport": "NFL", "date": dd.isoformat(),
                 "time": t, "timeEstimated": True, "durMin": DURATIONS["nfl_playoffs"],
                 "category": "postseason", "label": label + " — ESTIMATE", "priority": False,
                 "radio": "Westwood One national (est.)", "sfRadio": True, "westwoodOne": True,
                 "scope": "core", "certain": False, "verified": False,
                 "source": "https://www.nfl.com/schedules",
                 "note": "Window ESTIMATE — official schedule not released."})
    add({"id": f"nfl{year}-sb", "sport": "NFL", "date": sb.isoformat(), "time": "15:30",
         "timeEstimated": True, "durMin": DURATIONS["nfl_superbowl"], "category": "postseason",
         "label": f"Super Bowl (est. {sb.isoformat()} — not announced)", "priority": False,
         "radio": "Westwood One national (est.)", "sfRadio": True, "westwoodOne": True,
         "scope": "core", "certain": False, "verified": False,
         "source": "https://www.nfl.com/schedules",
         "note": "ESTIMATE — Super Bowl date for this season not announced."})

# ================================================================ Stanford / Cal NCAAF
def build_cfb_2026():
    for team, key, src, radio in (
        ("Stanford", "cfb_stanford_2026", "https://gostanford.com/sports/football/schedule/2026",
         "KNBR 1050 AM / KTCT (Stanford flagship)"),
        ("California", "cfb_cal_2026", "https://calbears.com/sports/football/schedule/2026",
         "The Varsity Network live audio (AM/FM flagship unconfirmed — flagged)"),
    ):
        raw = load_raw(f"{key}.json")
        for e in raw.get("events", []):
            gd = e.get("date", "")
            if not gd:
                continue
            pdate, ptime = utc_to_pt(gd)
            if pdate < TODAY:
                continue
            name = e.get("name", "")
            verified = team == "California"
            add({"id": f"cfb-{team.lower()}-{pdate.isoformat()}", "sport": "NCAAF",
                 "date": pdate.isoformat(), "time": ptime, "timeEstimated": False,
                 "durMin": DURATIONS["cfb"], "category": "regular", "label": name,
                 "priority": True, "radio": radio,
                 "sfRadio": True, "westwoodOne": False, "scope": "core",
                 "certain": True, "verified": verified, "source": src,
                 "note": "Official schedule page read this session." if verified else
                         "Official page not machine-readable here; cross-checked via ESPN. See flagged.html."})
    # Possible Stanford bowl (record-dependent; never claimed as certain)
    add({"id": "cfb-stanford-bowl-possible", "sport": "NCAAF", "date": "2026-12-18",
         "dateEnd": "2027-01-13", "time": "12:00", "timeEstimated": True,
         "durMin": DURATIONS["cfb"], "category": "possible",
         "label": "Stanford — possible bowl game (would be scheduled here if selected)",
         "priority": True, "radio": "KNBR 1050 AM / KTCT", "sfRadio": True,
         "westwoodOne": False, "scope": "core", "certain": False, "blocking": False, "verified": False,
         "source": "https://gostanford.com/sports/football/schedule/2026",
         "note": "Not counted as busy. If Stanford reaches bowl eligibility one game may fall in this window. See flagged.html."})

def est_cfb(year):
    """Stanford/Cal slates not released: Saturdays Sep-Nov marked as possible slate."""
    d = date(year, 9, 2)
    end = date(year, 11, 27)
    while d <= end:
        for team in ("Stanford", "California"):
            add({"id": f"cfb-{team.lower()}-{year}-{d.isoformat()}", "sport": "NCAAF",
                 "date": d.isoformat(), "time": "11:00", "timeEstimated": True,
                 "durMin": DURATIONS["cfb"], "category": "regular",
                 "label": f"{team} football — game likely (schedule TBA, est.)",
                 "priority": True, "radio": None, "sfRadio": True, "westwoodOne": False,
                 "scope": "core", "certain": False, "verified": False,
                 "source": "https://gostanford.com/sports/football/schedule" if team == "Stanford"
                           else "https://calbears.com/sports/football/schedule",
                 "note": f"{team} {year} schedule not released. Saturdays in season marked busy (conservative). ESTIMATE."})
        d += timedelta(weeks=1)

# ================================================================ Westwood One (verified rows)
# Transcribed from the official schedule read this session:
# https://www.westwoodonesports.com/nfl-schedule/ — every row links its event page.
WW_SRC = "https://www.westwoodonesports.com/events/{id}"
WW_EVENTS = [
    ("2026-11-25", "16:30", "Green Bay Packers at Los Angeles Rams", "Thanksgiving Wednesday", 548511),
    ("2026-11-26", "09:30", "Chicago Bears at Detroit Lions", "NFL Thanksgiving Day Tripleheader", 548512),
    ("2026-11-26", "13:15", "Philadelphia Eagles at Dallas Cowboys", "NFL Thanksgiving Day Tripleheader", 548513),
    ("2026-11-26", "17:00", "Kansas City Chiefs at Buffalo Bills", "NFL Thanksgiving Day Tripleheader", 548514),
    ("2026-11-27", "11:30", "Denver Broncos at Pittsburgh Steelers", "NFL Black Friday Game", 548515),
    ("2026-11-29", "17:20", "Las Vegas Raiders at Cleveland Browns", "Sunday Night Football", 548502),
    ("2026-11-30", "16:00", "Carolina Panthers at Tampa Bay Buccaneers", "Monday Night Football", 548544),
    ("2026-12-03", "16:30", "Kansas City Chiefs at Los Angeles Rams", "Thursday Night Football", 548566),
    ("2026-12-06", "16:30", "Houston Texans at Pittsburgh Steelers", "Sunday Night Football", 548503),
    ("2026-12-07", "16:00", "Dallas Cowboys at Seattle Seahawks", "Monday Night Football", 548545),
    ("2026-12-10", "16:30", "Minnesota Vikings at New England Patriots", "Thursday Night Football", 548567),
    ("2026-12-13", "16:30", "Buffalo Bills at Green Bay Packers", "Sunday Night Football", 548505),
    ("2026-12-14", "16:00", "Pittsburgh Steelers at Jacksonville Jaguars", "Monday Night Football", 548546),
    ("2026-12-17", "16:30", "San Francisco 49ers at Los Angeles Chargers", "Thursday Night Football", 548568),
    ("2026-12-19", "13:30", "Seattle Seahawks at Philadelphia Eagles", "Week 15 Saturday NFL Doubleheader", 548517),
    ("2026-12-19", "17:00", "Chicago Bears at Buffalo Bills", "Week 15 Saturday NFL Doubleheader", 548518),
    ("2026-12-20", "16:30", "Detroit Lions at Minnesota Vikings", "Sunday Night Football", 548506),
    ("2026-12-21", "16:00", "New England Patriots at Kansas City Chiefs", "Monday Night Football", 548548),
    ("2026-12-24", "16:30", "Houston Texans at Philadelphia Eagles", "Thursday Night Football", 548569),
    ("2026-12-25", "09:30", "Green Bay Packers at Chicago Bears", "Christmas Day NFL Tripleheader", 548528),
    ("2026-12-25", "13:15", "Buffalo Bills at Denver Broncos", "Christmas Day NFL Tripleheader", 548531),
    ("2026-12-25", "17:00", "Los Angeles Rams at Seattle Seahawks", "Christmas Day NFL Tripleheader", 548534),
    ("2026-12-26", "13:00", "Week 16 Saturday Doubleheader TBA", "Week 16 Saturday NFL Doubleheader", 548519),
    ("2026-12-26", "17:00", "Week 16 Saturday Doubleheader TBA", "Week 16 Saturday NFL Doubleheader", 548520),
    ("2026-12-27", "16:30", "Jacksonville Jaguars at Dallas Cowboys", "Sunday Night Football", 548507),
    ("2026-12-28", "16:00", "New York Giants at Detroit Lions", "Monday Night Football", 548550),
    ("2026-12-31", "16:30", "Baltimore Ravens at Cincinnati Bengals", "Thursday Night Football", 548570),
    ("2027-01-02", "17:00", "Week 17 Saturday Doubleheader TBA", "Week 17 Saturday NFL Doubleheader", 548522),
    ("2027-01-02", "13:00", "Week 17 Saturday Doubleheader TBA", "Week 17 Saturday NFL Doubleheader", 548521),
    ("2027-01-03", "16:30", "Philadelphia Eagles at San Francisco 49ers", "Sunday Night Football", 548509),
    ("2027-01-04", "16:00", "Houston Texans at Green Bay Packers", "Monday Night Football", 548552),
    ("2027-01-09", "09:30", "Week 18 Saturday Tripleheader TBA", "Week 18 Saturday NFL Tripleheader", 548523),
    ("2027-01-09", "13:15", "Week 18 Saturday Tripleheader TBA", "Week 18 Saturday NFL Tripleheader", 548524),
    ("2027-01-09", "17:00", "Week 18 Saturday Tripleheader TBA", "Week 18 Saturday NFL Tripleheader", 548526),
    ("2027-01-10", "16:30", "Week 18 Sunday Night Football — Teams TBA", "Sunday Night Football", 548510),
]

def build_westwood_one():
    for d, t, label, window, eid in WW_EVENTS:
        add({"id": f"ww-{eid}", "sport": "NFL", "date": d, "time": t,
             "timeEstimated": "TBA" in label, "durMin": DURATIONS["nfl_regular"],
             "category": "national", "label": label + " (Westwood One national)",
             "priority": "49ers" in label,
             "radio": "Westwood One — SF: KNBR 680/104.5, KTCT 1050 AM",
             "sfRadio": True, "westwoodOne": True, "scope": "core",
             "certain": True, "verified": True,
             "source": WW_SRC.format(id=eid),
             "note": "Official Westwood One event page. ET→PT converted."})

# ================================================================ flag register
def build_flags():
    global flag_items
    flag_items = [
        {"id": "F01", "title": "MLB CBA expires 2026-12-01 — lockout risk for the 2027 season",
         "detail": "MLB's released 2027 schedule is officially published but is contingent on a new CBA. Outlets report a lockout is considered imminent. If games are lost, the free-time map shifts (more free time) and rows must be re-verified after any settlement.",
         "source": "https://sports.yahoo.com/mlb/breaking-news/article/with-lockout-imminent-rob-manfred-cant-imagine-mlb-owners-ratifying-new-cba-without-salary-cap-floor-223700548.html"},
        {"id": "F02", "title": "MLB 2027 postseason dates not announced",
         "detail": "MLB's 2027 release says postseason dates are TBA. Wild Card/DS/LCS/WS rows are ESTIMATES modelled on the 2026 pattern (official API).",
         "source": "https://www.mlb.com/news/mlb-2027-schedule-released"},
        {"id": "F03", "title": "MLB 2027 game start times flagged startTimeTBD in the official API",
         "detail": "Rows with timeEstimated=true carry placeholder/estimated times until MLB confirms. Dates and matchups are official.",
         "source": "https://www.mlb.com/schedule"},
        {"id": "F04", "title": "MLB 2028–2029 schedules not released",
         "detail": "Official Stats API returns no games (evidence kept in data/raw/mlb_2028_*.json, mlb_2029_*.json). The site shows ESTIMATED daily slate rows over estimated season spans; no invented matchups.",
         "source": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2028-03-01&endDate=2028-03-31"},
        {"id": "F05", "title": "NFL 2027–2029 schedules not released",
         "detail": "ESPN's future-season scoreboard calls return current-season fallbacks (validated and discarded). Modelled weekly window rows (TNF/SNF/MNF/Sunday windows) are ESTIMATES. Super Bowl dates after LXI are estimates (≈ 2nd Sunday of February).",
         "source": "https://www.nfl.com/schedules"},
        {"id": "F06", "title": "NFL 2026 Weeks 13–18 rows cross-checked via ESPN, not read row-by-row on nfl.com",
         "detail": "Week 12 was verified directly on nfl.com. Other remaining weeks come from the ESPN public scoreboard dump with the official nfl.com by-week page attached to every row for manual re-check. Times may shift with flex scheduling (esp. Week 18).",
         "source": "https://www.nfl.com/schedules/2026/by-week/week-13"},
        {"id": "F07", "title": "Westwood One broadcast start vs kickoff time discrepancies (inherited flag)",
         "detail": "Westwood One lists 2026-12-17 49ers at Chargers at 4:30 PM PT while 49ers.com lists 5:15 PM PST kickoff; same pattern 2027-01-03 SNF. Treated as pregame-broadcast start vs kickoff. Both values shown.",
         "source": "https://www.westwoodonesports.com/nfl-schedule/"},
        {"id": "F08", "title": "Westwood One 2026–27 postseason national windows",
         "detail": "Westwood One carries the NFL postseason per its national rights, but per-game listings post during the playoffs (its page currently ends at Week 18). Postseason rows are marked national windows with estimated times.",
         "source": "https://www.westwoodonesports.com/nfl-schedule/"},
        {"id": "F09", "title": "Stanford 2026 rows cross-checked via ESPN (gostanford.com not machine-readable here)",
         "detail": "gostanford.com's schedule page is behind bot protection in this sandbox. Dates/opponents cross-checked against ESPN's public scoreboard; Big Game (2026-11-21) was verified on gostanford.com by a prior session. Cal's official page WAS read this session.",
         "source": "https://gostanford.com/sports/football/schedule/2026"},
        {"id": "F10", "title": "Stanford possible bowl game Dec 2026 – Jan 2027",
         "detail": "If Stanford becomes bowl-eligible, one game will land between ~2026-12-18 and ~2027-01-13. Shown as a non-blocking 'possible' row (never counted as busy; days are marked with ⚠).",
         "source": "https://gostanford.com/sports/football/schedule/2026"},
        {"id": "F11", "title": "Cal Bears football AM/FM radio flagship unconfirmed",
         "detail": "Cal's official page exposes live audio via The Varsity Network, but no official AM/FM flagship page was readable this session. Flagged for manual confirmation.",
         "source": "https://calbears.com/sports/football/schedule/2026"},
        {"id": "F12", "title": "A's relocation affects radio and venues across the window",
         "detail": "Athletics home games 2025–2027 in West Sacramento (Bay Area radio: iHeart Sports 960 AM / KNEW); Las Vegas planned from 2028 with no radio plan announced. 2028+ A's rows carry no radio claim.",
         "source": "https://www.sacbee.com/sports/article300334119.html"},
        {"id": "F13", "title": "Other Bay Area radio sports are NOT in the core free-time definition",
         "detail": "Warriors (NBA) air on 95.7 The Game and Sharks (NHL) games are heard locally; Westwood One also carries NCAA basketball (March Madness), golf and more. These overlap Feb–Mar vacation windows. The brief's 'what free means' list does not include them, so the core map excludes them; if you want them counted, say so and they will be folded in. See radio.html.",
         "source": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824"},
        {"id": "F14", "title": "Game durations are researched averages, not per-game guarantees",
         "detail": "MLB 158 min (2025 report), NFL 192 min, NCAAF 204 min. Postseason/Super Bowl use longer estimates. Extra innings/OT can exceed these.",
         "source": "https://www.lines.com/guides/how-long-is-baseball-game/1523"},
        {"id": "F15", "title": "Interpretation choices in the vacation-window scenarios",
         "detail": "The brief says both 'games scheduled to be played' and 'live over the radio in SF'. The site reports three scenarios (core; core minus MLB spring training; SF-radio-only) so both readings are visible. Feb–Mar 2027 windows differ sharply between them.",
         "source": "https://www.mlb.com/news/mlb-2027-schedule-released"},
        {"id": "F16", "title": "2027 NCAAF slates (Stanford/Cal) not released",
         "detail": "ESPN returns empty schedules for 2027+. Saturdays Sep–Nov are conservatively marked 'game likely (est.)'.",
         "source": "https://gostanford.com/sports/football/schedule"},
    ]

# ================================================================ vacation math
def busy_days(scope, years=(2027, 2028, 2029)):
    """Set of ISO dates with ≥1 blocking event under the given scope."""
    out = {}
    for y in years:
        days = set()
        for e in events:
            if e["date"].startswith(str(y)) is False and not e.get("dateEnd", "").startswith(str(y)):
                continue
            if scope == "no-st" and e["category"] in ("spring", "exhibition"):
                continue
            if scope == "sf-radio" and not e.get("sfRadio"):
                continue
            if not e.get("blocking", True):
                continue
            d0 = date.fromisoformat(e["date"])
            d1 = date.fromisoformat(e.get("dateEnd", e["date"]))
            d = d0
            while d <= d1:
                if d.year == y:
                    days.add(d.isoformat())
                d += timedelta(days=1)
        out[y] = days
    return out

def free_runs(busy, y):
    runs = []
    d = date(y, 1, 1)
    end = date(y, 12, 31)
    start = None
    while d <= end:
        iso = d.isoformat()
        if iso not in busy:
            if start is None:
                start = d
        else:
            if start is not None:
                runs.append((start, d - timedelta(days=1)))
                start = None
        d += timedelta(days=1)
    if start is not None:
        runs.append((start, end))
    return runs

def build_summary():
    summary = {"generated": TODAY.isoformat(), "scenarios": {}}
    names = {
        "core": "Core (brief's definition: all MLB incl. spring training, all NFL, Stanford/Cal NCAAF, Westwood One national NFL)",
        "no-st": "Core minus MLB spring training/exhibitions (MLB regular season + postseason only)",
        "sf-radio": "SF Bay Area AM/FM radio only (Giants, A's, 49ers, Stanford, Cal, Westwood One national)",
    }
    for scope in ("core", "no-st", "sf-radio"):
        busy = busy_days(scope)
        sc = {"label": names[scope], "years": {}}
        for y in (2027, 2028, 2029):
            runs = [(a, b) for a, b in free_runs(busy[y], y) if (b - a).days + 1 >= 2]
            rows = []
            for a, b in runs:
                n = (b - a).days + 1
                rows.append({
                    "start": a.isoformat(), "end": b.isoformat(), "days": n,
                    "fits": {"7": n >= 7, "14": n >= 14, "21": n >= 21},
                    "certainDays": scope != "sf-radio" or True,
                })
            rows.sort(key=lambda r: -r["days"])
            sc["years"][str(y)] = {
                "busyDays": len(busy[y]),
                "runs": rows[:12],
                "longest": rows[0]["days"] if rows else 0,
            }
        summary["scenarios"][scope] = sc
    return summary

# ================================================================ radio / durations
def build_radio():
    return {
        "stations": [
            {"call": "KNBR", "dial": "680 AM / 104.5 FM", "role": "Giants flagship (nearly all games incl. spring training + postseason); 49ers co-flagship; Westwood One SF affiliate",
             "verified": True, "source": "https://en.wikipedia.org/wiki/KNBR_(AM)"},
            {"call": "KTCT (KNBR 1050)", "dial": "1050 AM", "role": "Westwood One SF affiliate; Stanford football flagship",
             "verified": True, "source": "https://en.wikipedia.org/wiki/KTCT"},
            {"call": "KSAN", "dial": "107.7 FM", "role": "49ers Radio Network", "verified": True,
             "source": "https://www.49ers.com/schedule/2026/"},
            {"call": "KSFO", "dial": "810 AM", "role": "49ers Radio Network (co-flagship)", "verified": True,
             "source": "https://www.49ers.com/schedule/2026/"},
            {"call": "KNEW (iHeart Sports 960)", "dial": "960 AM", "role": "Athletics games — Bay Area (West Sacramento era 2025–2027)", "verified": True,
             "source": "https://www.sacbee.com/sports/article300334119.html"},
            {"call": "KSTE (Talk 650)", "dial": "650 AM (Sacramento)", "role": "Athletics flagship (West Sacramento era)", "verified": True,
             "source": "https://www.sacbee.com/sports/article300334119.html"},
            {"call": "KGMZ (95.7 The Game)", "dial": "95.7 FM", "role": "Warriors flagship (EXTENDED SCOPE — not in core free definition)", "verified": True,
             "source": "https://www.nba.com/warriors/radio-network"},
            {"call": "Cal live audio", "dial": "The Varsity Network (streaming)", "role": "California football live audio; AM/FM flagship unconfirmed (flagged)", "verified": False,
             "source": "https://calbears.com/sports/football/schedule/2026"},
        ],
        "note": "Reception target: Outer Sunset, San Francisco 94122 — KNBR 680 is a clear-channel 50 kW Class A signal; KTCT 1050 and KNEW 960 are Bay Area AM signals. All listed stations are standard AM/FM receivable.",
    }

def build_durations():
    return {
        "mlb_regular": {"min": 158, "label": "MLB regular season ≈ 2:38", "verified": True,
                        "source": "https://www.lines.com/guides/how-long-is-baseball-game/1523"},
        "mlb_spring": {"min": 150, "label": "MLB spring training ≈ 2:30", "verified": False,
                       "source": "https://www.lines.com/guides/how-long-is-baseball-game/1523"},
        "mlb_postseason": {"min": 184, "label": "MLB postseason ≈ 3:04", "verified": False,
                           "source": "https://theblogtimer.com/guides/how-long-is-a-baseball-game"},
        "nfl": {"min": 192, "label": "NFL ≈ 3:12 (halftime 12 min)", "verified": True,
                "source": "https://ticketwhiz.com/blog/how-long-is-a-football-game"},
        "nfl_playoffs": {"min": 198, "label": "NFL playoffs ≈ 3:18", "verified": False,
                         "source": "https://ticketwhiz.com/blog/how-long-is-a-football-game"},
        "nfl_superbowl": {"min": 240, "label": "Super Bowl ≈ 3.5–4 h (extended halftime)", "verified": False,
                          "source": "https://ticketwhiz.com/blog/how-long-is-a-football-game"},
        "cfb": {"min": 204, "label": "NCAAF ≈ 3:24 (halftime 20 min)", "verified": True,
                "source": "https://ticketwhiz.com/blog/how-long-is-a-football-game"},
    }

# ================================================================ main
def main():
    build_mlb_2027()
    est_mlb_special_2027()
    est_mlb_slate(2028, "2028-02-17", "2028-03-22", "2028-03-23", "2028-09-24", "2028-07-11", "2028-09-27", "2028-11-02")
    est_mlb_slate(2029, "2029-02-15", "2029-03-21", "2029-03-22", "2029-09-23", "2029-07-10", "2029-09-26", "2029-11-01")
    build_nfl_2026()
    est_nfl_season(2027)
    est_nfl_season(2028)
    est_nfl_season(2029)
    build_cfb_2026()
    est_cfb(2027)
    est_cfb(2028)
    est_cfb(2029)
    build_westwood_one()
    build_flags()

    # split by calendar year of the event date (window rows anchor on start date)
    by_year = {}
    for e in events:
        y = e["date"][:4]
        by_year.setdefault(y, []).append(e)
    for y, rows in by_year.items():
        rows.sort(key=lambda r: (r["date"], r.get("time") or "00:00"))
        path = os.path.join(OUT, f"games-{y}.json")
        with open(path, "w") as f:
            json.dump({"year": y, "count": len(rows), "games": rows}, f, indent=1)
        print(f"data/games-{y}.json: {len(rows)} rows")

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(build_summary(), f, indent=1)
    with open(os.path.join(OUT, "radio.json"), "w") as f:
        json.dump(build_radio(), f, indent=1)
    with open(os.path.join(OUT, "durations.json"), "w") as f:
        json.dump(build_durations(), f, indent=1)
    with open(os.path.join(OUT, "flags.json"), "w") as f:
        json.dump({"flags": flag_items}, f, indent=1)
    print("total events:", len(events))

if __name__ == "__main__":
    main()
