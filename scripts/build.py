#!/usr/bin/env python3
"""Build data/site.json — the single data file the static site reads.

Sources of truth, in priority order:
  1. MLB official Stats API            (2026, 2027)
  2. NFL.com weekly schedule pages      (2026 regular season + Sat/Thu/Sun/Mon windows)
  3. 49ers.com official schedule        (2026 preseason + regular season, incl. week 18)
  4. gostanford.com / calbears.com      (2026 NCAAF)
  5. westwoodonesports.com event grid   (national radio slate, NFL + NCAA + other sports)
  6. ESPN site API                      (cross-check ONLY — never used as the sole source)
"""
import json, os, re, sys, glob, datetime as dt, collections
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsers import mlb_games, nfl_games, ncaaf_games, cal_games, sf49ers_schedule, sf49ers_schema_dates

PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw')
CFG = json.load(open(os.path.join(ROOT, 'config', 'config.json')))
DUR = {k: v['value'] for k, v in CFG['duration_minutes'].items()}

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={y}&gameTypes=R,F,D,L,W,P,S"
NFL_BW = "https://www.nfl.com/schedules/2026/by-week/week-{w}/"
SF_URL = "https://www.49ers.com/schedule/"
STAN = "https://gostanford.com/sports/football/schedule?season=2026&view=table"
CAL = "https://calbears.com/sports/football/schedule"
WWO_URL = "https://www.westwoodonesports.com/nfl-schedule/"

HIGH = set(CFG['priority']['high'])
GAMES = []

def pt(s_iso):
    t = dt.datetime.fromisoformat(s_iso.replace('Z', '+00:00'))
    if t.tzinfo is None: t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(PT)

def add(**g):
    g.setdefault('verified', 'verified')
    g.setdefault('priority', 'normal')
    GAMES.append(g)

# ================================================================== MLB
for year in (2026, 2027):
    p = os.path.join(RAW, f'mlb_{year}_all.json')
    if not os.path.exists(p): continue
    for g in mlb_games(open(p, 'rb').read(), MLB_API.format(y=year)):
        hi = g['away'] in HIGH or g['home'] in HIGH
        start = pt(g['utc']) if g['utc'] else None
        ver = 'verified'; note = ''
        if g['tbd'] or start is None:
            start = dt.datetime.fromisoformat(g['official_date'] + 'T19:10:00').replace(tzinfo=PT)
            ver = 'estimated'; note = 'Start time TBD in MLB Stats API — estimated 19:10 PT.'
        add(league='MLB', season=year, group=g['type_group'], subtype=g['type_label'],
            start=start, dur=DUR['MLB'], away=g['away'], home=g['home'],
            label=f"{g['away']} at {g['home']}", venue=g['venue'],
            source=g['source'], verified=ver, note=note,
            priority='high' if hi else 'normal',
            high_side='/'.join([x for x in (g['away'], g['home']) if x in HIGH]),
            radio=(None if not hi else ('KNBR 680 (Giants radios) — see radio page' if 'San Francisco Giants' in (g['away'], g['home']) else 'Athletics radio network — see radio page')),
            raw_id=str(g['gamePk']))

# ================================================================== NFL 2026
# Three official-ish sources, merged into ONE roster keyed by (home, away, week):
#   * nfl.com weekly pages      -> real UTC kickoff, network, venue
#   * 49ers.com schedule page   -> schema.org UTC instant + printed PST clock + radio
#   * ESPN site API             -> cross-check only, fills weeks nfl.com leaves empty
NFL_ROW = {}

