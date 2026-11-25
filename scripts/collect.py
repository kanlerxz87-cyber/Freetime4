#!/usr/bin/env python3
"""Collect official schedule sources. Runs inside GitHub Actions (needs network)."""
import json, os, re, ssl, sys, time
import urllib.request, urllib.error

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
OUT = "data/raw"
os.makedirs(OUT, exist_ok=True)
REPORT = []

def fetch(url, timeout=45, headers=None):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.read(), dict(r.headers)

def save(name, url, note=""):
    try:
        st, body, hdrs = fetch(url)
        path = os.path.join(OUT, name)
        mode = "wb"
        with open(path, mode) as f:
            f.write(body)
        REPORT.append(f"| {name} | {st} | {len(body)} | {url} | {note} |")
        print(f"OK {st} {len(body):>9} {name}")
        return body
    except urllib.error.HTTPError as e:
        REPORT.append(f"| {name} | {e.code} | 0 | {url} | HTTPError {note} |")
        print(f"HTTP {e.code} {name}")
    except Exception as e:
        REPORT.append(f"| {name} | ERR | 0 | {url} | {type(e).__name__}: {str(e)[:80]} {note} |")
        print(f"ERR {name} {type(e).__name__}")
    return None

MLB = "https://statsapi.mlb.com/api/v1"

# ---------- MLB ----------
save("mlb_teams.json", f"{MLB}/teams?sportId=1&season=2027")
for yr in (2026, 2027, 2028, 2029):
    save(f"mlb_{yr}_all.json",
         f"{MLB}/schedule?sportId=1&season={yr}&gameTypes=R,F,D,L,W,P,S&hydrate=team,linescore")
save("mlb_2027_meta.json", f"{MLB}/seasons/2027?sportId=1")

# ---------- NFL.com ----------
for yr in (2026, 2027, 2028, 2029):
    for st in ("PRE", "REG", "POST"):
        save(f"nfl_{yr}_{st}.html", f"https://www.nfl.com/schedules/{yr}/{st}/")

# ---------- ESPN (cross-check only, NOT official) ----------
save("espn_nfl_2026_1.json", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2026&seasontype=1&limit=1000")
save("espn_nfl_2026_2.json", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2026&seasontype=2&limit=1000")
save("espn_nfl_2026_3.json", "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2026&seasontype=3&limit=1000")

# ---------- Stanford / Cal ----------
for slug, dom in (("stanford", "gostanford.com"), ("cal", "calbears.com")):
    save(f"{slug}_2026.html", f"https://{dom}/sports/football/schedule")
    for yr in (2027, 2028):
        save(f"{slug}_{yr}.html", f"https://{dom}/sports/football/schedule/season/{yr}")
    for api in [
        f"https://{dom}/api/v2/sports/football/schedule?season=2026",
        f"https://{dom}/api/v2/sports/football/season/2026/schedule",
        f"https://{dom}/api/oas/sports/football/schedule?season=2026",
        f"https://{dom}/api/v2/schedule?sport=football&season=2026",
    ]:
        nm = "api_" + re.sub(r"[^a-z0-9]+", "_", api.split("//")[1])[:60] + ".json"
        save(nm, api, "api-candidate")

# ---------- Westwood One ----------
save("wwo_nfl.html", "https://www.westwoodonesports.com/nfl-schedule/")
save("wwo_ncaaf.html", "https://www.westwoodonesports.com/ncaa-football-schedule/")
save("wwo_nfl_past.html", "https://www.westwoodonesports.com/nfl-schedule/?range=past")
for eid in ("3757", "all"):
    for extra in ("", "&widgetTitle=Upcoming+Broadcasts"):
        u = (f"https://www.westwoodonesports.com/more/eventGrid?id={eid}&range=current"
             f"&offset=0&limit=400&timezone=America/Los_Angeles{extra}")
        save(f"wwo_eg_{eid}_{'t' if extra else 'n'}.html", u, "eventgrid-candidate")
save("wwo_stations.html", "https://www.westwoodonesports.com/stations/")

# ---------- KNBR ----------
save("knbr_home.html", "https://www.knbr.com/")
save("knbr_sitemap.xml", "https://www.knbr.com/sitemap.xml")
save("knbr_schedule.html", "https://www.knbr.com/schedule/")

# ---------- MLB pressbox (schedule PDF/summary) ----------
save("mlb_pressbox_2027.html", "https://www.mlb.com/press-box/schedule?season=2027")

with open("data/collect-report.md", "w") as f:
    f.write("# Collect report\n\n| file | status | bytes | url | note |\n|---|---|---|---|---|\n")
    f.write("\n".join(REPORT) + "\n")
print("done", len(REPORT))
