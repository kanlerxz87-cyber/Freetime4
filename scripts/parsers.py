"""Parsers for each official source. Pure functions: (bytes/str) -> list[dict]."""
import json, re, html as H

# ---------------------------------------------------------------- MLB
MLB_TYPE_LABEL = {
    'S':'Spring Training','R':'Regular Season','F':'Wild Card','D':'Division Series',
    'L':'League Championship Series','W':'World Series','A':'All-Star Game',
    'E':'Exhibition','C':'Special Event','P':'Postseason',
}
MLB_TYPE_GROUP = {
    'S':'Spring Training','R':'Regular Season','A':'All-Star','E':'Exhibition','C':'Special Event',
    'F':'Postseason','D':'Postseason','L':'Postseason','W':'Postseason','P':'Postseason',
}

def mlb_games(raw, source_url):
    d = json.loads(raw)
    out = []
    for dt in d.get('dates', []):
        for g in dt.get('games', []):
            out.append({
                'league': 'MLB',
                'game_type': g.get('gameType'),
                'type_group': MLB_TYPE_GROUP.get(g.get('gameType'), 'MLB'),
                'type_label': MLB_TYPE_LABEL.get(g.get('gameType'), g.get('gameType')),
                'gamePk': g.get('gamePk'),
                'official_date': g.get('officialDate'),
                'utc': g.get('gameDate'),
                'tbd': bool(g.get('status', {}).get('startTimeTBD')),
                'away': g['teams']['away']['team'].get('name'),
                'home': g['teams']['home']['team'].get('name'),
                'venue': (g.get('venue') or {}).get('name'),
                'day_night': g.get('dayNight'),
                'status': g.get('status', {}).get('detailedState'),
                'description': g.get('description') or '',
                'dh': g.get('doubleHeader'),
                'source': source_url,
            })
    return out

# ---------------------------------------------------------------- NFL.com
def _decode_rsc(text):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', text, flags=re.S)
    return ''.join(json.loads(c) for c in chunks)

def _objects_with(s, needle):
    out = []
    for m in re.finditer(re.escape(needle), s):
        depth = 0; i = m.start(); start = None
        while i > 0:
            i -= 1; c = s[i]
            if c == '}': depth += 1
            elif c == '{':
                if depth == 0: start = i; break
                depth -= 1
        if start is None: continue
        depth = 0; j = start; instr = False; esc = False
        while j < len(s):
            c = s[j]
            if instr:
                if esc: esc = False
                elif c == '\\': esc = True
                elif c == '"': instr = False
            else:
                if c == '"': instr = True
                elif c == '{': depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        try: out.append(json.loads(s[start:j+1]))
                        except Exception: pass
                        break
            j += 1
    return out

def nfl_games(text, source_url, page_type, week_hint=None):
    s = _decode_rsc(text)
    games = {}
    for o in _objects_with(s, '"homeTeamFullName"'):
        gid = o.get('gameId')
        if not gid: continue
        if gid in games:
            for k, v in o.items():
                if games[gid].get(k) in (None, '', []) and v not in (None, '', []):
                    games[gid][k] = v
        else:
            games[gid] = o
    out = []
    for g in games.values():
        if not g.get('date') or not g.get('homeTeamFullName'): continue
        out.append({
            'league': 'NFL',
            'game_type': page_type,
            'type_group': page_type,
            'gameId': g['gameId'],
            'utc': g['date'],
            'away': g.get('awayTeamFullName'),
            'home': g['homeTeamFullName'],
            'venue': g.get('venueName') or g.get('location'),
            'network': g.get('hostNetwork') or ','.join(g.get('networks') or []),
            'week': g.get('week') if week_hint is None else week_hint,
            'title': g.get('title'),
            'source': source_url,
        })
    return out

