#!/usr/bin/env python3
"""Assemble data/calendar.json: every tracked game, resolved to Pacific time,
duration-estimated, priority-flagged, and marked VERIFIED or ESTIMATED."""
import json, os, re, sys, glob, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from zoneinfo import ZoneInfo
from parsers import mlb_games, nfl_games, ncaaf_games, cal_games

PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw')
CFG = json.load(open(os.path.join(ROOT, 'config', 'config.json')))
DUR = {k: v['value'] for k, v in CFG['duration_minutes'].items()}

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={y}&gameTypes=R,F,D,L,W,P,S"
NFL_BW = "https://www.nfl.com/schedules/2026/by-week/week-{w}/"
NFL_SF = "https://www.49ers.com/schedule/"
STAN = "https://gostanford.com/sports/football/schedule?season=2026&view=table"
CAL = "https://calbears.com/sports/football/schedule"
WWO_LIST = "https://www.westwoodonesports.com/more/eventGrid?id=all&range={r}&offset=0&limit=400&timezone=America/Los_Angeles"

HIGH_TEAMS = set(CFG['priority']['high'])
out = []

def mk(**kw):
    """Common record with derived Pacific times + duration."""
    dur = DUR[kw['league']]
    s_utc = kw.get('utc')
    start_pt = None
    if s_utc:
        t = dt.datetime.fromisoformat(s_utc.replace('Z', '+00:00'))
        if t.tzinfo is None: t = t.replace(tzinfo=dt.timezone.utc)
        start_pt = t.astimezone(PT)
    kw['start_pt'] = start_pt
    kw['dur'] = dur
    return kw

# ------------------------------------------------------------------ MLB
for year in (2026, 2027):
    p = os.path.join(RAW, f'mlb_{year}_all.json')
    if not os.path.exists(p): continue
    for g in mlb_games(open(p, 'rb').read(), MLB_API.format(y=year)):
        hi = g['away'] in HIGH_TEAMS or g['home'] in HIGH_TEAMS
        tbd = g['tbd']
        rec = mk(league='MLB', season=year, group=g['type_group'], subtype=g['type_label'],
                 utc=g['utc'], date=g['official_date'], away=g['away'], home=g['home'],
                 venue=g['venue'], source=g['source'], verif='verified',
                 priority='high' if hi else 'normal', raw_id=str(g['gamePk']),
                 radio=None, tbd=tbd)
        if tbd or not rec['start_pt']:
            rec['verif'] = 'estimated'
            rec['est_note'] = 'MLB Stats API reports this game with startTimeTBD; start estimated at 19:10 PT.'
            rec['utc'] = f"{g['official_date']}T02:10:00Z"
            rec = mk(**{k: v for k, v in rec.items() if k != 'start_pt'})
        rec['label'] = f"{g['away']} at {g['home']}"
        out.append(rec)
    print('MLB', year, len([x for x in out if x['league'] == 'MLB' and x['season'] == year]))

# 2028 / 2029 — not released: emit an explicit "unreleased" marker instead of fake games
for year in (2028, 2029):
    out.append(mk(league='MLB', season=year, group='Unreleased', subtype='Schedule not published',
                  utc=None, date=None, away=None, home=None, venue=None, source=None,
                  verif='unreleased', priority='normal', raw_id=None, radio=None,
                  label=f'MLB {year} schedule has not been released by MLB as of 2026-11-25',
                  est_note='MLB Stats API returns an empty schedule for this season.'))

# ------------------------------------------------------------------ NFL 2026
seen = set()
for f in sorted(glob.glob(os.path.join(RAW, 'nfl2026', 'nfl_*_week*.html'))):
    m = re.match(r'nfl_(PRE|REG|POST)_week(\d+)\.html', os.path.basename(f))
    if not m: continue
    wk = int(m.group(2))
    sub = 'Preseason' if wk <= 4 else ('Regular Season' if wk <= 18 else 'Postseason')
    for g in nfl_games(open(f, encoding='utf-8', errors='ignore').read(),
                       NFL_BW.format(w=wk), sub, wk):
        if g['gameId'] in seen: continue
        seen.add(g['gameId'])
        hi = 'San Francisco 49ers' in (g['away'], g['home'])
        rec = mk(league='NFL', season=2026, group=sub, subtype=sub, utc=g['utc'],
                 date=g['utc'][:10], away=g['away'], home=g['home'], venue=g['venue'],
                 source=g['source'], verif='verified',
                 priority='high' if hi else 'normal', raw_id=g['gameId'],
                 radio='Westwood One (if on the national list)', tbd=False,
                 network=g.get('network'), week=g.get('week'))
        rec['label'] = f"{g['away']} at {g['home']}"
        out.append(rec)
print('NFL2026', len(seen))

# ------------------------------------------------------------------ NCAAF
for school, fname, url in (('Stanford', 'stanford_2026.html', STAN),
                           ('California', 'cal_2026.html', CAL)):
    p = os.path.join(RAW, 'ncaaf', fname)
    if not os.path.exists(p): continue
    txt = open(p, encoding='utf-8', errors='ignore').read()
    if school == 'Stanford':
        gs = ncaaf_games(txt, url, school)
        for g in gs:
            rec = mk(league='NCAAF', season=2026, group='Regular Season', subtype='Regular Season',
                     utc=g['utc'], date=g['utc'][:10],
                     away=(g['school'] if g['at_vs'] == 'at' else g['away']),
                     home=(g['away'] if g['at_vs'] == 'at' else g['school']),
                     venue=g['venue'], source=url, verif='verified', priority='high',
                     raw_id=f"stan-{g['utc'][:10]}",
                     radio='KNBR 104.5 FM / 680 AM (KTCT 1050 - see radio page)', tbd=g['tbd'])
            rec['label'] = f"{rec['away']} at {rec['home']}"
            out.append(rec)
    else:
        for g in cal_games(txt, url):
            m2 = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', g['clock'].upper())
            h24 = int(m2.group(1)) % 12 + (12 if m2.group(3) == 'PM' else 0)
            minute = int(m2.group(2) or 0)
            local = dt.datetime.fromisoformat(g['date'] + f'T{h24:02d}:{minute:02d}:00').replace(tzinfo=PT)
            rec = mk(league='NCAAF', season=2026, group='Regular Season', subtype='Regular Season',
                     utc=local.astimezone(dt.timezone.utc).isoformat(), date=g['date'],
                     away=('California' if g['at_vs'].startswith('at') else g['opponent']),
                     home=(g['opponent'] if g['at_vs'].startswith('at') else 'California'),
                     venue=g['venue'], source=url, verif='verified', priority='high',
                     raw_id=g['gameId'], radio=g.get('radio'), tbd=g['tbd'])
            rec['label'] = f"{rec['away']} at {rec['home']}"
            out.append(rec)
print('NCAAF total', len([x for x in out if x['league'] == 'NCAAF']))

json.dump([{**r, 'start_pt': (r['start_pt'].isoformat() if r.get('start_pt') else None)} for r in out],
          open(os.path.join(ROOT, 'data', 'calendar.json'), 'w'), indent=0)
print('TOTAL', len(out))
