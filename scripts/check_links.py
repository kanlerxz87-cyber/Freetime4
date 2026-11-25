#!/usr/bin/env python3
"""check_links.py — internal link + data-integrity check for the published site."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "calendar.html", "vacation.html", "mlb.html", "nfl.html",
         "westwood-one.html", "ncaaf.html", "radio.html", "sources.html",
         "flagged.html", "executive-summary.html", "free-time.html", "flagged-review.html"]

errors, warnings = [], []

def exists(rel):
    rel = rel.split("#")[0].split("?")[0]
    if not rel:
        return True
    return os.path.exists(os.path.join(ROOT, rel))

for page in PAGES:
    p = os.path.join(ROOT, page)
    if not os.path.exists(p):
        errors.append(f"missing page: {page}")
        continue
    html = open(p, encoding="utf-8").read()
    for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
        url = m.group(1)
        if url.startswith(("http://", "https://", "mailto:", "data:", "#")):
            continue
        if "${" in url:  # JS template literal, resolved at runtime
            continue
        if not exists(url):
            errors.append(f"{page}: broken internal link -> {url}")

for y in [2026, 2027, 2028, 2029, 2030]:
    p = os.path.join(ROOT, "data", f"games-{y}.json")
    if not os.path.exists(p):
        errors.append(f"missing data file games-{y}.json")
        continue
    d = json.load(open(p))
    for i, e in enumerate(d["games"]):
        for field in ("id", "date", "label", "durMin", "verified", "source"):
            if field not in e or e[field] in (None, ""):
                errors.append(f"games-{y}.json row {i}: missing field {field}")
        if e.get("source", "").startswith("http") is False:
            errors.append(f"games-{y}.json row {i}: source is not a URL: {e.get('source')}")
        if e.get("verified") and "microsoft" in json.dumps(e).lower():
            pass

s = json.load(open(os.path.join(ROOT, "data", "summary.json")))
for scope, sc in s["scenarios"].items():
    for y, info in sc["years"].items():
        for r in info["runs"]:
            if r["end"] < r["start"]:
                errors.append(f"summary {scope} {y}: bad run {r}")

flags = json.load(open(os.path.join(ROOT, "data", "flags.json")))
flag_page = open(os.path.join(ROOT, "flagged.html"), encoding="utf-8").read()
for f in flags["flags"]:
    if not f.get("source", "").startswith("https://"):
        errors.append(f"flag {f['id']}: source not https")

print(f"pages checked: {len(PAGES)}")
for w in warnings:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
print("RESULT:", "FAIL" if errors else "PASS", f"({len(errors)} errors)")
sys.exit(1 if errors else 0)