# ---------------------------------------------------------------- Stanford / Cal
def ncaaf_games(text, source_url, school):
    """Parse the rendered schedule-event-item blocks."""
    out = []
    blocks = re.split(r'<div class="schedule-event-item"', text)[1:]
    for b in blocks:
        b = b.split('<div name="scheduleAfterScheduledEvent')[0]
        m = re.search(r'<time datetime="([^"]+)" class="schedule-event-date__weekday"[^>]*>', b)
        if not m: continue
        iso = m.group(1)
        opp = re.search(r'class="schedule-event-item-team__opponent-name"[^>]*>(.*?)</strong>', b, flags=re.S)
        loc = re.search(r'class="schedule-event-item-team__location"[^>]*>(.*?)</span>', b, flags=re.S)
        clock = re.search(r'class="schedule-event-date__clock"[^>]*>(.*?)</time>', b, flags=re.S)
        atvs = 'at' if 'schedule-event-item__top--away' in b else ('vs.' if 'schedule-event-item__top--home' in b else '')
        tbd = 'TBD' in (clock.group(1) if clock else '') or 'TBA' in (clock.group(1) if clock else '')
        out.append({
            'league': 'NCAAF',
            'school': school,
            'game_type': 'Regular Season',
            'type_group': 'NCAAF',
            'gameId': None,
            'utc': iso,
            'away': H.unescape(opp.group(1)).strip() if opp else None,
            'home': school,
            'venue': H.unescape(loc.group(1)).strip() if loc else None,
            'at_vs': atvs,
            'clock': H.unescape(clock.group(1)).strip() if clock else None,
            'tbd': tbd,
            'source': source_url,
        })
    return out

# ---------------------------------------------------------------- Westwood One
WWO_MONTHS = {m: i+1 for i, m in enumerate(
    ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])}

def wwo_list(text, source_url, year_hint):
    out = []
    for m in re.finditer(r"<div class='event'>\s*<div class='info'>(.*?)</div>\s*</div>", text, flags=re.S):
        blk = m.group(1)
        name = re.search(r"<div class='name'><a href='([^']+)'>(.*?)</a></div>", blk, flags=re.S)
        date = re.search(r"<div class='date'[^>]*>(.*?)</div>", blk, flags=re.S)
        desc = re.search(r"<div class='description'>(.*?)</div>", blk, flags=re.S)
        ven = re.search(r"<div class='venue'>(.*?)</div>", blk, flags=re.S)
        if not name: continue
        dtxt = H.unescape(date.group(1)).strip() if date else ''
        out.append({
            'href': name.group(1),
            'title': H.unescape(name.group(2)).strip(),
            'date_text': dtxt,
            'desc': H.unescape(re.sub('<[^>]+>', '', desc.group(1))).strip() if desc else '',
            'venue': H.unescape(ven.group(1)).strip() if ven else '',
            'source': source_url,
            'year_hint': year_hint,
        })
    return out

def wwo_event_detail(text):
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?"@type"\s*:\s*"Event".*?\})\s*</script>',
                  text, flags=re.S)
    if not m: return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None

# ---------------------------------------------------------------- Cal (oas __NUXT_DATA__)
def _oas_load(text):
    import json as J
    m = re.search(r'id="__NUXT_DATA__"[^>]*>(.*?)</script>', text, flags=re.S)
    if not m: return None
    p = J.loads(m.group(1)); memo = {}
    def resolve(i):
        if isinstance(i, bool) or i is None or isinstance(i, float) or isinstance(i, str): return i
        if not isinstance(i, int): return i
        if i < 0: return None
        if i >= len(p): return i
        if i in memo: return memo[i]
        v = p[i]
        if isinstance(v, (str, bool, float)) or v is None: return v
        if isinstance(v, int): return resolve(v)
        if isinstance(v, list):
            if v and isinstance(v[0], str) and v[0] in ('Reactive','ShallowReactive','Ref','ShallowRef','Object'):
                return resolve(v[1])
            out = []; memo[i] = out
            for x in v: out.append(resolve(x))
            return out
        if isinstance(v, dict):
            out = {}; memo[i] = out
            for k, x in v.items(): out[k] = resolve(x)
            return out
        return v
    return resolve(0)

def _walk(obj, pred, out, depth=0, seen=None):
    if seen is None: seen = set()
    if depth > 20: return out
    if isinstance(obj, (dict, list)):
        if id(obj) in seen: return out
        seen.add(id(obj))
    if pred(obj): out.append(obj)
    if isinstance(obj, dict):
        for v in obj.values(): _walk(v, pred, out, depth+1, seen)
    elif isinstance(obj, list):
        for v in obj: _walk(v, pred, out, depth+1, seen)
    return out

