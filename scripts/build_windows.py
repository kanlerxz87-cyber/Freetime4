#!/usr/bin/env python3
"""
Free-time engine + vacation-window analysis.

Definition (from the user's requirements): a minute is FREE when none of these are
on air on receivable Bay Area radio:
  - MLB (all 30 clubs; Giants and Athletics flagged high priority)
  - NFL - San Francisco 49ers (preseason, regular season, postseason)
  - Stanford NCAAF, California NCAAF
  - Westwood One Sports national NFL radio broadcasts (TNF/SNF/MNF/playoffs/Super Bowl)

On-air (busy) windows per game are estimated from researched average durations
(data/site source: durations.json). All times Pacific (PST/PDT).

Outputs:
  data/site/days_<year>.json  - per-day busy minutes, free minutes, merged busy spans
  data/site/windows.json      - vacation windows (>= 2 consecutive fully-free days)
                                for both blocking variants
"""
import json
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data", "site")
PT = ZoneInfo("America/Los_Angeles")

# Estimated on-air windows (minutes). start_offset < 0 = pregame lead.
WINDOWS = {
    "MLB": {"pre": 20, "post": 175, "postseason_pre": 30, "postseason_post": 210,
            "note": "Average MLB game 2:42-2:44 (2026 verified); +radio pregame/postgame"},
    "NFL": {"pre": 30, "post": 225,
            "note": "Average NFL game 3:02-3:12; +KNBR/WW1 pregame 30 min"},
    "WW1": {"pre": 0, "post": 240,
            "note": "WW1 listed time is broadcast/pregame start; window = start + 4h"},
    "NCAAF": {"pre": 15, "post": 240,
              "note": "Average FBS game 3:26 (2025); +pregame"},
}


def load_games(year):
    with open(os.path.join(DATA, f"games_{year}.json")) as f:
        return json.load(f)["games"]


def busy_span(row, exclude_spring=False):
    if not row.get("blocks", False):
        return None
    if exclude_spring and row["sport"] == "MLB" and row.get("type") in ("Spring training", "Exhibition"):
        return None
    h, m = row["startPT"].split(":")
    start = int(h) * 60 + int(m)
    sp = row["sport"]
    if sp == "MLB":
        pre, post = WINDOWS["MLB"]["pre"], WINDOWS["MLB"]["post"]
        if row.get("type") in ("Wild Card Series", "Division Series", "League Championship Series", "World Series"):
            pre, post = WINDOWS["MLB"]["postseason_pre"], WINDOWS["MLB"]["postseason_post"]
    elif sp == "NFL" and row["category"] == "WW1":
        pre, post = WINDOWS["WW1"]["pre"], WINDOWS["WW1"]["post"]
    elif sp == "NFL":
        pre, post = WINDOWS["NFL"]["pre"], WINDOWS["NFL"]["post"]
    else:
        pre, post = WINDOWS["NCAAF"]["pre"], WINDOWS["NCAAF"]["post"]
    return start - pre, start + post


def day_length(d):
    # handles 23h (spring DST) and 25h (fall DST) Pacific days
    dt0 = datetime(d.year, d.month, d.day, tzinfo=PT)
    dt1 = dt0 + timedelta(days=1)
    return int((dt1.astimezone(PT) - dt0.astimezone(PT)).total_seconds() // 60)


def merge(spans):
    spans = sorted(spans)
    out = []
    for s, e in spans:
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def build_year(year, exclude_spring=False):
    games = load_games(year)
    by_day = {}
    for g in games:
        sp = busy_span(g, exclude_spring)
        if sp is None:
            continue
        by_day.setdefault(g["datePT"], []).append((g, sp))
    days = []
    d = date(year, 1, 1)
    end = date(year, 12, 31)
    while d <= end:
        ds = d.isoformat()
        entries = by_day.get(ds, [])
        spans = merge([sp for _, sp in entries])
        busy = sum(min(e, day_length(d)) - s for s, e in spans)
        blocking_ids = [g["id"] for g, sp in entries]
        days.append({
            "date": ds,
            "weekday": d.strftime("%a"),
            "busyMin": busy,
            "dayLen": day_length(d),
            "busySpans": [[s, e] for s, e in spans],
            "free": busy == 0,
            "nGames": len(blocking_ids),
            "gameIds": blocking_ids,
        })
        d += timedelta(days=1)
    return days


def find_windows(days, min_len=2):
    wins = []
    cur = []
    for day in days:
        if day["free"]:
            cur.append(day)
        else:
            if len(cur) >= min_len:
                wins.append(cur)
            cur = []
    if len(cur) >= min_len:
        wins.append(cur)
    return wins


def main():
    out = {}
    summary = {}
    for variant, exclude in (("default", False), ("no-spring", True)):
        all_days, all_windows = [], {}
        for year in (2026, 2027, 2028, 2029):
            days = build_year(year, exclude)
            with open(os.path.join(DATA, f"days_{year}{'-nospring' if exclude else ''}.json"), "w") as f:
                json.dump({"year": year, "variant": variant, "days": days}, f, separators=(",", ":"))
            all_days += days
            all_windows[year] = [
                {"start": w[0]["date"], "end": w[-1]["date"], "days": len(w),
                 "weekdayStart": w[0]["weekday"], "weekdayEnd": w[-1]["weekday"]}
                for w in find_windows(days, 2)
            ]
        out[variant] = {"windows": all_windows}
        free_by_year = {y: sum(1 for d in all_days if d["date"].startswith(str(y)) and d["free"]) for y in (2026, 2027, 2028, 2029)}
        summary[variant] = free_by_year
        top = sorted([w for ws in all_windows.values() for w in ws], key=lambda w: -w["days"])[:12]
        summary[variant + "_top_windows"] = top
    result = {
        "generated": datetime.now(PT).strftime("%Y-%m-%d %H:%M %Z"),
        "definition": "A day is FREE when zero estimated on-air minutes of blocking radio broadcasts (MLB all 30 clubs incl. spring training; NFL 49ers; Stanford/Cal NCAAF; Westwood One national NFL) overlap the Pacific day.",
        "variants": {
            "default": "Spring training counts as blocking (user asked for MLB preseason to count).",
            "no-spring": "MLB spring training/exhibitions excluded from blocking (shows the deep Feb-Mar window without spring games; spring games rarely air on Bay Area radio).",
        },
        "freeDaysPerYear": summary,
        "windows": out,
    }
    with open(os.path.join(DATA, "windows.json"), "w") as f:
        json.dump(result, f, separators=(",", ":"))
    for v in ("default", "no-spring"):
        print(v, summary[v])
        for w in summary[v + "_top_windows"][:8]:
            print("   ", w)


if __name__ == "__main__":
    main()
