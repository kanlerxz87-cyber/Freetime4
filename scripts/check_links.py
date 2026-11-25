#!/usr/bin/env python3
"""Static link + asset check for the published site. Runs offline."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sorted(f for f in os.listdir(ROOT) if f.endswith('.html'))
errs, warn = [], []
for p in pages:
    h = open(os.path.join(ROOT, p), encoding='utf-8').read()
    for m in re.finditer(r'(?:href|src)="([^"#]+)"', h):
        u = m.group(1)
        if u.startswith(('http://', 'https://', 'mailto:', 'data:')): continue
        if '${' in u or u.startswith('?'): continue   # template placeholder filled at runtime
        target = u.split('?')[0]
        if not target: continue
        if not os.path.exists(os.path.join(ROOT, target)):
            errs.append(f'{p}: missing {target}')
    # every page must load app.js and the stylesheet
    if 'assets/app.js' not in h: errs.append(f'{p}: no app.js')
    if 'assets/style.css' not in h: errs.append(f'{p}: no style.css')
    if 'id="hdr"' not in h: warn.append(f'{p}: no header mount')
# required pages exist
for need in ('index.html','calendar.html','vacation.html','mlb.html','nfl.html','ncaaf.html',
             'radio.html','sources.html','flagged.html','data/site.json','.nojekyll'):
    if not os.path.exists(os.path.join(ROOT, need)): errs.append(f'missing required file {need}')
# data integrity
import json
d = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
for k in ('games','days','months','seasons','config','unreleased','stretches_audible'):
    if k not in d: errs.append(f'site.json missing key {k}')
print(f'pages {len(pages)}  games {len(d["games"])}')
for w in warn: print('WARN', w)
for e in errs: print('ERROR', e)
print('LINKS:', 'PASS' if not errs else f'FAIL ({len(errs)})')
sys.exit(0 if not errs else 1)
