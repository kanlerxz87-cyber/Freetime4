/* common helpers — Free Time Vacation */
const DAY = 86400000;
const TODAY_STR = "2026-11-25"; // data build horizon "today"

function fmtTime(mins) {
  const h = Math.floor(mins / 60), m = mins % 60;
  return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
}
function toMin(t) {
  if (!t) return null;
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}
function isoAdd(iso, n) {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}
function isoDow(iso) {
  return ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][new Date(iso + "T12:00:00Z").getUTCDay()];
}
function isoPretty(iso) {
  const d = new Date(iso + "T12:00:00Z");
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const CACHE = {};
async function loadYear(y) {
  if (!CACHE[y]) {
    const r = await fetch(`data/games-${y}.json`);
    if (!r.ok) return { games: [] };
    CACHE[y] = await r.json();
  }
  return CACHE[y];
}
function nav(active) {
  const items = [
    ["index.html", "Executive Summary"],
    ["calendar.html", "Calendar / Scoreboard"],
    ["vacation.html", "Vacation Windows"],
    ["mlb.html", "MLB"],
    ["nfl.html", "NFL"],
    ["westwood-one.html", "Westwood One"],
    ["ncaaf.html", "Stanford & Cal"],
    ["radio.html", "Radio"],
    ["sources.html", "Sources & Method"],
    ["flagged.html", "Flagged for Review"],
  ];
  document.write('<nav class="site">' + items.map(([href, label]) =>
    `<a href="${href}" class="${href === active ? "active" : ""}">${label}</a>`).join("") + "</nav>");
}
function verBadge(e) {
  if (e.verified) return '<span class="badge ver" title="Read on an official source this session">✓ verified</span>';
  return '<span class="badge est" title="Estimate or cross-check — see source link and flagged page">est / unverified</span>';
}
function timeCell(e) {
  if (!e.time) return '<span class="muted">TBD</span>';
  return esc(e.time) + (e.timeEstimated ? ' <span class="badge est">time est</span>' : "");
}

/* free-block computation for one day (minutes from midnight, PST) */
function dayEvents(games, iso, scenario) {
  return games.filter(e => {
    const end = e.dateEnd || e.date;
    if (iso < e.date || iso > end) return false;
    if (e.blocking === false) return true; // shown, but not counted busy
    if (scenario === "no-st" && (e.category === "spring" || e.category === "exhibition")) return false;
    if (scenario === "sf-radio" && !e.sfRadio) return false;
    return true;
  });
}
function freeBlocks(events) {
  const busy = [];
  const warns = [];
  for (const e of events) {
    if (e.blocking === false) { warns.push(e); continue; }
    const s = toMin(e.time ?? "12:00");
    let en = s + (e.durMin ?? 120);
    if (en > 1440) en = 1440;
    busy.push([s, en]);
  }
  busy.sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const b of busy) {
    if (merged.length && b[0] <= merged[merged.length - 1][1]) {
      merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b[1]);
    } else merged.push([...b]);
  }
  const blocks = [];
  let cur = 0;
  for (const [s, en] of merged) {
    if (s > cur) blocks.push({ type: "free", from: cur, to: s });
    blocks.push({ type: "busy", from: s, to: en });
    cur = en;
  }
  if (cur < 1440) blocks.push({ type: "free", from: cur, to: 1440 });
  return { blocks, merged, warns };
}
