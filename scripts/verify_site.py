#!/usr/bin/env python3
"""Final verification pass (integration session):
1. Every HTML page in site/ parses; all local links resolve to real files.
2. Data JSONs parse; every verified row has a sourceUrl; every ESTIMATE row has none.
3. Cross-file consistency: every day's gameIds exist in the corresponding games file.
4. Every verified Stanford/Cal 2026 row date matches the official pages' dates
   (regression check against the values transcribed from gostanford.com/calbears.com).
Exits non-zero on failure.
"""
import json
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "site")

fail = []


def check(cond, msg):
    if cond:
        print("  ok:", msg)
    else:
        fail.append(msg)
        print("  FAIL:", msg)


print("[1] site pages + local links")
htmls = [f for f in os.listdir(SITE) if f.endswith(".html")]
for h in sorted(htmls):
    text = open(os.path.join(SITE, h)).read()
    for m in re.finditer(r'(?:href|src)="([^"#]+?)(?:[#?][^"]*)?"', text):
        u = m.group(1)
        if u.startswith(("http://", "https://", "data:", "mailto:", "${")):
            continue
        target = os.path.normpath(os.path.join(SITE, u))
        if not os.path.exists(target):
            fail.append(f"{h}: broken local link {u}")
    print(f"  ok: {h} links checked")

print("[2] data integrity")
years = (2026, 2027, 2028, 2029)
games_by_year = {}
for y in years:
    d = json.load(open(os.path.join(DATA, f"games_{y}.json")))
    games_by_year[y] = d["games"]
    for g in d["games"]:
        st = g["status"]
        url = g.get("sourceUrl") or ""
        if st in ("VERIFIED", "VERIFIED-SLOT", "PARTIAL-VERIFIED") and not url:
            fail.append(f"{y}: {g['id']} status {st} without sourceUrl")
        if st == "ESTIMATE" and url:
            fail.append(f"{y}: {g['id']} ESTIMATE but has sourceUrl (should be blank)")
        if st == "ESTIMATED-TIME" and not url:
            fail.append(f"{y}: {g['id']} ESTIMATED-TIME without sourceUrl (date must be sourced)")
        if not g.get("datePT") or not re.match(r"^\d{4}-\d{2}-\d{2}$", g["datePT"]):
            fail.append(f"{y}: {g['id']} bad datePT")
    print(f"  ok: games_{y}.json — {len(d['games'])} rows, statuses validated")

print("[3] days files consistency")
for y in years:
    for variant in ("", "-nospring"):
        d = json.load(open(os.path.join(DATA, f"days_{y}{variant}.json")))
        ids = {g["id"] for g in games_by_year[y] if g.get("blocks", False)}
        for day in d["days"]:
            for gid in day["gameIds"]:
                if gid not in ids:
                    fail.append(f"days_{y}{variant}: {day['date']} references missing game {gid}")
        nfree = sum(1 for x in d["days"] if x["free"])
        print(f"  ok: days_{y}{variant}.json — {len(d['days'])} days, {nfree} free")

print("[4] windows file")
w = json.load(open(os.path.join(DATA, "windows.json")))
for variant in ("default", "no-spring"):
    for y in ("2027", "2028", "2029"):
        assert variant in w["windows"] and y in w["windows"][variant]["windows"]
print("  ok: windows.json complete for both variants x 3 years")

print("[5] regression: Stanford/Cal 2026 dates match official pages")
import datetime
from zoneinfo import ZoneInfo
PT = ZoneInfo("America/Los_Angeles")
for label, expected in (
    ("Stanford", ["2026-08-29", "2026-09-04", "2026-09-19", "2026-09-26", "2026-10-03", "2026-10-10",
                  "2026-10-17", "2026-10-23", "2026-10-31", "2026-11-14", "2026-11-21", "2026-11-28"]),
    ("California", ["2026-09-05", "2026-09-12", "2026-09-19", "2026-09-25", "2026-10-03", "2026-10-10",
                    "2026-10-17", "2026-10-24", "2026-10-31", "2026-11-14", "2026-11-21", "2026-11-28"]),
):
    rows = [g for g in games_by_year[2026] if g["category"] == f"NCAAF-{label}"]
    dates = sorted({g["datePT"] for g in rows})
    check(dates == expected, f"{label} 2026 dates == official schedule page ({len(expected)} games)")

print("[6] regression: 2027 MLB key dates")
r27 = sorted([g for g in games_by_year[2027] if g["sport"] == "MLB" and g["type"] == "Regular season"], key=lambda g: g["datePT"])
check(r27[0]["datePT"] == "2027-03-24", "2027 Opening Night 2027-03-24")
check(r27[-1]["datePT"] == "2027-09-26", "2027 final regular day 2027-09-26")
asg = [g for g in games_by_year[2027] if g["type"] == "All-Star Game"]
check(len(asg) == 1 and asg[0]["datePT"] == "2027-07-13", "2027 All-Star Game 2027-07-13")
sf = [g for g in r27 if g["home"] == "SF" or g["away"] == "SF"]
check(len(sf) == 162, f"Giants 162 regular games (got {len(sf)})")
ath = [g for g in r27 if g["home"] == "ATH" or g["away"] == "ATH"]
check(len(ath) == 162, f"Athletics 162 regular games (got {len(ath)})")

print("[7] regression: 49ers + Super Bowl")
nf = [g for y in years for g in games_by_year[y] if g["category"] == "NFL-49ers" and g["status"] == "VERIFIED"]
check(len(nf) == 20, f"49ers 2026 = 20 verified games across calendar years (got {len(nf)})")
check(len({g['id'] for g in games_by_year[2026]} | {g['id'] for g in games_by_year[2027]}) == len(games_by_year[2026]) + len(games_by_year[2027]), "no duplicate game ids within 2026+2027")
sb = [g for g in games_by_year[2027] if g["datePT"] == "2027-02-14" and g["sport"] == "NFL" and g.get("blocks")]
check(len(sb) >= 1 and sb[0]["status"] == "VERIFIED-SLOT", "Super Bowl LXI 2027-02-14 present and blocking")

print("[8] WW1 file")
ww1 = json.load(open(os.path.join(ROOT, "data", "raw", "ww1_nfl_schedule.json")))
check(len(ww1["broadcasts"]) == 35, f"35 WW1 broadcasts (got {len(ww1['broadcasts'])})")

print()
if fail:
    print(f"FAILED: {len(fail)} problems")
    for f in fail:
        print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
