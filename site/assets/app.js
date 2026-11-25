/* Freetime4 canonical site — shared JS.
   Data lives in data/site/ (root-level). All times shown are Pacific (PST/PDT as applicable). */
const DATA = "../data/site/";
const STATUS_LABEL = {
  "VERIFIED": "Verified (official source)",
  "VERIFIED-SLOT": "Verified window (teams TBD)",
  "PARTIAL-VERIFIED": "Partly verified (matchup announced; time estimated)",
  "ESTIMATE": "Estimate — not an official schedule",
  "ESTIMATED-TIME": "Official date; time estimated"
};
const STATUS_ORDER = { "VERIFIED": 0, "VERIFIED-SLOT": 1, "PARTIAL-VERIFIED": 2, "ESTIMATED-TIME": 3, "ESTIMATE": 4 };

async function fetchJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(url + ": " + r.status);
  return r.json();
}
const yearCache = {};
async function gamesFor(year) {
  if (!yearCache[year]) yearCache[year] = fetchJSON(DATA + "games_" + year + ".json").then(d => d.games);
  return yearCache[year];
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function chip(text, cls) { return `<span class="chip ${esc(cls || text)}">${esc(text)}</span>`; }
function statusChip(row) {
  return `<span class="chip ${row.status}">${row.status}</span>`;
}
function ptNote() {
  return "All times Pacific (PST/PDT as applicable).";
}

/* ---------- generic table ---------- */
function renderTable(el, rows, cols) {
  const head = cols.map(c => `<th>${c.h}</th>`).join("");
  const body = rows.map(r => "<tr>" + cols.map(c => `<td>${c.f(r)}</td>`).join("") + "</tr>").join("");
  el.innerHTML = `<div class="tablewrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
function countNote(el, rows, label) {
  const n = rows.length;
  const est = rows.filter(r => r.status === "ESTIMATE").length;
  const ver = rows.filter(r => r.status === "VERIFIED" || r.status === "VERIFIED-SLOT").length;
  el.textContent = `${n.toLocaleString()} ${label || "rows"} — ${ver.toLocaleString()} verified with source links, ${est.toLocaleString()} flagged ESTIMATE (official schedule not released).`;
}

/* ---------- sport pages ---------- */
function bindFilters(yearSel, apply) {
  yearSel.addEventListener("change", apply);
}
function rowLink(r) {
  return r.sourceUrl ? `<a href="${esc(r.sourceUrl)}" target="_blank" rel="noopener">source</a>` : `<span class="small">none (estimate)</span>`;
}
function matchupCell(r) {
  const hi = r.priority === "high";
  const name = esc(r.matchup || (r.away + " at " + r.home));
  return (hi ? '<b>' + name + '</b>' : name) + (r.venue ? `<div class="small">${esc(r.venue)}</div>` : "");
}
function radioCell(r) {
  return r.radio ? esc(r.radio) : '<span class="small">—</span>';
}

async function renderGamesPage(cfg) {
  const yearSel = document.querySelector("#year");
  const statusSel = document.querySelector("#status");
  const teamSel = document.querySelector("#team");
  const typeSel = document.querySelector("#type");
  const table = document.querySelector("#table");
  const note = document.querySelector("#note");
  if (yearSel && cfg.years && !yearSel.options.length) {
    cfg.years.forEach(y => yearSel.insertAdjacentHTML("beforeend", `<option value="${y}">${y}</option>`));
  }
  const apply = async () => {
    const y = yearSel ? +yearSel.value : cfg.years[0];
    let rows = await gamesFor(y);
    if (cfg.filter) rows = rows.filter(cfg.filter);
    if (statusSel && statusSel.value) rows = rows.filter(r => r.status === statusSel.value);
    if (teamSel && teamSel.value) rows = rows.filter(r => r.away === teamSel.value || r.home === teamSel.value);
    if (typeSel && typeSel.value) rows = rows.filter(r => r.type === typeSel.value);
    rows.sort((a, b) => (a.datePT + (a.startPT || "")).localeCompare(b.datePT + (b.startPT || "")));
    countNote(note, rows);
    renderTable(table, rows, [
      { h: "Date (PT)", f: r => esc(r.datePT) },
      { h: "Start (PT)", f: r => esc(r.startPT || "TBD") },
      { h: "Type", f: r => esc(r.type || "") + (r.week ? ` <span class="small">wk ${r.week}</span>` : "") },
      { h: "Matchup", f: matchupCell },
      { h: "Radio (Bay Area AM/FM)", f: radioCell },
      { h: "Priority", f: r => chip(r.priority) },
      { h: "Status", f: statusChip },
      { h: "Source", f: rowLink },
    ]);
  };
  if (yearSel) yearSel.addEventListener("change", apply);
  if (statusSel) statusSel.addEventListener("change", apply);
  if (teamSel) teamSel.addEventListener("change", apply);
  if (typeSel) typeSel.addEventListener("change", apply);
  apply().catch(e => { table.innerHTML = '<div class="warn">Failed to load data: ' + esc(e.message) + "</div>"; });
}

/* ---------- scoreboard ---------- */
async function loadDay(dateStr) {
  const y = +dateStr.slice(0, 4);
  const [games, days] = await Promise.all([
    gamesFor(y),
    fetchJSON(DATA + "days_" + y + ".json")
  ]);
  const day = days.days.find(d => d.date === dateStr);
  const todays = games.filter(g => g.datePT === dateStr);
  return { day, games: todays, variant: days.variant };
}

function fmtMin(min) {
  const h = Math.floor(min / 60), m = min % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}
function dayBar(day) {
  if (!day) return "";
  const len = day.dayLen;
  const ticks = [];
  for (let h = 0; h <= 24; h += 3) ticks.push(`<div class="tick" style="left:${(h * 60 / len) * 100}%"></div>`);
  const busy = day.busySpans.map(([s, e]) => `<div class="busy" style="left:${(s / len) * 100}%;width:${((e - s) / len) * 100}%"></div>`).join("");
  return `<div class="daybar">${ticks.join("")}${busy}</div>
  <div class="daybar-labels"><span>midnight</span><span>6 AM</span><span>noon</span><span>6 PM</span><span>midnight</span></div>`;
}

async function renderScoreboard() {
  const sel = document.querySelector("#date");
  const view = document.querySelector("#view");
  const variantSel = document.querySelector("#variant");
  const url = new URL(location.href);
  const today = new Date().toLocaleDateString("en-CA", { timeZone: "America/Los_Angeles" });
  if (!sel.value) sel.value = url.searchParams.get("d") || today;

  async function refresh() {
    const dateStr = sel.value;
    const variant = variantSel.value;
    const y = +dateStr.slice(0, 4);
    const [games, days] = await Promise.all([gamesFor(y), fetchJSON(DATA + `days_${y}${variant === "nospring" ? "-nospring" : ""}.json`)]);
    const day = days.days.find(d => d.date === dateStr);
    const todays = games.filter(g => g.datePT === dateStr);
    const d = new Date(dateStr + "T12:00:00");
    const pretty = d.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
    let head, banner;
    if (day && day.free) {
      banner = `<div class="free-banner">✓ FREE DAY — no blocking games on the radio</div>`;
    } else {
      banner = `<div class="busy-banner">● GAMES ON THE RADIO — ${day ? day.busySpans.length : 0} busy window(s), ${day ? Math.round(day.busyMin / 60) : 0} h of the day blocked (estimated)</div>`;
    }
    head = `<div class="d">${pretty}</div>
      <div class="sub">Pacific time (PST/PDT) · ${variant === "nospring" ? "spring training NOT counted as blocking" : "spring training counted as blocking (MLB preseason)"}</div>
      ${banner}${day ? dayBar(day) : ""}`;
    const rows = todays.map(g => `<tr>
      <td>${esc(g.startPT || "TBD")}</td>
      <td>${esc(g.sport)}</td>
      <td>${esc(g.category)}</td>
      <td>${matchupCell(g)}</td>
      <td>${radioCell(g)}</td>
      <td>${chip(g.priority)}</td>
      <td>${statusChip(g)}</td>
      <td>${rowLink(g)}</td>
    </tr>`).join("");
    const estimateWarn = todays.some(g => g.status === "ESTIMATE")
      ? '<div class="warn">This day includes ESTIMATED games (official schedule not yet released). Estimates are pattern-based, clearly flagged, and may change when official schedules publish.</div>'
      : "";
    view.innerHTML = `<div class="scoreday">${head}</div>${estimateWarn}
      <div class="tablewrap"><table><thead><tr><th>Start (PT)</th><th>Sport</th><th>Category</th><th>Matchup</th><th>Radio</th><th>Priority</th><th>Status</th><th>Source</th></tr></thead>
      <tbody>${rows || '<tr><td colspan="8">No games in dataset for this day.</td></tr>'}</tbody></table></div>`;
    history.replaceState(null, "", `?d=${dateStr}${variant === "nospring" ? "&v=nospring" : ""}`);
  }
  document.querySelector("#prev").onclick = () => shiftDay(-1);
  document.querySelector("#next").onclick = () => shiftDay(1);
  document.querySelector("#today").onclick = () => { sel.value = today; refresh(); };
  sel.addEventListener("change", refresh);
  variantSel.addEventListener("change", refresh);
  function shiftDay(n) {
    const d = new Date(sel.value + "T12:00:00");
    d.setDate(d.getDate() + n);
    sel.value = d.toLocaleDateString("en-CA", { timeZone: "UTC" });
    refresh();
  }
  const v = url.searchParams.get("v");
  if (v === "nospring") variantSel.value = "nospring";
  refresh().catch(e => { view.innerHTML = '<div class="warn">Failed to load: ' + esc(e.message) + "</div>"; });
}

/* ---------- vacation windows ---------- */
async function renderWindows() {
  const view = document.querySelector("#view");
  const w = await fetchJSON(DATA + "windows.json");
  const cards = [];
  for (const variant of ["default", "no-spring"]) {
    const wins = w.windows[variant].windows;
    cards.push(`<h2>${variant === "default" ? "Strict rule: spring training counts as MLB preseason (blocking)" : "Lenient rule: spring training excluded (see methodology)"}</h2>`);
    for (const y of ["2027", "2028", "2029"]) {
      const list = (wins[y] || []).sort((a, b) => b.days - a.days);
      const estimated = y !== "2027";
      cards.push(`<h3>${y} ${estimated ? chip("ESTIMATE", "ESTIMATE") : chip("VERIFIED", "VERIFIED")}</h3>`);
      cards.push(`<div class="card ${estimated ? "estimated win-card" : "win-card"}">
        <table><thead><tr><th>From</th><th>To</th><th>Days</th><th>Notes</th></tr></thead><tbody>
        ${list.slice(0, 10).map(x => `<tr><td>${x.weekdayStart} ${x.start}</td><td>${x.weekdayEnd} ${x.end}</td><td class="num"><b>${x.days}</b></td>
          <td class="small">${x.days >= 7 ? "Multi-week vacation possible" : x.days >= 4 ? "Long-weekend-plus" : "Short break"}</td></tr>`).join("") || "<tr><td colspan=4>None ≥ 2 days</td></tr>"}
        </tbody></table></div>`);
    }
  }
  cards.push(`<div class="warn">2028 and 2029 windows are computed from ESTIMATED schedules (flagged). 2027 windows use the official MLB 2027 schedule plus pattern-estimated NFL/NCAAF seasons. Free = no MLB, no NFL 49ers, no Stanford/Cal, no Westwood One national broadcast on air, per the free-time definition.</div>`);
  view.innerHTML = cards.join("");
}

/* ---------- index KPIs ---------- */
async function renderIndex() {
  const w = await fetchJSON(DATA + "windows.json");
  const meta = await fetchJSON(DATA + "meta.json");
  const set = (id, v) => { document.querySelector("#" + id).textContent = v; };
  set("k27", w.freeDaysPerYear.default[2027]);
  set("k28", w.freeDaysPerYear.default[2028]);
  set("k29", w.freeDaysPerYear.default[2029]);
  set("kmeta", Object.values(meta.counts).reduce((a, b) => a + b, 0).toLocaleString() + " rows");
}