def nfl_put(away, home, start, week, group, source, verified, note='', **kw):
    key = (home, away, week)
    # a mirrored row (same two clubs, same week, sides swapped) is the same game
    if key not in NFL_ROW and (away, home, week) in NFL_ROW:
        key = (away, home, week)
    row = NFL_ROW.get(key)
    if row is None:
        NFL_ROW[key] = {
            'league': 'NFL', 'season': 2026, 'group': group, 'subtype': group,
            'start': start, 'dur': DUR['NFL'], 'away': away, 'home': home,
            'label': f'{away} at {home}', 'venue': kw.get('venue'),
            'network': kw.get('network'), 'source': source, 'verified': verified,
            'note': note, 'priority': 'high' if 'San Francisco 49ers' in (away, home) else 'normal',
            'high_side': 'San Francisco 49ers' if 'San Francisco 49ers' in (away, home) else '',
            'radio': kw.get('radio'), 'raw_id': kw.get('raw_id'), 'week': week,
            'date_hint': kw.get('date_hint'), 'confirm': [],
        }
        return
    # second source for the same game: record agreement, keep the better time
    if start and not row['start']:
        row['start'] = start
    if start and row['start'] and abs((start - row['start']).total_seconds()) <= 900:
        row['confirm'].append(source)
        if row['verified'] == 'cross-checked' and verified == 'verified':
            row['verified'] = 'verified'
            row['source'] = source
    if kw.get('radio') and not row['radio']:
        row['radio'] = kw['radio']
    if kw.get('venue') and not row['venue']:
        row['venue'] = kw['venue']
    if kw.get('network') and not row['network']:
        row['network'] = kw['network']

# ---- pass 1: nfl.com weekly pages
for f in sorted(glob.glob(os.path.join(RAW, 'nfl2026', 'nfl_*_week*.html'))):
    m = re.match(r'nfl_(PRE|REG|POST)_week(\d+)\.html', os.path.basename(f))
    if not m: continue
    wk = int(m.group(2))
    for g in nfl_games(open(f, encoding='utf-8', errors='ignore').read(),
                       NFL_BW.format(w=wk), 'Regular Season', wk):
        s = pt(g['utc'])
        grp = 'Preseason' if s.month == 8 else 'Regular Season'
        nfl_put(g['away'], g['home'], s, wk, grp, g['source'], 'verified',
                venue=g['venue'], network=g.get('network'), raw_id=g['gameId'])
print('nfl.com pass:', len(NFL_ROW))

# ---- pass 2: 49ers.com (schema.org instant preferred, then the printed PST clock)
sf_html = open(os.path.join(RAW, 'nfl2026', '49ers_official_2026.html'),
               encoding='utf-8', errors='ignore').read()
schema = sf49ers_schema_dates(sf_html)
NICK = {'Rams': 'Los Angeles Rams', 'Dolphins': 'Miami Dolphins', 'Cardinals': 'Arizona Cardinals',
        'Broncos': 'Denver Broncos', 'Seahawks': 'Seattle Seahawks', 'Commanders': 'Washington Commanders',
        'Falcons': 'Atlanta Falcons', 'Raiders': 'Las Vegas Raiders', 'Cowboys': 'Dallas Cowboys',
        'Vikings': 'Minnesota Vikings', 'Giants': 'New York Giants', 'Chargers': 'Los Angeles Chargers',
        'Chiefs': 'Kansas City Chiefs', 'Eagles': 'Philadelphia Eagles', 'Titans': 'Tennessee Titans'}
PRE_WEEK = {'Titans': 1, 'Chargers': 2, 'Raiders': 3}
PRE_HINTS = {}
for g in sf49ers_schedule(sf_html, SF_URL, 2026):
    opp = NICK.get(g['opponent'], g['opponent'])
    away, home = (opp, 'San Francisco 49ers') if g['at_vs'] == 'VS' else ('San Francisco 49ers', opp)
    if g['subtype'] == 'Preseason':
        wk = -PRE_WEEK.get(g['opponent'], 0)
    else:
        wk = g['week']
    ref = schema.get(('reg', 2026, g['week'])) if g['subtype'] == 'Regular Season' else None
    start = None
    if ref:
        start = dt.datetime.fromisoformat(ref).replace(tzinfo=dt.timezone.utc).astimezone(PT)
    elif g['clock']:
        m2 = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', g['clock'])
        h = int(m2.group(1)) % 12 + (12 if m2.group(3) == 'PM' else 0)
        d0 = dt.date.fromisoformat(g['date'])
        if d0.month == 1: d0 = d0.replace(year=d0.year + 1)
        start = dt.datetime(d0.year, d0.month, d0.day, h, int(m2.group(2)), tzinfo=PT)
    if start is None and g['subtype'] == 'Preseason':
        # 49ers.com prints only "FINAL / L 13-19" for past preseason games - no kickoff.
        # The date is official; the time comes from the ESPN cross-check.
        d0 = dt.date.fromisoformat(g['date'])
        nfl_put(away, home, None, wk, 'Preseason', SF_URL, 'cross-checked',
                note='Date from 49ers.com; kickoff not printed there (game already played), '
                     'so the time comes from the ESPN cross-check.',
                venue=g['venue'], raw_id=f"sf-pre-{wk}", date_hint=d0.isoformat())
        continue
    if start is None:
        # week 18 is published as "TBD / AT Cardinals": no date and no kickoff exist yet
        NFL_TBD = globals().get('NFL_TBD', [])
        NFL_TBD.append({'away': away, 'home': home, 'venue': g['venue'],
                        'radio': g['radio'], 'week': wk})
        globals()['NFL_TBD'] = NFL_TBD
        continue
    nfl_put(away, home, start, wk, g['subtype'], SF_URL, 'verified',
            venue=g['venue'], network=g['network'], radio=g['radio'],
            raw_id=f"sf-{g['subtype'][:3]}-{wk}")
