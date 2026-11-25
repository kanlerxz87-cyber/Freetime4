#!/usr/bin/env python3
"""Cross-check: ESPN 2026 NFL slate vs nfl.com/49ers.com. Used to fill gaps only
when the game is absent from the official pages, and always labelled cross-checked."""
import json, os, glob, datetime as dt, collections
from zoneinfo import ZoneInfo
PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_espn():
    ev = {}
    for f in glob.glob(os.path.join(ROOT, 'data/raw/espn_nfl_2026_*.json')):
        d = json.load(open(f))
        for e in d.get('events', []):
            comp = e['competitions'][0]
            teams = {}
            for c in comp['competitors']:
                teams[c['homeAway']] = c['team'].get('displayName') or c['team'].get('name')
            if 'home' not in teams or 'away' not in teams: continue
            t = dt.datetime.fromisoformat(e['date'].replace('Z', '+00:00')).astimezone(PT)
            ev[e['id']] = {'start': t, 'away': teams['away'], 'home': teams['home'],
                           'week': (e.get('week') or {}).get('number'), 'name': e.get('name'),
                           'url': 'https://www.espn.com/nfl/scoreboard/_/week/{0}/year/2026/seasontype/2'.format((e.get('week') or {}).get('number', 1))}
    return ev

def merge(site_json_path):
    d = json.load(open(site_json_path))
    games = d['games']
    espn = load_espn()
    existing = collections.defaultdict(set)
    for g in games:
        if g['league'] != 'NFL': continue
        existing[frozenset([g['away'], g['home']])].add(g['date'])
    added = []
    for eid, e in espn.items():
        ds = e['start'].date().isoformat()
        # The 2026 NFL season runs Aug 2026 -> Feb 2027. Anything earlier is the
        # 2025 season and must not leak in.
        if not ('2026-08-01' <= ds <= '2027-02-28'):
            continue
        key = frozenset([e['away'], e['home']])
        if ds in existing.get(key, ()): continue
        # allow ±1 day (UTC/late-night conversion)
        d0 = e['start'].date()
        if any(abs((d0 - dt.date.fromisoformat(x)).days) <= 1 for x in existing.get(key, ())):
            continue
        added.append({
            'league': 'NFL', 'season': 2026,
            'group': 'Preseason' if e['start'].month == 8 else 'Regular Season',
            'subtype': 'Regular Season',
            'start_iso': e['start'].isoformat(),
            'end_iso': (e['start'] + dt.timedelta(minutes=192)).isoformat(),
            'date': ds, 'dur': 192,
            'start_min': e['start'].hour * 60 + e['start'].minute,
            'away': e['away'], 'home': e['home'], 'label': f"{e['away']} at {e['home']}",
            'venue': None, 'network': None,
            'source': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2026',
            'source_label': 'ESPN site API (cross-check, not an official league page)',
            'verified': 'cross-checked', 'note': 'Not present on the nfl.com weekly pages — added from the ESPN cross-check.',
            'priority': 'high' if 'San Francisco 49ers' in (e['away'], e['home']) else 'normal',
            'high_side': ('San Francisco 49ers' if 'San Francisco 49ers' in (e['away'], e['home']) else ''),
            'radio': None, 'raw_id': f'espn-{eid}',
        })
    for a in added:
        existing[frozenset([a['away'], a['home']])].add(a['date'])
    games.extend(added)
    games.sort(key=lambda g: g['start_iso'] or '9999')
    for i, g in enumerate(games): g['id'] = i
    d['games'] = games
    d['counts'] = dict(collections.Counter(g['league'] for g in games))
    d['crosscheck_added'] = len(added)
    json.dump(d, open(site_json_path, 'w'), separators=(',', ':'))
    print('added from ESPN cross-check:', len(added))
    return added

if __name__ == '__main__':
    add = merge(os.path.join(ROOT, 'data', 'site.json'))
    for a in sorted(add, key=lambda x: x['start_iso'])[:20]:
        print(' ', a['date'], a['start_iso'][11:16], a['label'])
