#!/usr/bin/env python3
"""Checks for docs/: internal links resolve, every table body row carries an
official-source link (except rows that are intentionally text-only), and the
data files parse. External URLs are listed, not fetched (sandbox egress is limited)."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
problems = []
external = set()

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.rows, self.in_tbody, self.row_has_link, self.row_text = [], [], False, False, []
        self.cur_row_links = 0
        self.depth_row = 0
        self.bad_rows = 0
        self.total_rows = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self.depth_row:
                self.cur_row_links += 1
        if tag == "tbody": self.in_tbody = True
        if tag == "tr" and self.in_tbody:
            self.depth_row = 1; self.cur_row_links = 0
    def handle_endtag(self, tag):
        if tag == "tbody": self.in_tbody = False
        if tag == "tr" and self.depth_row:
            self.total_rows += 1
            if self.cur_row_links == 0: self.bad_rows += 1
            self.depth_row = 0

for page in sorted(DOCS.glob("*.html")):
    p = P(); p.feed(page.read_text(encoding="utf-8"))
    for href in p.links:
        if href.startswith("http"):
            external.add(href)
        elif href.startswith("#"):
            continue
        else:
            target = (DOCS / href.split("#")[0]).resolve()
            if not target.exists():
                problems.append(f"{page.name}: broken internal link -> {href}")
    if p.total_rows:
        print(f"{page.name}: {p.total_rows} table rows, {p.bad_rows} without a link")
        if p.bad_rows:
            problems.append(f"{page.name}: {p.bad_rows} table rows lack a source link")

for f in sorted((ROOT / "data").glob("*.json")):
    try:
        json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        problems.append(f"{f.name}: invalid JSON ({e})")

for asset in ["assets/site.css", "assets/calendar.js", "data/calendar.json"]:
    if not (DOCS / asset).exists():
        problems.append(f"missing {asset}")

print(f"external source links on site: {len(external)}")
if problems:
    print("PROBLEMS:"); [print(" -", x) for x in problems]
    sys.exit(1)
print("OK: no broken internal links; every table row has a source link")
