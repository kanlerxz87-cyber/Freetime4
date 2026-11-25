#!/usr/bin/env python3
"""Build and validate the dependency-free static Gameplan site."""
from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
REQUIRED_PAGES = ("mlb.html", "nfl.html", "college.html", "radio.html", "sources.html")


def fail(message: str) -> None:
    raise SystemExit(f"build check failed: {message}")


def validate_url(value: str, where: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"expected an https source URL at {where}: {value!r}")


def validate_date(value: object, where: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        fail(f"expected ISO date or null at {where}")
    try:
        date.fromisoformat(value)
    except ValueError:
        fail(f"invalid ISO date at {where}: {value!r}")
    if len(value) != 10:
        fail(f"expected YYYY-MM-DD at {where}: {value!r}")


def validate_time(value: object, where: str) -> None:
    if value is not None and (not isinstance(value, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value)):
        fail(f"expected HH:MM or null at {where}: {value!r}")


def main() -> None:
    index = ROOT / "index.html"
    source_dir = ROOT / "site"
    data_file = source_dir / "data" / "schedules.json"
    if not index.is_file() or not data_file.is_file():
        fail("index.html or site/data/schedules.json is missing")

    data = json.loads(data_file.read_text(encoding="utf-8"))
    if not data.get("asOf"):
        fail("data.asOf must be set to the latest completed source-audit date")
    validate_date(data["asOf"], "asOf")
    for key in ("fortyNiners", "collegeFootball", "westwoodOne", "radioStations", "reviewItems", "mlbEvents", "leagueDates", "legacyOpponentGrids"):
        if not isinstance(data.get(key), list):
            fail(f"data field {key!r} must be an array")
    for group in ("fortyNiners", "collegeFootball", "westwoodOne", "mlbEvents", "leagueDates", "legacyOpponentGrids"):
        for index_num, event in enumerate(data.get(group, [])):
            validate_date(event.get("date"), f"{group}[{index_num}].date")
            validate_time(event.get("timePT"), f"{group}[{index_num}].timePT")
            if event.get("sourceUrl"):
                validate_url(event["sourceUrl"], f"{group}[{index_num}].sourceUrl")
            for url_num, url in enumerate(event.get("supportingSourceUrls", [])):
                validate_url(url, f"{group}[{index_num}].supportingSourceUrls[{url_num}]")
    for key, value in data.get("sources", {}).items():
        validate_url(value, f"sources.{key}")
    for index_num, review in enumerate(data.get("reviewItems", [])):
        for url_num, url in enumerate(review.get("sourceUrls", [])):
            validate_url(url, f"reviewItems[{index_num}].sourceUrls[{url_num}]")
    for index_num, station in enumerate(data.get("radioStations", [])):
        for url_num, url in enumerate(station.get("sourceUrls", [])):
            validate_url(url, f"radioStations[{index_num}].sourceUrls[{url_num}]")

    for page in REQUIRED_PAGES:
        if not (source_dir / "pages" / page).is_file():
            fail(f"category page is missing: site/pages/{page}")
    for asset in ("assets/app.js", "assets/category.js", "assets/styles.css", "assets/category.css"):
        if not (source_dir / asset).is_file():
            fail(f"required asset is missing: site/{asset}")

    # Guard the cleanup target before replacing the generated build output.
    if BUILD.resolve() == ROOT.resolve() or BUILD.resolve().parent != ROOT.resolve():
        fail("refusing to clean an unexpected build path")
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    shutil.copy2(index, BUILD / "index.html")
    shutil.copytree(source_dir, BUILD / "site")
    (BUILD / ".nojekyll").touch()
    print(f"Built {BUILD.relative_to(ROOT)} ({len(data.get('fortyNiners', []))} 49ers rows, "
          f"{len(data.get('collegeFootball', []))} college rows, "
          f"{len(data.get('reviewItems', []))} review flags).")


if __name__ == "__main__":
    main()
