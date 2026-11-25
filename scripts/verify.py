#!/usr/bin/env python3
"""Data-quality gate. Fails the build if anything is invented or unsourced."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
G = d['games']; errs = []; warn = []
OFFICIAL = ('statsapi.mlb.com', 'nfl.com', '49ers.com', 'gostanford.com', 'calbears.com',
            'westwoodonesports.com', 'mlb.com')
for g in G:
    if not g.get('source'): errs.append(f"missing source: {g.get('label')}")
    elif not any(h in g['source'] for h in OFFICIAL) and g['verified'] != 'cross-checked':
        errs.append(f"non-official source on a verified row: {g['source']}")
    if not g.get('start_iso') or not g.get('end_iso'):
        errs.append(f"missing times: {g.get('label')}")
    if g['verified'] == 'estimated' and not g.get('note'):
        errs.append(f"estimated row without a note: {g.get('label')}")
    if g['verified'] in ('verified', 'cross-checked') and (not g.get('away') and not g.get('label')):
        errs.append(f"verified row with no teams: {g.get('label')}")
    if g['verified'] == 'estimated' and g.get('away'):
        errs.append(f"estimate invented matchup names: {g.get('label')}")
# counts sanity
c = collections.Counter(g['league'] for g in G)
exp = {'MLB': (7780, 7800), 'NFL': (1800, 1900), 'NCAAF': (290, 300), 'WWO': (300, 320)}
for k, (lo, hi) in exp.items():
    if not (lo <= c[k] <= hi): warn.append(f"{k} count {c[k]} outside expected {lo}-{hi}")
# days
bad = [k for k, v in d['days'].items() if v['free_audible_min'] > 1439 or v['free_strict_min'] > 1439]
if bad: errs.append(f"impossible free minutes on {len(bad)} days")
# sources present in every league
for lg in ('MLB', 'NFL', 'NCAAF', 'WWO'):
    n = len({g['source'] for g in G if g['league'] == lg})
    if not n: errs.append(f"no sources for {lg}")

print(f"rows {len(G)}  counts {dict(c)}")
print(f"verified {sum(1 for g in G if g['verified']=='verified')}  "
      f"cross-checked {sum(1 for g in G if g['verified']=='cross-checked')}  "
      f"estimated {sum(1 for g in G if g['verified']=='estimated')}")
for w in warn: print("WARN:", w)
for e in errs[:25]: print("ERROR:", e)
print("RESULT:", "PASS" if not errs else f"FAIL ({len(errs)} errors)")
sys.exit(0 if not errs else 1)