print('after 49ers pass:', len(NFL_ROW), 'unpublished/TBD:', len(globals().get('NFL_TBD', [])))
for row in NFL_ROW.values(): GAMES.append(row)
nfl_nflcom = len(NFL_ROW)

# ================================================================== NCAAF
for school, fname, url in (('Stanford', 'stanford_2026.html', STAN), ('California', 'cal_2026.html', CAL)):
    p = os.path.join(RAW, 'ncaaf', fname)
    if not os.path.exists(p): continue
    txt = open(p, encoding='utf-8', errors='ignore').read()
    if school == 'Stanford':
        for g in ncaaf_games(txt, url, school):
            start = pt(g['utc'])
            away = g['school'] if g['at_vs'] == 'at' else g['away']
            home = g['away'] if g['at_vs'] == 'at' else g['school']
            add(league='NCAAF', season=2026, group='Regular Season', subtype='Regular Season',
                start=start, dur=DUR['NCAAF'], away=away, home=home,
                label=f"{away} at {home}", venue=g['venue'], source=url,
                priority='high', high_side='Stanford', radio='KNBR 104.5 FM / 680 AM',
                verified='verified' if not g['tbd'] else 'estimated',
                note='' if not g['tbd'] else 'Kickoff TBD on the official site.', raw_id=f"stan-{start.date()}")
    else:
        for g in cal_games(txt, url):
            c = g['clock']
            m = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', c.upper())
            h = int(m.group(1)) % 12 + (12 if m.group(3) == 'PM' else 0)
            d = dt.date.fromisoformat(g['date'])
            start = dt.datetime(d.year, d.month, d.day, h, int(m.group(2) or 0), tzinfo=PT)
            away = 'California' if g['at_vs'].startswith('at') else g['opponent']
            home = g['opponent'] if g['at_vs'].startswith('at') else 'California'
            add(league='NCAAF', season=2026, group='Regular Season', subtype='Regular Season',
                start=start, dur=DUR['NCAAF'], away=away, home=home,
                label=f"{away} at {home}", venue=g['venue'], source=url,
                priority='high', high_side='California', radio=g['radio'],
                verified='verified', raw_id=g['gameId'])

