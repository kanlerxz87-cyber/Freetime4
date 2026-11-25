"""Extract game objects from NFL.com Next.js RSC flight payload."""
import re, json, html

def decode_rsc(text):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', text, flags=re.S)
    return ''.join(json.loads(c) for c in chunks)

def find_objects(s, needle='"homeTeamFullName"'):
    """Yield decoded JSON objects containing needle by bracket matching."""
    out = []
    for m in re.finditer(re.escape(needle), s):
        # walk backwards to the opening brace of this object
        depth = 0; i = m.start(); start = None
        while i > 0:
            i -= 1
            c = s[i]
            if c == '}': depth += 1
            elif c == '{':
                if depth == 0:
                    start = i; break
                depth -= 1
        if start is None: continue
        # walk forward to matching close
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
                        try:
                            out.append(json.loads(s[start:j+1]))
                        except Exception:
                            pass
                        break
            j += 1
    return out

def games_from_html(html_text):
    s = decode_rsc(html_text)
    objs = find_objects(s)
    seen = {}
    for o in objs:
        gid = o.get('gameId') or o.get('id')
        if not gid: continue
        if gid not in seen:
            seen[gid] = o
        else:
            # merge non-null fields
            for k, v in o.items():
                if seen[gid].get(k) in (None, '', []) and v not in (None, '', []):
                    seen[gid][k] = v
    return list(seen.values())