CAL_MONTHS = {m: i+1 for i, m in enumerate(
    ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}

def cal_games(text, source_url, year=2026):
    """Parse Cal game cards. Cards are rendered in schedule order; the team name,
    site, venue and radio outlet follow a 'Game Info' marker."""
    out = []
    idxs = [m.start() for m in re.finditer(r's-game-card-standard__header-game-team-score', text)]
    bounds = idxs + [len(text)]
    for k in range(len(idxs)):
        seg = text[bounds[k]:bounds[k+1]]
        txt = re.sub(r'<[^>]+>', '\n', seg)
        txt = H.unescape(txt)
        lines = [x.strip() for x in txt.split('\n') if x.strip()]
        date = time_ = atvs = opp = venue = city = radio = None
        score = None
        for i, x in enumerate(lines):
            m = re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})$', x)
            if m and not date:
                date = (CAL_MONTHS[m.group(1)], int(m.group(2)))
                continue
            m2 = re.match(r'^(\d{1,2}(?::\d{2})?\s*(?:AM|PM))$', x)
            if m2 and date and not time_:
                time_ = m2.group(1); continue
            if x in ('vs', 'at') and date and not atvs:
                atvs = x
                opp = lines[i+1] if i+1 < len(lines) else None
                venue = lines[i+2] if i+2 < len(lines) else None
                city = lines[i+3] if i+3 < len(lines) else None
                continue
            if x.startswith('Radio:') and not radio:
                rest = x.split('Radio:', 1)[1].strip()
                radio = rest or (lines[i+1] if i+1 < len(lines) else None)
                continue
            mm = re.match(r'^([WL]),$', x)
            if mm: score = lines[i+1] if i+1 < len(lines) else None
        if not date: continue
        out.append({
            'league': 'NCAAF', 'school': 'California', 'game_type': 'Regular Season',
            'type_group': 'NCAAF', 'gameId': f'cal-{year}-{date[0]:02d}-{date[1]:02d}',
            'date': f'{year}-{date[0]:02d}-{date[1]:02d}', 'utc': None, 'clock': time_,
            'at_vs': atvs + (' ' if atvs in ('vs','at') else ''),
            'opponent': opp, 'venue': venue, 'city': city, 'radio': radio,
            'result': score, 'tbd': (time_ or '').upper() == 'TBD',
            'source': source_url,
        })
    return out

# ---------------------------------------------------------------- 49ers.com official schedule
SF_MONTHS = {m: i+1 for i, m in enumerate(
    ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}

def sf49ers_schedule(text, source_url, year=2026):
    """Parse 49ers.com schedule cards: WEEK n · Thu 08/13 · 5:15 PM PST · VS/AT · Team · Net · Radio · Venue"""
    out = []
    lines = [H.unescape(x).strip() for x in re.sub(r'<[^>]+>', '\n', text).split('\n')]
    lines = [x for x in lines if x]
    section = None
    i = 0
    while i < len(lines):
        x = lines[i]
        if x.upper() == 'PRESEASON': section = 'Preseason'
        elif x.upper() == 'REGULAR SEASON': section = 'Regular Season'
        elif x.upper() in ('POSTSEASON', 'PLAYOFFS'): section = 'Postseason'
        m = re.match(r'^WEEK (\d+)$', x)
        if m and section:
            wk = int(m.group(1))
            j = i + 1
            date = time_ = atvs = opp = venue = net = radio = None
            while j < len(lines) and j < i + 16:
                y = lines[j]
                md = re.match(r'^·?\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{2})/(\d{2})$', y)
                if md and not date:
                    date = (SF_MONTHS.get({v: k for k, v in SF_MONTHS.items()}.get(int(md.group(2))), 1), int(md.group(2)), int(md.group(3)))
                    date = (int(md.group(2)), int(md.group(3)))
                elif re.match(r'^·?\s*\d{1,2}:\d{2}\s*(AM|PM)\s*(PST|PDT)?$', y) and not time_:
                    time_ = re.sub(r'^·\s*', '', y)
                elif y.upper() in ('VS', 'AT') and not atvs:
                    atvs = y.upper(); opp = lines[j+1] if j+1 < len(lines) else None
                elif 'FM' in y or re.match(r'^\d{3,4} AM$', y) or 'AM /' in y:
                    if not radio: radio = y
                elif re.match(r'^(FOX|CBS|NBC|ESPN|ABC|Prime Video|NFL Network|NETFLIX)$', y, re.I) and not net:
                    net = y
                elif opp and y.endswith(('Stadium', 'Field', 'Park', 'Centre', 'Center', 'Ground', 'Dome')) and not venue:
                    venue = y
                if y.upper() in ('WEEK %d' % (wk + 1),):
                    break
                j += 1
            if date:
                out.append({'league': 'NFL', 'team': 'San Francisco 49ers', 'subtype': section,
                            'week': wk, 'month': date[0], 'day': date[1], 'year': year,
                            'clock': time_, 'at_vs': atvs, 'opponent': opp, 'venue': venue,
                            'network': net, 'radio': radio, 'source': source_url})
        i += 1
    return out