# ================================================================== Westwood One
for f in glob.glob(os.path.join(RAW, 'wwo_events', '*.json')):
    d = json.load(open(f))
    ld = d['ld']
    sd = ld.get('startDate')
    if not sd: continue
    start = pt(sd)
    name = ld.get('name', '')
    desc = re.sub('<[^>]+>', '', ld.get('description', '') or '')
    low = name.lower()
    if re.search(r'\b(at|vs\.?)\b', low):
        if ' vs' in low:
            a, b = re.split(r'\s+vs\.?\s+', name, maxsplit=1)
        else:
            a, b = re.split(r'\s+at\s+', name, maxsplit=1)
        away, home = a.strip(), b.strip()
    else:
        away, home = name, ''
    # sport classification
    if re.search(r'nfl|week 1[0-8]|thanksgiving|christmas day nfl|sunday night football|monday night football|thursday night football|super bowl|wild card|divisional|conference championship', low):
        sport = 'NFL'
    elif re.search(r'sec championship|army vs navy|michigan|ohio state|duke at florida|cfb|college football', low):
        sport = 'NCAAF'
    elif re.search(r'uswnt|usmnt|soccer', low):
        sport = 'SOCCER'
    elif re.search(r'college world series|mcws', low):
        sport = 'COLLEGE BASEBALL'
    elif re.search(r'lacrosse', low):
        sport = 'LACROSSE'
    elif re.search(r'golf', low):
        sport = 'GOLF'
    else:
        sport = 'OTHER'
    if start.year < 2026: continue
    add(league='WWO', season=start.year, group='National radio', subtype=sport,
        start=start, dur=DUR.get('NFL', 192) if sport in ('NFL', 'NCAAF') else 180,
        away=away, home=home, label=name, venue=(ld.get('location') or {}).get('name'),
        source=d['url'], priority='high', high_side='Westwood One national radio',
        radio='Westwood One national feed (local affiliate — see radio page)',
        verified='verified', note=desc, raw_id=d['href'])

# ================================================================== order + emit
GAMES.sort(key=lambda g: g['start'] or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
for i, g in enumerate(GAMES):
    g['id'] = i
    if g['start'] is None:
        g['start_iso'] = None
        g['date'] = g.get('date_hint')
        g['end_iso'] = None
        g['start_min'] = None
    else:
        g['start_iso'] = g['start'].isoformat() if g['start'] else None
        g['date'] = g['start'].date().isoformat()
        g['end_iso'] = (g['start'] + dt.timedelta(minutes=g['dur'])).isoformat()
        g['start_min'] = g['start'].hour * 60 + g['start'].minute
    del g['start']

# unverified / not-released markers
UNRELEASED = []
for league, year, url, note in [
    ('MLB', 2028, 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2028',
     'MLB Stats API returns zero games for 2028 — the schedule has not been released.'),
    ('MLB', 2029, 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2029',
     'MLB Stats API returns zero games for 2029 — the schedule has not been released.'),
    ('NFL', 2027, 'https://www.nfl.com/schedules/2027/REG/',
     'nfl.com/schedules/2027 pages render 2026 data; 2027 has not been released (the 49ers call their 2027 page "historical" and list no games).'),
    ('NFL', 2028, 'https://www.nfl.com/schedules/2028/REG/',
     'nfl.com/schedules/2028 pages render 2026 data; 2028 has not been released.'),
    ('NFL', 2029, 'https://www.nfl.com/schedules/2029/REG/',
     'nfl.com/schedules/2029 pages render 2026 data; 2029 has not been released.'),
    ('NCAAF', 2027, 'https://gostanford.com/sports/football/schedule',
     'Stanford publishes only the current season; a 2027 request returns the 2026 slate.'),
    ('NCAAF', 2028, 'https://calbears.com/sports/football/schedule',
     'Cal publishes only the current season; a 2028 request returns the 2026 slate.'),
]:
    UNRELEASED.append({'league': league, 'year': year, 'source': url, 'note': note})

# 2027 WWO national schedule (published through Week 18)
wwo_2027 = [g for g in GAMES if g['league'] == 'WWO' and g['season'] == 2027]

out = {
    'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
    'config': CFG,
    'games': GAMES,
    'unreleased': UNRELEASED,
    'counts': dict(collections.Counter(g['league'] for g in GAMES)),
    'date_range': [GAMES[0]['date'], GAMES[-1]['date']] if GAMES else [],
}
json.dump(out, open(os.path.join(ROOT, 'data', 'site.json'), 'w'), separators=(',', ':'))
print('games', len(GAMES), out['counts'])
print('range', out['date_range'])
nfl_sf_added = sum(1 for g in GAMES if g['league']=='NFL' and g.get('source')==SF_URL)
print('NFL nfl.com', nfl_nflcom, '| 49ers.com-only rows', nfl_sf_added,
      '| confirmed by 2+ sources', sum(1 for g in GAMES if g['league']=='NFL' and len(g.get('confirm') or [])>0))
