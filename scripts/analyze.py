#!/usr/bin/env python3
"""Free-time + vacation-window analysis, written into data/site.json.

Definitions
-----------
BUSY minute : any minute inside [start, start+duration) of a tracked broadcast.
FREE minute : every other minute of the day.
Whether a broadcast is audible in 94122 on an AM/FM radio is decided by the
'audible' rule below; the strict "everything" mode ignores it.
"""
import json, os, sys, datetime as dt, collections
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Which broadcasts are treated as *audible in 94122*.
#  - MLB Giants: KNBR 680 (official)
#  - MLB Athletics: Bay Area affiliate KNEW 960 (iHeart announcement) -> audible
#  - NFL 49ers: KSAN 107.7 / KNBR 104.5 / 680 (official 49ers page) -> audible
#  - Stanford / Cal: KNBR / KSFO 810 (official school pages) -> audible
#  - National (WWO) NFL: audible ONLY when the same game is also carried locally
#    by a Bay Area station. Local carriage of national games is not published,
#    so by default these are NOT counted; toggle with mode='audible_plus_national'.
AUDIBLE_LOCAL = {'San Francisco Giants', 'Athletics', 'San Francisco 49ers', 'Stanford', 'California'}

def parse(g):
    s = dt.datetime.fromisoformat(g['start_iso'])
    return s, s + dt.timedelta(minutes=g['dur'])

def is_audible(g):
    """Is this broadcast confirmed to be on a Bay Area station?

    Evidence used (all from official pages):
      * MLB Giants              -> KNBR 680            (mlb.com/giants/team/broadcasters)
      * MLB Athletics           -> KNEW 960 Bay Area   (club's iHeartRadio release)
      * NFL 49ers               -> KSAN 107.7 / KNBR 104.5 / 680 (49ers.com game cards)
      * NCAAF Cal                -> KSFO 810 / KNBR     (calbears.com game cards)
      * NCAAF Stanford          -> NOT CONFIRMED for 2026 -> excluded
      * Westwood One national   -> affiliate NOT confirmed -> excluded
      * estimated seasons       -> excluded
    """
    if g.get('estimated_window'):
        return False
    if g['league'] == 'MLB':
        return g.get('high_side') in ('San Francisco Giants', 'Athletics')
    if g['league'] == 'NFL':
        return 'San Francisco 49ers' in (g.get('away') or '', g.get('home') or '')
    if g['league'] == 'NCAAF':
        return g.get('high_side') == 'California'
    return False

def windows_for_day(day_start, day_end, intervals):
    """Return (free_windows, busy_windows) clipped to the day."""
    busy = sorted((max(s, day_start), min(e, day_end)) for s, e in intervals
                  if s < day_end and e > day_start)
    merged = []
    for s, e in busy:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    free, cur = [], day_start
    for s, e in merged:
        if s > cur: free.append((cur, s))
        cur = max(cur, e)
    if cur < day_end: free.append((cur, day_end))
    return free, merged

def hm(t):
    return t.strftime('%H:%M')

def ampm(t):
    return t.strftime('%-I:%M %p')

