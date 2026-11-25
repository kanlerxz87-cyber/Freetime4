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
