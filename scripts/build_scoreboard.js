// Builds docs/data/scoreboard.json from the verified source JSON files.
// Times: Westwood One lists ET; converted to PT by subtracting 3 hours (both zones observe DST together).
// Durations: NFL = 183 min (secondary average, see averages-and-rules.json). College = null (unverified).
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const read = f => JSON.parse(fs.readFileSync(path.join(root, "docs/data", f), "utf8"));
const toMin = t => { // "7:30 PM" -> 1170
  const m = (t || "").match(/^(\d{1,2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let h = parseInt(m[1], 10) % 12; if (m[3] === "PM") h += 12;
  return h * 60 + parseInt(m[2], 10);
};
const fmt = total => { total = ((total % 1440) + 1440) % 1440; return String(Math.floor(total / 60)).padStart(2, "0") + ":" + String(total % 60).padStart(2, "0"); };
const etToPT = t => { const m = toMin(t); return m === null ? null : fmt(m - 180); }; // Eastern -> Pacific
const ptToPT = t => { const m = toMin(t); return m === null ? null : fmt(m); };    // already Pacific
const NFL_MIN = 183, CFB_MIN = null;
const events = [];
const nat = read("nfl-national-radio.json");
for (const e of nat.events) {
  events.push({ league: "NFL", source: "Westwood One (" + e.event_id + ")", source_url: "https://www.westwoodonesports.com/nfl-schedule/",
    date: e.date, start_pt: etToPT(e.time_et), start_as_printed: e.time_et ? e.time_et + " ET" : "", title: e.matchup,
    duration_min: NFL_MIN, flag: e.flag || "" });
}
const sf = read("nfl-49ers-2026.json");
for (const g of sf.games) {
  if (!g.date) continue;
  events.push({ league: "NFL", source: "49ers.com", source_url: "https://www.49ers.com/schedule/", date: g.date,
    start_pt: ptToPT(g.time_pt), start_as_printed: g.time_pt ? g.time_pt + " PT" : "",
    title: "49ers " + (g.home_away === "Away" ? "at " : "vs ") + g.opponent + (g.type === "Preseason" ? " (preseason)" : ""),
    duration_min: g.type === "Preseason" ? null : NFL_MIN, flag: g.flag || "" });
}
const cfb = read("college-football-2026.json");
for (const [k, team] of [["stanford", "Stanford"], ["cal", "Cal"]]) {
  for (const g of cfb[k].games) {
    events.push({ league: "NCAAF", source: team + " athletics", source_url: k === "stanford" ? "https://gostanford.com/sports/football/schedule" : "https://calbears.com/sports/football/schedule",
      date: g.date, start_pt: ptToPT(g.time_pt), start_as_printed: g.time_pt ? g.time_pt + " PT" : "",
      title: team + " " + (g.home_away === "Away" ? "at " : "vs ") + g.opponent, duration_min: CFB_MIN, flag: g.flag || "" });
  }
}
events.sort((a, b) => (a.date + (a.start_pt || "99:99")).localeCompare(b.date + (b.start_pt || "99:99")));
const out = { generated_from: ["nfl-national-radio.json", "nfl-49ers-2026.json", "college-football-2026.json", "averages-and-rules.json"],
  timezone_note: "All start times shown in Pacific. Eastern times (Westwood One) minus 3 hours; Pacific times as printed by the team or school.",
  events };
fs.writeFileSync(path.join(root, "docs/data/scoreboard.json"), JSON.stringify(out, null, 2) + "\n");
console.log("events:", events.length, "timed:", events.filter(e => e.start_pt).length);
