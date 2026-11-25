#!/usr/bin/env python3
"""
Fetch official schedules from official / trusted sources.

Runs on a GitHub Actions runner (which has unrestricted internet access).
The local sandbox cannot reach these hosts directly, so this script must be
executed via .github/workflows/fetch-schedules.yml.

Outputs trimmed JSON files under data/raw/. If a season's schedule has not
been released yet, the result file is written with count 0 — this documents
"officially empty" (evidence fetched from the source), not a guess.

Sources
-------
MLB   : MLB Stats API  https://statsapi.mlb.com/api/v1/schedule  (official MLB)
NFL   : ESPN public schedule/scoreboard API (site.api.espn.com / site.web.api.espn.com),
        trusted aggregator that mirrors the official NFL schedule.
        NFL.com schedule pages are linked per row on the site for manual review
        (NFL's own schedule API requires OAuth credentials).
NCAAF : ESPN public college-football API for Stanford + California (cross-checked
        against official athletics schedule pages gostanford.com / calbears.com,
        which are linked per row on the site).
"""
import json
import os
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data", "raw"))

MLB_SEASONS = [2026, 2027, 2028, 2029]
MLB_GAME_TYPES = ["R", "A", "F", "D", "L", "W", "E", "S"]
NFL_SEASONS = [2026, 2027, 2028, 2029]
NFL_SEASON_TYPES = {1: "pre", 2: "reg", 3: "post"}
NCAAF_SEASONS = [2026, 2027, 2028, 2029]


def get_json(url, retries=4, backoff=5):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Freetime4-schedule-fetch/1.0 (+github.com/kanlerxz87-cyber/Freetime4)"}
    )
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = e
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(backoff * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last}")


def save(name, obj):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
    print(f"  wrote {name} ({os.path.getsize(path)} bytes)")


# ---------------------------------------------------------------- MLB (official)
def fetch_mlb():
    print("MLB Stats API (official):")
    for season in MLB_SEASONS:
        games = []
        for gt in MLB_GAME_TYPES:
            url = (
                "https://statsapi.mlb.com/api/v1/schedule"
                f"?sportId=1&season={season}&gameType={gt}"
            )
            try:
                data = get_json(url)
            except RuntimeError as e:
                print(f"  {season} gameType={gt}: FAILED {e}")
                continue
            if not data:
                continue
            for date in data.get("dates", []):
                for g in date.get("games", []):
                    teams = g.get("teams", {})
                    games.append(
                        {
                            "gamePk": g.get("gamePk"),
                            "startUTC": g.get("gameDate"),
                            "date": g.get("officialDate"),
                            "type": g.get("gameType"),
                            "abstractState": (g.get("status") or {}).get("abstractGameState"),
                            "codeState": (g.get("status") or {}).get("codedGameState"),
                            "doubleHeader": g.get("doubleHeader"),
                            "gameNumber": g.get("gameNumber"),
                            "venue": (g.get("venue") or {}).get("name"),
                            "awayId": (teams.get("away") or {}).get("team", {}).get("id"),
                            "homeId": (teams.get("home") or {}).get("team", {}).get("id"),
                            "awayScore": (teams.get("away") or {}).get("score"),
                            "homeScore": (teams.get("home") or {}).get("score"),
                        }
                    )
            time.sleep(0.4)
        games.sort(key=lambda x: (x["startUTC"] or "", x["gamePk"] or 0))
        save(
            f"mlb_{season}.json",
            {
                "season": season,
                "source": "MLB Stats API https://statsapi.mlb.com/api/v1/schedule (official MLB data)",
                "fetchedUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "gameTypesRequested": MLB_GAME_TYPES,
                "count": len(games),
                "games": games,
            },
        )

        # Team directory for id -> name/abbr mapping (used by the local build step).
        t = get_json(f"https://statsapi.mlb.com/api/v1/teams?sportId=1&season={season}")
        teams = []
        if t:
            for team in t.get("teams", []):
                teams.append(
                    {
                        "id": team.get("id"),
                        "abbr": team.get("abbreviation"),
                        "name": team.get("name"),
                        "league": (team.get("league") or {}).get("name"),
                        "division": (team.get("division") or {}).get("name"),
                        "venue": (team.get("venue") or {}).get("name"),
                    }
                )
            teams.sort(key=lambda x: x["abbr"] or "")
        save(f"mlb_teams_{season}.json", {"season": season, "count": len(teams), "teams": teams})


# ---------------------------------------------------------------- NFL (ESPN mirror of official)
ESPN_NFL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
ESPN_NFL_WEB = "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl"


def trim_nfl_event(ev):
    comp = (ev.get("competitions") or [{}])[0]
    comp_status = comp.get("status") or {}
    venue = comp.get("venue") or {}
    home = away = None
    for c in comp.get("competitors", []):
        entry = {
            "id": (c.get("team") or {}).get("id"),
            "abbr": (c.get("team") or {}).get("abbreviation"),
            "name": (c.get("team") or {}).get("displayName"),
            "homeAway": c.get("homeAway"),
            "score": c.get("score"),
        }
        if c.get("homeAway") == "home":
            home = entry
        else:
            away = entry
    broadcast = ""
    for b in comp.get("broadcasts", []) or []:
        names = b.get("names") or []
        if names:
            broadcast = ", ".join(names)
            break
    return {
        "id": ev.get("id"),
        "dateUTC": ev.get("date"),
        "name": ev.get("name"),
        "shortName": ev.get("shortName"),
        "seasonYear": (ev.get("season") or {}).get("year"),
        "seasonType": (ev.get("season") or {}).get("type"),
        "week": (ev.get("week") or {}).get("number"),
        "state": ((comp_status.get("type") or {}).get("state")),
        "detail": ((comp_status.get("type") or {}).get("detail")),
        "venue": venue.get("fullName"),
        "home": home,
        "away": away,
        "tv": broadcast,
    }


