#!/usr/bin/env python3
"""Build data/games.json from the collected official raw sources (no network needed)."""
import json, os, re, sys, glob, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from parsers import mlb_games, nfl_games, ncaaf_games, wwo_list, wwo_event_detail

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw')
OUT = os.path.join(ROOT, 'data')

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={y}&gameTypes=R,F,D,L,W,P,S"
NFL_BW = "https://www.nfl.com/schedules/2026/by-week/week-{w}/"
NFL_SF = "https://www.49ers.com/schedule/"
STAN_SCHED = "https://gostanford.com/sports/football/schedule?season=2026&view=table"
CAL_SCHED = "https://calbears.com/sports/football/schedule"
WWO = "https://www.westwoodonesports.com/nfl-schedule/"

games = []

# ---------------------------------------------------------------- MLB
for year in (2026, 2027):
    path = os.path.join(RAW, f'mlb_{year}_all.json')
    if not os.path.exists(path): continue
    gs = mlb_games(open(path, 'rb').read(), MLB_API.format(y=year))
    for g in gs: g['season'] = year
    games += gs
    print(f'MLB {year}: {len(gs)}')

# ---------------------------------------------------------------- NFL (2026)
seen = {}
for f in sorted(glob.glob(os.path.join(RAW, 'nfl2026', 'nfl_*_week*.html'))):
    base = os.path.basename(f)
    m = re.match(r'nfl_(PRE|REG|POST)_week(\d+)\.html', base)
    if not m: continue
    wk = int(m.group(2))
    type_ = 'Preseason' if wk <= 4 else ('Regular Season' if wk <= 18 else 'Postseason')
    url = NFL_BW.format(w=wk)
    for g in nfl_games(open(f, encoding='utf-8', errors='ignore').read(), url, type_, wk):
        if g['gameId'] in seen: continue
        seen[g['gameId']] = True
        g['season'] = 2026
        games.append(g)
print('NFL 2026:', len(seen))
print('  NFL months covered:', sorted({g['utc'][:7] for g in games if g['league']=='NFL'}))

# ---------------------------------------------------------------- NCAAF
for school, fname, url in (('Stanford', 'stanford_2026.html', STAN_SCHED),
                           ('California', 'cal_2026.html', CAL_SCHED)):
    path = os.path.join(RAW, 'ncaaf', fname)
    if not os.path.exists(path): continue
    gs = ncaaf_games(open(path, encoding='utf-8', errors='ignore').read(), url, school)
    for g in gs: g['season'] = 2026
    games += gs
    print(f'NCAAF {school}: {len(gs)}')

# ---------------------------------------------------------------- Westwood One
# upcoming grid is the authoritative "current" list; past grid gives history
wwo_events = []
for fname, url in (('wwo_eg_all_t.html', "https://www.westwoodonesports.com/more/eventGrid?id=all&range=current&offset=0&limit=400&timezone=America/Los_Angeles"),
                   ('wwo_past.html',     "https://www.westwoodonesports.com/more/eventGrid?id=all&range=past&offset=0&limit=400&timezone=America/Los_Angeles")):
    p = os.path.join(RAW, fname)
    if os.path.exists(p):
        wwo_events += wwo_list(open(p, encoding='utf-8', errors='ignore').read(), url, 2026)
# de-dupe by href
byref = {}
for e in wwo_events:
    byref.setdefault(e['href'], e)
wwo_events = list(byref.values())
print('WWO events listed:', len(wwo_events))
json.dump(wwo_events, open(os.path.join(OUT, 'wwo_events_list.json'), 'w'), indent=1)

json.dump({'generated': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
           'games': games}, open(os.path.join(OUT, 'games.json'), 'w'), indent=0)
print('TOTAL games written:', len(games))
