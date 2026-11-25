#!/usr/bin/env python3
"""Clearly-labelled ESTIMATES for seasons the leagues have NOT released.

Method (identical for every league):
  * take the most recent RELEASED season for that league,
  * record the season's month/day span and, for each weekday, the frequency of
    every observed start time,
  * rebuild the same span in the target year (so leap years cannot shift it),
    keeping the most common start times per weekday,
  * emit ONE row per start time per day and never invent opponents or matchups.

Every row is verified='estimated' with an explicit note. Nothing here is
presented as a real schedule.
"""
import json, os, sys, collections, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEAGUE_SOURCES = {
    'MLB': 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&gameTypes=R,F,D,L,W,P,S',
    'NFL': 'https://www.nfl.com/schedules/2026/by-week/week-1/',
    'NCAAF': 'https://gostanford.com/sports/football/schedule',
}
NOTE = {
    'MLB': ('ESTIMATE — MLB has not released this schedule. Rebuilt from the released {ref} season: '
            'same month/day span, same weekday pattern, same first-pitch times. Opponents are '
            'deliberately omitted because the interleague rotation is unknown.'),
    'NFL': ('ESTIMATE — the NFL has not released this schedule. Rebuilt from the released {ref} season: '
            'same weekday and kickoff windows. Matchups are deliberately omitted.'),
    'NCAAF': ('ESTIMATE — neither school has released this schedule. Rebuilt from the published {ref} '
              'Stanford and Cal slate: same weekdays and kickoff slots. Opponents omitted.'),
}
MAX_SLOTS = {'MLB': 6, 'NFL': 6, 'NCAAF': 5}

def main():
    d = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
    cfg = d['config']
    DUR = {k: v['value'] for k, v in cfg['duration_minutes'].items()}
    real = [g for g in d['games'] if g['verified'] not in ('estimated', 'unpublished')]

    def pattern(league, season):
        times = collections.defaultdict(collections.Counter)
        ds = []
        for g in real:
            if g['league'] != league or g['season'] != season: continue
            if not g.get('start_iso'): continue      # TBD row: no time to model from
            t = dt.datetime.fromisoformat(g['start_iso']).astimezone(PT)
            times[t.weekday()][f'{t.hour:02d}:{t.minute:02d}'] += 1
            ds.append(t.date())
        if not ds: return None, None, None
        top = {wd: [k for k, _ in c.most_common(MAX_SLOTS[league])] for wd, c in times.items()}
        return (min(ds), max(ds)), top, len(ds)

    jobs = [
        ('MLB',   2027, 2028, DUR['MLB']),
        ('MLB',   2027, 2029, DUR['MLB']),
        ('NFL',   2026, 2027, DUR['NFL']),
        ('NFL',   2026, 2028, DUR['NFL']),
        ('NFL',   2026, 2029, DUR['NFL']),
        ('NCAAF', 2026, 2027, DUR['NCAAF']),
        ('NCAAF', 2026, 2028, DUR['NCAAF']),
        ('NCAAF', 2026, 2029, DUR['NCAAF']),
    ]
    new = []
    for league, ref_year, target, dur in jobs:
        span, top, n = pattern(league, ref_year)
        if not span: 
            print('no reference data for', league, ref_year); continue
        year_shift = target - span[0].year
        lo = span[0].replace(year=span[0].year + year_shift)
        hi = span[1].replace(year=span[1].year + year_shift)
        rows = []
        day = lo
        while day <= hi:
            for hhmm in top.get(day.weekday(), ()):
                h, m = map(int, hhmm.split(':'))
                start = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=PT)
                rows.append({
                    'league': league, 'season': target, 'group': 'Estimated',
                    'subtype': 'Estimated slate',
                    'start_iso': start.isoformat(),
                    'end_iso': (start + dt.timedelta(minutes=dur)).isoformat(),
                    'dur': dur, 'date': day.isoformat(),
                    'start_min': h * 60 + m,
                    'away': None, 'home': None,
                    'label': f"{league} {target} — estimated {start.strftime('%-I:%M %p')} PT window",
                    'venue': None, 'network': None,
                    'source': LEAGUE_SOURCES[league],
                    'source_label': 'reference season only — this season is NOT released',
                    'verified': 'estimated', 'priority': 'normal', 'high_side': '',
                    'radio': None, 'raw_id': f"est-{league}-{target}-{day}-{hhmm}",
                    'note': NOTE[league].format(ref=ref_year),
                    'estimated_window': True,
                })
            day += dt.timedelta(days=1)
        print(f'{league} {target}: {len(rows)} rows  ({lo} → {hi}, pattern from {n} {ref_year} games)')
        new += rows

    games = real + new
    games.sort(key=lambda g: g['start_iso'] or '9999')
    for i, g in enumerate(games): g['id'] = i
    d['games'] = games
    d['counts'] = dict(collections.Counter(g['league'] for g in games))
    d['estimate_counts'] = dict(collections.Counter(g['league'] for g in new))
    json.dump(d, open(os.path.join(ROOT, 'data', 'site.json'), 'w'), separators=(',', ':'))
    print('total games', len(games), d['counts'])

if __name__ == '__main__':
    main()
