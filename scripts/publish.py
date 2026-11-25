#!/usr/bin/env python3
"""Copy the built site to the repo root so GitHub Pages (main / root) serves it."""
import json, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'site')
data = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
os.makedirs(os.path.join(SRC, 'data'), exist_ok=True)
# the page fetches data/site.json relative to the published root
shutil.copy(os.path.join(ROOT, 'data', 'site.json'), os.path.join(SRC, 'data', 'site.json'))
for f in os.listdir(SRC):
    if f.endswith('.html'):
        shutil.copy(os.path.join(SRC, f), os.path.join(ROOT, f))
shutil.copytree(os.path.join(SRC, 'assets'), os.path.join(ROOT, 'assets'), dirs_exist_ok=True)
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
shutil.copy(os.path.join(SRC, 'data', 'site.json'), os.path.join(ROOT, 'data', 'site.json'))
open(os.path.join(ROOT, '.nojekyll'), 'w').close()
print('published:', sorted(f for f in os.listdir(ROOT) if f.endswith('.html')))
print('data size', os.path.getsize(os.path.join(ROOT, 'data', 'site.json')))
