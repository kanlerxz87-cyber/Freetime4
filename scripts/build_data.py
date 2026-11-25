#!/usr/bin/env python3
"""
Curate raw fetched data (data/raw) into site JSON (data/site).

Rules
-----
- All times converted to Pacific (America/Los_Angeles, PST/PDT as applicable).
- MLB Stats API placeholder times for TBD games (UTC hour 04-12 = 00:00-08:59 ET,
  impossible game times) are detected and left for the estimate builder.
- Every verified row carries a sourceUrl to an official page.
- rows: data/site/games_<year>.json + data/site/meta.json + data/site/ww1.json
"""
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "site")
PT = ZoneInfo("America/Los_Angeles")

MLB_URL = "https://www.mlb.com/gameday/{gamePk}"
NFL_URL = "https://www.nfl.com/schedules/"
NCAAF_STANFORD_URL = "https://gostanford.com/sports/football/schedule"
NCAAF_CAL_URL = "https://calbears.com/sports/football/schedule"
ESPN_NFL_NOTE = "Values cross-checked against ESPN public schedule API (trusted mirror of official NFL schedule); official NFL page linked here."
ESPN_NCAAF_NOTE = "Values cross-checked against ESPN public college-football API; official athletics schedule page linked here."

RADIO = {
    "MLB-Giants": "KNBR 680 AM / 104.5 FM (flagship)",
    "MLB-Athletics": "KNEW 960 AM (Bay Area); flagship KSTE 650 Sacramento; Spanish KIQI 1010 AM",
    "MLB-other": "Local flagship of the club; NOT receivable on Bay Area AM/FM (MLB app only)",
    "NFL-49ers": "KNBR 680 AM / 104.5 FM + 107.7 The Bone + 810 KSFO (2026 49ers Radio Network)",
    "NFL-national": "",
    "WW1": "Westwood One on KNBR 680 AM / 104.5 FM (Bay Area WW1 affiliate)",
    "NCAAF-Stanford": "KNBR 680/104.5 (The Sports Leader)",
    "NCAAF-California": "810 AM KSFO (Cal games air only on 810)",
}


def utc_to_pt(start_utc):
    if not start_utc:
        return None, None, False
    utc_dt = datetime.fromisoformat(start_utc.replace("Z", "+00:00"))
    # MLB Stats API placeholder for TBD games: UTC hour 04-12 -> 00:00-08:59 ET, impossible game time.
    is_placeholder = 4 <= utc_dt.hour <= 12
    dt = utc_dt.astimezone(PT)
    return dt, dt.strftime("%H:%M"), is_placeholder


def load(name):
    with open(os.path.join(RAW, name)) as f:
        return json.load(f)


def mlb_team_map():
    m = {}
    for y in (2026, 2027):
        try:
            t = load(f"mlb_teams_{y}.json")
            for team in t["teams"]:
                m[team["id"]] = team
        except FileNotFoundError:
            pass
    return m


