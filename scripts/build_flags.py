#!/usr/bin/env python3
"""Consolidate the Flagged-for-Review registers from all sessions' sites plus this
session's flags into site/data/flags.json (single canonical register for the site)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

MINE = [
    {"id": "C-01", "area": "MLB labor", "item": "CBA expires Dec 1, 2026 — lockout expected",
     "detail": "The MLB CBA expires 11:59 PM ET Dec 1, 2026 and owners are expected to lock players out (hard-cap vs union fight). The officially released 2027 schedule (Opening Day Mar 25) could be delayed or games cancelled. The site keeps the official 2027 schedule and flags this risk.",
     "source": "https://sports.yahoo.com/mlb/article/mlb-labor-faq-with-a-lockout-on-the-horizon-heres-what-baseball-fans-need-to-know-175303012.html", "status": "open"},
    {"id": "C-02", "area": "Radio", "item": "KSFO 560 AM is dead — do not tune to 560",
     "detail": "Cumulus surrendered the 560 AM license Aug 5, 2026; the FCC cancelled it Aug 6, 2026. The KSFO brand continues on 810 kHz (former KGO). Older sources (including some team pages) still list 560.",
     "source": "https://en.wikipedia.org/wiki/KZAC", "status": "resolved-in-data"},
    {"id": "C-03", "area": "Radio", "item": "49ers flagship changed: KNBR 680/104.5 (not 560 KSFO)",
     "detail": "The 2026 49ers Radio Network lists KNBR 680/104.5 as flagship with 107.7 The Bone and 810 KSFO. Verified Nov 2026.",
     "source": "https://www.fubo.tv/news/nfl/san-francisco-49ers/what-channel-is-the-49ers-game-on/", "status": "resolved-in-data"},
    {"id": "C-04", "area": "Westwood One", "item": "RESOLVED: WW1 'conflicts' were pregame starts",
     "detail": "Two sessions flagged Dec 17, 2026 (SF@LAC) and Jan 3, 2027 (PHI@SF) kickoff-time conflicts between Westwood One and 49ers.com. Resolution: WW1's listed time is the radio broadcast window start (pregame), not kickoff. Kickoffs verified from the official schedule feed: Dec 17 kickoff 8:15 PM ET (5:15 PM PT); Jan 3 kickoff 8:20 PM ET (5:20 PM PT).",
     "source": "https://www.westwoodonesports.com/events/548568", "status": "resolved"},
    {"id": "C-05", "area": "Athletics", "item": "A's Bay Area radio in 2027 (Las Vegas era) unknown",
     "detail": "A's play in West Sacramento through 2026 (Bay Area carriage: 960 AM KNEW) and the official 2027 schedule lists Las Vegas Ballpark as their park with Las Vegas series in May-June. Their 2027 radio network is not announced; Bay Area AM/FM carriage is uncertain.",
     "source": "https://www.mlb.com/news/mlb-2027-schedule-released", "status": "open"},
    {"id": "C-06", "area": "NCAAF", "item": "Pro Bowl Games 2027 date conflicts (Feb 6/7/10)",
     "detail": "Trackers disagree on the 2027 Pro Bowl Games date/location; no official source found in this pass. Not counted as a radio-blocking event (no Westwood One carriage evidence). Shown nowhere as verified.",
     "source": "https://www.sportbusy.com/events/pro-bowl-2027/", "status": "open"},
    {"id": "C-07", "area": "MLB", "item": "2027 MLB postseason dates not announced",
     "detail": "Official API has no 2027 postseason. The site adds pattern-estimated slots (verified 2026 spacing from the final regular-season day) flagged ESTIMATE so late Sept/Oct 2027 is conservatively treated as busy.",
     "source": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027&gameType=F", "status": "estimated"},
    {"id": "C-08", "area": "Estimates", "item": "2028/2029 MLB home/away flips are speculative",
     "detail": "2028/2029 rows are the official 2027 schedule shifted 364/728 days. MLB's real future schedules may flip home/away on specific matchups or move special events. All such rows carry status ESTIMATE with blank source links, per the verification rules.",
     "source": "", "status": "estimated"},
    {"id": "C-09", "area": "NCAAF", "item": "Possible Stanford/Cal bowl games (Dec 2026) not included",
     "detail": "Bowl matchups are announced in early December 2026. If Stanford or Cal qualifies, one or two December days currently shown free would become busy. Not estimated — flagged instead.",
     "source": "https://calbears.com/sports/football/schedule", "status": "open"},
    {"id": "C-10", "area": "NCAAF", "item": "2028 SJSU-vs-Stanford date discrepancy in trackers",
     "detail": "Future-schedules trackers disagree (Sep 23 vs Nov 25, 2028) for San Jose State at Stanford. The site estimates the standard Saturday slate instead of choosing either unverified date.",
     "source": "https://fbschedules.com/ncaa/stanford/", "status": "open"},
    {"id": "C-11", "area": "Scope", "item": "Other Bay Area radio sports (Warriors, Sharks, Dons, etc.) are informational only",
     "detail": "Your free-time definition blocks MLB, NFL 49ers, Stanford/Cal and Westwood One national broadcasts. Other live radio sports (e.g., Warriors on 95.7) exist but are NOT counted in the free-time math. Ask if you want them added as blocking.",
     "source": "", "status": "needs-user-decision"},
    {"id": "C-12", "area": "Time zone", "item": "PST vs PDT handling",
     "detail": "You asked for PST. The site uses true Pacific time with PST/PDT switching so summer game times match the radio; winter dates are exactly PST. A fixed PST(UTC-8) view would misstate summer games by an hour.",
     "source": "", "status": "needs-user-decision"},
]


def main():
    rows = []
    for path, session in (
        ("docs/data.json", "arena/bbbb5122-freetime4 (docs/ site)"),
        ("calendar-site/data/flagged.json", "arena/7fca3e35-freetime4 (calendar-site)"),
        ("verified/data/flags.json", "arena/48068f3b-freetime4 (verified/ site)"),
    ):
        p = os.path.join(ROOT, path)
        if os.path.exists(p):
            d = json.load(open(p))
            flags = d.get("flags") if isinstance(d, dict) else d
            if isinstance(flags, dict):
                flags = list(flags.values())
            for f in flags or []:
                f2 = dict(f)
                f2["session"] = session
                f2["originFile"] = path
                rows.append(f2)
    for f in MINE:
        f["session"] = "arena/c04f5702-freetime4 (canonical site)"
        rows.append(f)
    out = os.path.join(ROOT, "site", "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "flags.json"), "w") as fh:
        json.dump({"count": len(rows), "flags": rows}, fh, separators=(",", ":"))
    print("flags consolidated:", len(rows))


if __name__ == "__main__":
    main()