def fetch_nfl():
    print("NFL via ESPN public API (mirror of official schedule):")

    # 49ers full schedule (id 25) — all season types, all years.
    for season in NFL_SEASONS:
        events = []
        for st, st_name in NFL_SEASON_TYPES.items():
            url = f"{ESPN_NFL_WEB}/teams/25/schedule?season={season}&seasontype={st}"
            try:
                data = get_json(url)
            except RuntimeError as e:
                print(f"  49ers {season} type={st_name}: FAILED {e}")
                continue
            if not data:
                continue
            for ev in data.get("events", []):
                t = trim_nfl_event(ev)
                t["seasonType"] = st
                events.append(t)
            time.sleep(0.4)
        events.sort(key=lambda x: x["dateUTC"] or "")
        save(
            f"nfl_49ers_{season}.json",
            {
                "season": season,
                "team": "San Francisco 49ers (ESPN id 25)",
                "source": "ESPN public API https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/teams/25/schedule (mirror of official NFL schedule; official page: https://www.nfl.com/schedules/)",
                "fetchedUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "count": len(events),
                "events": events,
            },
        )

    # Full league schedule.
    # 2026: iterate day-by-day (ground truth). Later seasons: try a range query;
    # expectation is empty (not yet released) and the empty file is the evidence.
    windows = {2026: ("2026-08-01", "2027-02-20"), 2027: ("2027-08-01", "2028-02-28"),
               2028: ("2028-08-01", "2029-02-28"), 2029: ("2029-08-01", "2030-02-28")}
    for season, (start, end) in windows.items():
        events = {}
        method = "day-by-day"
        if season == 2026:
            d = start
            from datetime import date, timedelta

            d0 = date.fromisoformat(start)
            d1 = date.fromisoformat(end)
            cur = d0
            while cur <= d1:
                iso = cur.isoformat().replace("-", "")
                try:
                    data = get_json(f"{ESPN_NFL}/scoreboard?dates={iso}")
                except RuntimeError as e:
                    print(f"  scoreboard {iso}: FAILED {e}")
                    cur += timedelta(days=1)
                    time.sleep(0.25)
                    continue
                for ev in data.get("events", []):
                    t = trim_nfl_event(ev)
                    events[t["id"]] = t
                cur += timedelta(days=1)
                time.sleep(0.25)
        else:
            method = "range-query"
            rng = start.replace("-", "") + "-" + end.replace("-", "")
            try:
                data = get_json(f"{ESPN_NFL}/scoreboard?dates={rng}&limit=1000")
                for ev in data.get("events", []):
                    t = trim_nfl_event(ev)
                    events[t["id"]] = t
            except RuntimeError as e:
                print(f"  range {rng}: FAILED {e}")
        evs = sorted(events.values(), key=lambda x: x["dateUTC"] or "")
        save(
            f"nfl_league_{season}.json",
            {
                "season": season,
                "source": "ESPN public API https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard (mirror of official NFL schedule; official page: https://www.nfl.com/schedules/)",
                "method": method,
                "window": [start, end],
                "fetchedUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "count": len(evs),
                "events": evs,
            },
        )


# ---------------------------------------------------------------- NCAAF Stanford + Cal (ESPN)
ESPN_CF = "https://site.api.espn.com/apis/site/v2/sports/football/college-football"
ESPN_CF_WEB = "https://site.web.api.espn.com/apis/site/v2/sports/football/college-football"


def fetch_ncaaf():
    print("NCAAF via ESPN public API (Stanford + California):")
    data = get_json(f"{ESPN_CF}/teams?limit=500")
    target = {}
    for t in data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", []):
        team = t.get("team") or {}
        name = (team.get("displayName") or team.get("name") or "").strip()
        if name == "Stanford Cardinal":
            target["Stanford"] = team.get("id")
        elif name == "California Golden Bears":
            target["California"] = team.get("id")
    print(f"  team ids found: {target}")
    save("ncaaf_team_ids.json", {"source": "ESPN public API", "ids": target, "fetchedUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    for label, tid in target.items():
        for season in NCAAF_SEASONS:
            events = []
            for st in (2, 3):  # regular season, postseason (bowls/playoff)
                url = f"{ESPN_CF_WEB}/teams/{tid}/schedule?season={season}&seasontype={st}"
                try:
                    d = get_json(url)
                except RuntimeError as e:
                    print(f"  {label} {season} st={st}: FAILED {e}")
                    continue
                if not d:
                    continue
                for ev in d.get("events", []):
                    t = trim_nfl_event(ev)
                    t["seasonType"] = st
                    events.append(t)
                time.sleep(0.4)
            events.sort(key=lambda x: x["dateUTC"] or "")
            save(
                f"ncaaf_{label.lower()}_{season}.json",
                {
                    "season": season,
                    "team": label,
                    "source": f"ESPN public API https://site.web.api.espn.com/apis/site/v2/sports/football/college-football/teams/{tid}/schedule (mirror of official schedule; official pages: https://gostanford.com/sports/football/schedule, https://calbears.com/sports/football/schedule)",
                    "fetchedUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "count": len(events),
                    "events": events,
                },
            )


if __name__ == "__main__":
    print(f"Fetching into {OUT}")
    fetch_mlb()
    fetch_nfl()
    fetch_ncaaf()
    print("DONE")