def mlb_rows(year, teams):
    d = load(f"mlb_{year}.json")
    # The official API can return a game twice when it is postponed and rescheduled
    # (postponed instance + final instance sharing a gamePk). Keep the final
    # occurrence: prefer completed ('F'/'O') rows, then the latest slot.
    best = {}
    for g in d["games"]:
        pk = g["gamePk"]
        prev = best.get(pk)
        rank = (0 if g.get("codeState") in ("F", "O") else 1, g["startUTC"] or "")
        if prev is None or rank < prev[0]:
            best[pk] = (rank, g)
    rows = []
    for g in (v[1] for v in best.values()):
        if g["type"] not in ("R", "A", "F", "D", "L", "W", "S", "E"):
            continue
        dt, hhmm, placeholder = utc_to_pt(g["startUTC"])
        date_pt = dt.strftime("%Y-%m-%d") if dt else g["date"]
        home = teams.get(g["homeId"], {})
        away = teams.get(g["awayId"], {})
        home_abbr, away_abbr = home.get("abbr") or "?", away.get("abbr") or "?"
        typemap = {
            "R": "Regular season", "A": "All-Star Game", "F": "Wild Card Series",
            "D": "Division Series", "L": "League Championship Series", "W": "World Series",
            "S": "Spring training", "E": "Exhibition",
        }
        if home_abbr == "SF" or away_abbr == "SF":
            cat, prio, radio = "MLB-Giants", "high", RADIO["MLB-Giants"]
        elif home_abbr == "ATH" or away_abbr == "ATH":
            cat, prio, radio = "MLB-Athletics", "high", RADIO["MLB-Athletics"]
        else:
            cat, prio, radio = "MLB-other", "standard", RADIO["MLB-other"]
        rows.append({
            "id": f"mlb-{g['gamePk']}",
            "datePT": date_pt,
            "startPT": hhmm,
            "sport": "MLB",
            "category": cat,
            "type": typemap.get(g["type"], g["type"]),
            "matchup": f"{away.get('name', away_abbr)} at {home.get('name', home_abbr)}",
            "away": away_abbr, "home": home_abbr,
            "venue": g.get("venue") or "",
            "priority": prio,
            "radio": radio,
            "blocks": True,
            "status": "ESTIMATED-TIME" if placeholder else "VERIFIED",
            "sourceUrl": MLB_URL.format(gamePk=g["gamePk"]),
            "sourceNote": "MLB Stats API (official) — game page linked",
        })
    return rows


def nfl_row(e, cat, prio, radio, source_url, source_note, status="VERIFIED"):
    dt, hhmm, _ = utc_to_pt(e["dateUTC"])
    if dt is None:
        return None
    home = (e.get("home") or {}).get("abbr") or (e.get("home") or {}).get("name") or "TBD"
    away = (e.get("away") or {}).get("abbr") or (e.get("away") or {}).get("name") or "TBD"
    stmap = {1: "Preseason", 2: "Regular season", 3: "Postseason"}
    return {
        "id": f"nfl-{e['id']}",
        "datePT": dt.strftime("%Y-%m-%d"),
        "startPT": hhmm,
        "sport": "NFL",
        "category": cat,
        "type": stmap.get(e.get("seasonType"), ""),
        "week": e.get("week"),
        "matchup": e.get("name") or f"{away} at {home}",
        "away": away, "home": home,
        "venue": e.get("venue") or "",
        "priority": prio,
        "radio": radio,
        "blocks": True,
        "status": status,
        "sourceUrl": source_url,
        "sourceNote": source_note,
    }


def nfl_rows(year):
    rows = []
    if year == 2026:
        nine = load("nfl_49ers_2026.json")
        for e in nine["events"]:
            rows.append(nfl_row(e, "NFL-49ers", "high", RADIO["NFL-49ers"], NFL_URL, ESPN_NFL_NOTE))
        have = {r["id"] for r in rows}  # e.g. "nfl-401873170"
        league = load("nfl_league_2026.json")
        for e in league["events"]:
            if f"nfl-{e['id']}" in have:
                continue  # same game already present from the 49ers schedule file
            teams_tbd = (e.get("name") or "").find("TBD") >= 0 or "TBD @ TBD" in (e.get("name") or "")
            cat = "NFL-national"
            status = "VERIFIED" if not teams_tbd else "VERIFIED-SLOT"
            r = nfl_row(e, cat, "high", RADIO["NFL-national"], NFL_URL, ESPN_NFL_NOTE, status)
            if r:
                # Other clubs' games are displayed but are NOT receivable on Bay Area AM/FM
                # unless carried by Westwood One (separate WW1 rows carry that coverage).
                # NFL playoff slots ARE carried nationally by Westwood One.
                if r.get("type") == "Postseason":
                    r["radio"] = "Westwood One national radio on KNBR 680 AM / 104.5 FM (playoffs)"
                    r["blocks"] = True
                else:
                    r["radio"] = "Not on Bay Area AM/FM (club's local flagship only)"
                    r["blocks"] = False
                rows.append(r)
    return rows