def main():
    d = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
    games = d['games']
    cfg = d['config']

    by_day = collections.defaultdict(list)
    for g in games:
        if not g.get('start_iso'): continue      # TBD / unpublished: cannot occupy a minute
        s, e = parse(g)
        by_day[s.date().isoformat()].append((s, e, g))

    # ------------------------------------------------------------------ day index
    days = {}
    first = dt.date.fromisoformat(min(by_day)) if by_day else dt.date(2026, 1, 1)
    last = dt.date.fromisoformat(max(by_day)) if by_day else dt.date(2027, 9, 30)
    # extend to cover full MLB/NFL 2027 season even where no game exists
    last = max(last, dt.date(2027, 9, 30))

    cur = first
    while cur <= last:
        ds = cur.isoformat()
        start = dt.datetime.combine(cur, dt.time(0, 0), PT)
        end = dt.datetime.combine(cur, dt.time(23, 59), PT)
        items = by_day.get(ds, [])
        # strict mode: everything counts
        strict = [(s, e) for s, e, g in items]
        free_s, busy_s = windows_for_day(start, end, strict)
        # audible mode: only what you can hear on a Bay Area radio
        audible = [(s, e) for s, e, g in items if is_audible(g)]
        free_a, busy_a = windows_for_day(start, end, audible)
        days[ds] = {
            'date': ds,
            'dow': cur.strftime('%a'),
            'weekday': cur.weekday(),
            'games': len(items),
            'highest': ('high' if any(g['priority'] == 'high' for s, e, g in items) else ('normal' if items else None)),
            'all_free': len(items) == 0,
            'busy_strict': [[hm(a), hm(b)] for a, b in busy_s],
            'free_strict': [[hm(a), hm(b)] for a, b in free_s],
            'free_strict_min': sum(int((b - a).total_seconds() // 60) for a, b in free_s),
            'busy_audible': [[hm(a), hm(b)] for a, b in busy_a],
            'free_audible': [[hm(a), hm(b)] for a, b in free_a],
            'free_audible_min': sum(int((b - a).total_seconds() // 60) for a, b in free_a),
        }
        cur += dt.timedelta(days=1)

    # ------------------------------------------------------------------ vacation windows
    def runs(mode_key, lo, hi):
        out, cur_run = [], None
        day = lo
        while day <= hi:
            rec = days.get(day.isoformat())
            ok = bool(rec and rec[mode_key])
            if ok:
                if cur_run is None: cur_run = {'start': day, 'end': day, 'days': 1}
                else:
                    cur_run['end'] = day
                    cur_run['days'] = (cur_run['end'] - cur_run['start']).days + 1
            else:
                if cur_run: out.append(cur_run); cur_run = None
            day += dt.timedelta(days=1)
        if cur_run: out.append(cur_run)
        out.sort(key=lambda r: (-r['days'], r['start']))
        return out

    # one combined window lets a trip that straddles New Year be found
    lo_all = dt.date(min(cfg['vacation_seasons']), 1, 1)
    hi_all = dt.date(max(cfg['vacation_seasons']), 12, 31)

    def no_audible_runs_all(lo, hi):
        out, cur_run = [], None
        day = lo
        while day <= hi:
            rec = days.get(day.isoformat())
            ok = bool(rec and not rec['busy_audible'])
            if ok:
                if cur_run is None: cur_run = {'start': day, 'end': day, 'days': 1}
                else:
                    cur_run['end'] = day; cur_run['days'] = (cur_run['end'] - cur_run['start']).days + 1
            else:
                if cur_run: out.append(cur_run); cur_run = None
            day += dt.timedelta(days=1)
        if cur_run: out.append(cur_run)
        out.sort(key=lambda r: (-r['days'], r['start']))
        return out

    seasons = {}
    for year in cfg['vacation_seasons']:
        lo = dt.date(year, 1, 1); hi = dt.date(year, 12, 31)
        seasons[year] = {
            'all_free_strict': [{**r, 'start': r['start'].isoformat(), 'end': r['end'].isoformat()}
                                 for r in runs('all_free', lo, hi)],
            'all_free_audible': [{**r, 'start': r['start'].isoformat(), 'end': r['end'].isoformat()}
                                  for r in runs('all_free', lo, hi)],
        }

    # Audible-but-no-sports-at-all: use "no audible broadcast" instead of all_free
    def no_audible_runs(lo, hi):
        out, cur_run = [], None
        day = lo
        while day <= hi:
            rec = days.get(day.isoformat())
            ok = bool(rec and not rec['busy_audible'])
            if ok:
                if cur_run is None: cur_run = {'start': day, 'end': day, 'days': 1}
                else:
                    cur_run['end'] = day; cur_run['days'] = (cur_run['end'] - cur_run['start']).days + 1
            else:
                if cur_run: out.append(cur_run); cur_run = None
            day += dt.timedelta(days=1)
        if cur_run: out.append(cur_run)
        out.sort(key=lambda r: (-r['days'], r['start']))
        return out

    for year in cfg['vacation_seasons']:
        rr = no_audible_runs(dt.date(year, 1, 1), dt.date(year, 12, 31))
        seasons[year]['no_radio_runs'] = [{**r, 'start': r['start'].isoformat(), 'end': r['end'].isoformat()} for r in rr]

    # ------------------------------------------------------------------ month summaries
    months = {}
    for ds, rec in days.items():
        mk = ds[:7]
        m = months.setdefault(mk, {'month': mk, 'days': 0, 'all_free_days': 0,
                                   'free_minutes': 0, 'busy_minutes': 0, 'games': 0,
                                   'high_games': 0})
        m['days'] += 1
        m['all_free_days'] += 1 if rec['all_free'] else 0
        m['free_minutes'] += rec['free_audible_min']
        m['busy_minutes'] += 1440 - rec['free_audible_min']
        m['games'] += rec['games']
        m['high_games'] += 1 if rec['highest'] == 'high' else 0
    for mk, m in months.items():
        m['free_pct'] = round(100 * m['free_minutes'] / (m['days'] * 1439), 1)

    # ------------------------------------------------------------------ season windows (sports-year)
    season_summary = collections.defaultdict(lambda: {'games': 0, 'first': None, 'last': None})
    for g in games:
        key = f"{g['league']} {g['season']}"
        s = season_summary[key]
        s['games'] += 1
        if s['first'] is None or g['date'] < s['first']: s['first'] = g['date']
        if s['last'] is None or g['date'] > s['last']: s['last'] = g['date']

    # ---------------------------------------------------------------- game-free stretches
    # Truthful "nothing on" view: the gap between the END of one broadcast and the
    # START of the next, measured in whole days with no broadcast overlapping them.
    def stretches(pred, lo, hi):
        rows = [(dt.datetime.fromisoformat(x['start_iso']), dt.datetime.fromisoformat(x['end_iso']))
                for x in games if pred(x) and x.get('start_iso')]
        iv = sorted(rows)
        merged2 = []
        for s, e in iv:
            if merged2 and s <= merged2[-1][1]:
                merged2[-1][1] = max(merged2[-1][1], e)
            else:
                merged2.append([s, e])
        out = []
        for i in range(len(merged2) - 1):
            a = merged2[i][1].astimezone(PT)
            b = merged2[i + 1][0].astimezone(PT)
            # first whole untouched day and last whole untouched day
            first = (a.date() + dt.timedelta(days=1)) if a.time() != dt.time(0, 0) else a.date()
            last = (b.date() - dt.timedelta(days=1)) if b.time() != dt.time(0, 0) else b.date()
            days = (last - first).days + 1
            if days >= 4 and last >= lo and first <= hi:
                out.append({'start': max(first, lo).isoformat(), 'end': min(last, hi).isoformat(),
                            'days': days, 'hrs': round((b - a).total_seconds() / 3600, 1)})
        out.sort(key=lambda r: (-r['days'], r['start']))
        return out

    lo_y, hi_y = dt.date(2026, 1, 1), dt.date(2030, 12, 31)
    d['stretches_audible'] = stretches(is_audible, lo_y, hi_y)
    d['stretches_strict'] = stretches(lambda g: not g.get('estimated_window'), lo_y, hi_y)

    combined = no_audible_runs_all(lo_all, hi_all)
    d['combined_windows'] = [{**r, 'start': r['start'].isoformat(), 'end': r['end'].isoformat()} for r in combined]

    d['days'] = days
    d['seasons'] = seasons
    d['months'] = months
    d['season_summary'] = season_summary
    d['day_range'] = [first.isoformat(), last.isoformat()]

    # ---------------------------------------------------------------- compact output
    # The pages only need these fields per game; dropping the rest keeps the
    # published JSON small enough to load fast on a phone.
    KEEP = ('id', 'league', 'season', 'group', 'subtype', 'start_iso', 'end_iso', 'date',
            'away', 'home', 'label', 'venue', 'network', 'source', 'verified', 'note',
            'priority', 'high_side', 'radio', 'dur', 'estimated_window', 'start_min')
    d['games'] = [{k: g[k] for k in KEEP if k in g} for g in d['games']]
    json.dump(d, open(os.path.join(ROOT, 'data', 'site.json'), 'w'), separators=(',', ':'))
    print('bytes', os.path.getsize(os.path.join(ROOT, 'data', 'site.json')))
    print('days', len(days), 'range', d['day_range'])
    for y in cfg['vacation_seasons']:
        print(y, 'all-free runs', len(seasons[y]['all_free_audible']), 'best',
              seasons[y]['all_free_audible'][0] if seasons[y]['all_free_audible'] else None)
        print('   no-radio runs', len(seasons[y]['no_radio_runs']),
              seasons[y]['no_radio_runs'][0] if seasons[y]['no_radio_runs'] else None)

if __name__ == '__main__':
    main()
