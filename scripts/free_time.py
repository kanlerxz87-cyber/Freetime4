#!/usr/bin/env python3
"""Free-time engine.

A minute is FREE when none of the tracked broadcasts/games is on air.
All computation happens in Pacific local wall-clock time.
"""
import json, os, sys, datetime as dt
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- season windows
def season_windows():
    """First/last tracked day per season, used to rank windows."""
    return {
        2026: (dt.date(2026, 2, 1), dt.date(2027, 2, 20)),
        2027: (dt.date(2027, 2, 1), dt.date(2028, 2, 20)),
        2028: (dt.date(2028, 2, 1), dt.date(2029, 2, 20)),
        2029: (dt.date(2029, 2, 1), dt.date(2030, 2, 20)),
    }

# ---------------------------------------------------------------- calendar label
US_HOLIDAYS = {
    (1, 1): "New Year's Day", (7, 4): "Independence Day", (11, 11): "Veterans Day",
    (12, 25): "Christmas Day", (12, 24): "Christmas Eve", (12, 31): "New Year's Eve",
    (6, 19): "Juneteenth", (11, 26): "Thanksgiving (2026)", (11, 25): "Thanksgiving (2027)",
    (5, 31): "Memorial Day (2027)", (5, 29): "Memorial Day (2028)", (5, 28): "Memorial Day (2029)",
    (9, 6): "Labor Day (2027)", (9, 4): "Labor Day (2028)", (9, 3): "Labor Day (2029)",
}

def season_of(d):
    """Which MLB/NFL/NCAAF 'sports year' a date belongs to."""
    return d.year if d.month >= 2 else d.year - 1

# ---------------------------------------------------------------- interval plumbing
def merge(intervals):
    if not intervals: return []
    intervals = sorted(intervals)
    out = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= out[-1][1]:
            if e > out[-1][1]: out[-1][1] = e
        else:
            out.append([s, e])
    return [(a, b) for a, b in out]

def complement(day_start, day_end, busy):
    out = []
    cur = day_start
    for s, e in merge(busy):
        s = max(s, day_start); e = min(e, day_end)
        if e <= day_start or s >= day_end: continue
        if s > cur: out.append((cur, s))
        cur = max(cur, e)
    if cur < day_end: out.append((cur, day_end))
    return out

def fmt(mins):
    h, m = divmod(int(mins), 60)
    return f"{h}:{m:02d}"

def clock(t):
    return t.strftime("%-I:%M %p")

# ---------------------------------------------------------------- build from games.json
def to_intervals(games, durations):
    """games: list of dicts already resolved to PT start datetimes with .dur minutes."""
    out = []
    for g in games:
        if not g.get('start_pt'): continue
        s = g['start_pt']
        e = s + dt.timedelta(minutes=g['dur'])
        out.append({'start': s, 'end': e, 'game': g})
    return out

def day_view(day, items, default_caps=("05:00", "23:59")):
    """Return busy/free split for one Pacific date."""
    ds = dt.datetime.combine(day, dt.time(0, 0), PT)
    de = dt.datetime.combine(day, dt.time(23, 59), PT)
    busy = [(max(i['start'], ds), min(i['end'], de)) for i in items
            if i['start'] < de and i['end'] > ds]
    free = complement(ds, de, busy)
    return {day: {'busy': busy, 'free': free}}

def vacate_analysis(days_index, windows, min_days=5, max_days=21):
    """Sliding-window search: find the longest runs of ALL-FREE days."""
    results = {}
    for year, (first, last) in windows.items():
        d = first
        runs = []
        cur = None
        while d <= last:
            rec = days_index.get(d.isoformat())
            free = bool(rec and rec.get('all_free'))
            if free:
                if cur is None: cur = {'start': d, 'end': d}
                else: cur['end'] = d
            else:
                if cur: runs.append(cur); cur = None
            d += dt.timedelta(days=1)
        if cur: runs.append(cur)
        runs.sort(key=lambda r: (r['end'] - r['start']).days + 1, reverse=True)
        results[year] = runs[:40]
    return results