def ncaaf_rows(year):
    rows = []
    if year == 2026:
        for label, url in (("Stanford", NCAAF_STANFORD_URL), ("California", NCAAF_CAL_URL)):
            d = load(f"ncaaf_{label.lower()}_{year}.json")
            for e in d["events"]:
                r = nfl_row(e, f"NCAAF-{label}", "high", RADIO[f"NCAAF-{label}"], url, ESPN_NCAAF_NOTE)
                if r:
                    r["sport"] = "NCAAF"
                    r["id"] = f"ncaaf-{label.lower()}-{e['id']}"
                    r.pop("week", None)
                    rows.append(r)
    return rows


def ww1_rows():
    d = load("ww1_nfl_schedule.json")
    rows = []
    for b in d["broadcasts"]:
        start_local = datetime.fromisoformat(f"{b['date']}T{b['timeET']}:00") .replace(tzinfo=ZoneInfo("America/New_York"))
        pt = start_local.astimezone(PT)
        ww1 = {
            "id": f"ww1-{b['date']}-{b['timeET'].replace(':', '')}",
            "datePT": pt.strftime("%Y-%m-%d"),
            "startPT": pt.strftime("%H:%M"),
            "sport": "NFL",
            "category": "WW1",
            "type": b["label"],
            "matchup": b["matchup"],
            "venue": b["venue"],
            "priority": "high",
            "radio": RADIO["WW1"],
            "blocks": True,
            "status": "VERIFIED",
            "sourceUrl": b["url"],
            "sourceNote": "westwoodonesports.com NFL schedule page (fetched 2026-11-25). Listed time is the radio broadcast window start (pregame), typically 45-50 min before kickoff.",
        }
        rows.append(ww1)
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    teams = mlb_team_map()
    games = {}
    for y in (2026, 2027, 2028, 2029):
        games[y] = []
    games[2026] += mlb_rows(2026, teams) + nfl_rows(2026) + ncaaf_rows(2026)
    games[2027] += mlb_rows(2027, teams)
    # Distribute EVERY row by its Pacific calendar year so the scoreboard/windows
    # per-year files align (e.g. the Jan-Feb 2027 NFL playoffs/Super Bowl from the
    # 2026 season land in games_2027).
    distributed = {}
    for y, rows in games.items():
        for r in rows:
            distributed.setdefault(int(r["datePT"][:4]), []).append(r)
    # WW1 broadcasts (Nov 2026 - Jan 2027) — already carry their Pacific datePT.
    for r in ww1_rows():
        distributed.setdefault(int(r["datePT"][:4]), []).append(r)

    counts = {}
    for y, rows in distributed.items():
        rows.sort(key=lambda r: (r["datePT"], r["startPT"] or "99:99"))
        with open(os.path.join(OUT, f"games_{y}.json"), "w") as f:
            json.dump({"year": y, "source": "data/site provenance: see meta.json", "count": len(rows), "games": rows}, f, separators=(",", ":"))
        counts[y] = len(rows)
    meta = {
        "generated": datetime.now(PT).strftime("%Y-%m-%d %H:%M %Z"),
        "timezone": "America/Los_Angeles (PST/PDT as applicable — true Pacific time shown)",
        "counts": counts,
        "sources": {
            "MLB": "MLB Stats API https://statsapi.mlb.com/api/v1/schedule (official MLB); per-row link https://www.mlb.com/gameday/{gamePk}",
            "NFL": "NFL.com schedules (official, linked per row); values from ESPN public API (trusted mirror of official schedule)",
            "NCAAF": "Official athletics pages gostanford.com & calbears.com (linked per row); cross-checked with ESPN public API",
            "WW1": "https://www.westwoodonesports.com/nfl-schedule/ fetched live 2026-11-25",
        },
        "notes": [
            "MLB 2027 schedule officially released (Opening Night Mar 24, Opening Day Mar 25, final day Sep 26, 2027; All-Star Game Jul 13 at Wrigley).",
            "MLB 2028/2029 not released as of 2026-11-25 (official API returns zero games) — estimated, flagged.",
            "NFL 2027-2029 not released — estimated, flagged. NCAAF 2027-2029 not released — estimated, flagged.",
            "MLB Stats API placeholder times (UTC 04:00-12:59 = impossible ET game time) treated as TBD and re-estimated with ESTIMATED-TIME flag.",
        ],
    }
    with open(os.path.join(OUT, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("counts:", counts)


if __name__ == "__main__":
    main()
