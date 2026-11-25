/* FREE TIME VACATION - shared renderer (vanilla JS, no deps) */
const PT = "America/Los_Angeles";
const AWAKE = { start: "06:00", end: "23:30" };

function fmtMin(m) {
  const h = Math.floor(m / 60), mm = m % 60;
  return String(h).padStart(2, "0") + ":" + String(mm).padStart(2, "0");
}
function parseMin(t) {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}
function toMin(t) { return parseMin(t); }

function dateFromISO(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}
function isoFromDate(dt) {
  return dt.toISOString().slice(0, 10);
}
function prettyDate(iso) {
  const d = dateFromISO(iso);
  return d.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
}

async function getJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(path + ": HTTP " + r.status);
  return r.json();
}

/* -------- scoreboard day view -------- */
function busyBar(day) {
  const START = toMin(AWAKE.start), END = toMin(AWAKE.end), SPAN = END - START;
  let ticks = "";
  for (let h = 6; h <= 23; h += 3) {
    const pct = ((h * 60 - START) / SPAN) * 100;
    ticks += `<div class="tick" style="left:${pct}%"></div>`;
  }
  const blocks = (day.busy || []).map(e => {
    let s = Math.max(toMin(e.start), START), en = Math.min(toMin(e.end), END);
    if (en <= s) return "";
    const left = ((s - START) / SPAN) * 100, w = ((en - s) / SPAN) * 100;
    return `<div class="blk" title="${e.label} (${e.start}-${e.end} PT)" style="left:${left}%;width:${w}%"></div>`;
  }).join("");
  return `<div class="bar">${ticks}${blocks}</div>
    <div class="barlbl"><span>${AWAKE.start}</span><span>PT day bar (red = live sports on Bay Area radio)</span><span>${AWAKE.end}</span></div>`;
}

function tile(e) {
  const est = e.estimated || e.time_status === "tbd" || e.time_status === "tbd_estimated";
  return `<div class="tile">
    <div class="top"><span class="lg">${(e.league || "").toUpperCase()}</span><span class="tm">${e.start}&ndash;${e.end} PT</span></div>
    <div class="body">
      <div class="mu">${e.label}</div>
      <div class="meta">&#128251; ${e.radio || "radio TBA"} ${est ? '<span class="badge est">EST/TBD</span>' : '<span class="badge official">VERIFIED</span>'}</div>
      <div class="meta src">src: <a href="${e.source}" target="_blank" rel="noopener">${(e.source || "").replace(/^https?:\/\//, "").slice(0, 60)}</a></div>
    </div>
  </div>`;
}

function renderDay(day, idx, days) {
  const el = document.getElementById("day-view");
  if (!el) return;
  const freeRows = (day.free || []).map(f =>
    f.start === AWAKE.start && f.end === AWAKE.end
      ? `<li><b>ALL DAY FREE</b> (${f.start}&ndash;${f.end} PT, no live sports on any monitored station)</li>`
      : `<li>${f.start}&ndash;${f.end} PT free</li>`).join("");
  el.innerHTML = `
    <div class="daynav">
      <button id="d-prev">&larr; Yesterday</button>
      <span class="date">${prettyDate(day.date)}</span>
      <button id="d-next">Tomorrow &rarr;</button>
      <input type="date" id="d-pick" value="${day.date}">
      <span class="badge ${day.free_day ? "official" : "est"}" style="font-size:12px">${day.free_day ? "FREE DAY" : "GAMES TODAY"}</span>
    </div>
    ${busyBar(day)}
    <h2>Free-time windows (exact, PT)</h2>
    <ul>${freeRows || "<li>See tiles below</li>"}</ul>
    ${day.free_day ? `<div class="freeallday">&#9989; FREE ALL DAY &mdash; no live sports on Bay Area radio (Giants, A's, 49ers, Stanford, Cal, WW1 national, CFP)</div>` : ""}
    ${(day.busy || []).length ? `<h2>Games &amp; broadcasts (${day.busy.length})</h2><div class="tiles">${day.busy.map(tile).join("")}</div>` : ""}
  `;
  document.getElementById("d-prev").onclick = () => jump(idx - 1);
  document.getElementById("d-next").onclick = () => jump(idx + 1);
  document.getElementById("d-pick").onchange = (ev) => {
    const i = days.findIndex(d => d.date === ev.target.value);
    if (i >= 0) jump(i);
  };
}

function jump(i, days) {
  if (typeof days === "undefined") days = window.__days;
  i = Math.max(0, Math.min(window.__days.length - 1, i));
  window.__idx = i;
  renderDay(window.__days[i], i, window.__days);
  const target = document.getElementById("day-view");
  if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* -------- 30-day strip -------- */
function renderStrip(days) {
  const el = document.getElementById("strip");
  if (!el) return;
  const todayIso = new Date().toLocaleDateString("en-CA", { timeZone: PT });
  const i0 = days.findIndex(d => d.date >= todayIso);
  const start = i0 < 0 ? 0 : i0;
  const slice = days.slice(start, start + 30);
  el.innerHTML = slice.map(d => {
    const dd = d.date.slice(8), mo = d.date.slice(5, 7);
    return `<a class="cell ${d.free_day ? "f" : "b"}" href="index.html?date=${d.date}" title="${d.date} - ${d.free_day ? "FREE" : d.busy.length + " broadcast(es)"}">${mo}/${dd}</a>`;
  }).join("");
}

/* -------- generic table renderer -------- */
function renderTable(id, rows, cols) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<table class="data"><thead><tr>${cols.map(c => `<th>${c.h}</th>`).join("")}</tr></thead>
    <tbody>${rows.map(r => `<tr>${cols.map(c => `<td>${c.f(r)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function badgeEst(r) {
  const est = r.estimated || r.time_status === "tbd" || r.time_status === "tbd_estimated" || !r.time_pt;
  return est ? '<span class="badge est">EST/TBD</span>' : '<span class="badge official">VERIFIED</span>';
}
function srcLink(s) {
  return `<span class="src"><a href="${s}" target="_blank" rel="noopener">${(s || "").replace(/^https?:\/\//, "").slice(0, 52)}&hellip;</a></span>`;
}
function timeCell(r) {
  return r.time_pt ? r.time_pt + " PT" : (r.time_est_pt ? "~" + r.time_est_pt + " PT (est)" : "TBD");
}
function highCell(r) {
  return r.priority === "high" ? '<span class="badge high">HIGH</span>' : "";
}

async function boot() {
  const [free, mlb, nfl, ncaaf, vac, flags, radio, dur] = await Promise.all([
    getJSON("data/free_days.json"), getJSON("data/mlb_2027.json"), getJSON("data/nfl.json"),
    getJSON("data/ncaaf.json"), getJSON("data/vacation.json"), getJSON("data/flags.json"),
    getJSON("data/radio.json"), getJSON("data/durations.json"),
  ]);
  window.__days = free.days;
  const params = new URLSearchParams(location.search);
  let idx = free.days.findIndex(d => d.date === params.get("date"));
  if (idx < 0) {
    const todayIso = new Date().toLocaleDateString("en-CA", { timeZone: PT });
    idx = free.days.findIndex(d => d.date === todayIso);
    if (idx < 0) idx = 0;
  }
  window.__idx = idx;
  renderStrip(free.days);
  renderDay(free.days[idx], idx, free.days);

  /* executive summary */
  const es = document.getElementById("exec-summary");
  if (es) {
    const byYear = vac.years || {};
    const big = (y) => (byYear[y] || []).filter(v => v.days >= 7)
      .map(v => `<li><a href="index.html?date=${v.start}">${v.start} &rarr; ${v.end}</a> &mdash; ${v.days} days</li>`).join("") || "<li>none</li>";
    const today = free.days[idx];
    es.innerHTML = `
      <div class="cards">
        <div class="card ${today.free_day ? "free-hero" : "busy-hero"}">
          <h3>Today (${today.date})</h3>
          <div class="big">${today.free_day ? "FREE ALL DAY" : today.busy.length + " broadcast window(s) today"}</div>
        </div>
        <div class="card">
          <h3>Longest 2027 stretch</h3>
          <div class="big">${(byYear["2027"] || []).reduce((a, v) => v.days > (a?.days || 0) ? v : a, null)?.days || 0} days</div>
          <div class="src">Feb 1&ndash;13, before the Super Bowl</div>
        </div>
        <div class="card">
          <h3>Data status</h3>
          <div class="big" style="color:var(--good)">2026 NFL + 2027 MLB: VERIFIED</div>
          <div class="src">2028/29: pattern estimates &mdash; see <a href="flagged.html">Flagged for Review</a></div>
        </div>
      </div>
      <h2>Vacation windows (all-free day runs, 7+ days)</h2>
      <div class="yearcols">
        <div class="card"><h3>2027</h3><ul>${big("2027")}</ul></div>
        <div class="card"><h3>2028</h3><ul>${big("2028")}</ul></div>
        <div class="card"><h3>2029</h3><ul>${big("2029")}</ul></div>
      </div>
      <p class="legend">A "free day" = zero live-sports windows 06:00&ndash;23:30 PT on monitored stations (KNBR 680/104.5, KTCT 1050, KSAN 107.7, KNEW 960, KGO 810). Full list: <a href="vacation.html">Vacation Windows</a>.</p>`;
  }

  /* league pages */
  renderTable("tbl-mlb-g", mlb.giants.games, [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Time (PT)", f: timeCell },
    { h: "Matchup", f: r => r.matchup },
    { h: "Type", f: r => r.type },
    { h: "Radio", f: r => r.radio || "TBA" },
    { h: "Status", f: badgeEst },
    { h: "Pri", f: highCell },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  renderTable("tbl-mlb-a", mlb.athletics.games, [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Time (PT)", f: timeCell },
    { h: "Matchup", f: r => r.matchup },
    { h: "Type", f: r => r.type },
    { h: "Radio", f: r => r.radio || "TBA" },
    { h: "Status", f: badgeEst },
    { h: "Pri", f: highCell },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  const daymap = document.getElementById("tbl-mlb-daymap");
  if (daymap) {
    const zero = new Set(mlb.zero_game_dates_2027);
    renderTable("tbl-mlb-daymap", mlb.daymap, [
      { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
      { h: "Total MLB games", f: r => r.games },
      { h: "Bay Area club playing?", f: r => (mlb.giants.games.some(g => g.date === r.date) || mlb.athletics.games.some(g => g.date === r.date)) ? "Giants and/or A's" : "no SF club game" },
    ]);
  }
  renderTable("tbl-nfl-sf", nfl.games.filter(g => g.sf), [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Kickoff (PT)", f: timeCell },
    { h: "Matchup", f: r => r.matchup },
    { h: "Wk", f: r => r.week },
    { h: "WW1 on-air (PT)", f: r => r.ww1_broadcast_pt || "&ndash;" },
    { h: "Radio", f: r => r.radio },
    { h: "Status", f: badgeEst },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  renderTable("tbl-nfl-all", nfl.games, [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Kickoff (PT)", f: timeCell },
    { h: "Matchup", f: r => r.matchup },
    { h: "Wk", f: r => r.week },
    { h: "Status", f: badgeEst },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  renderTable("tbl-nfl-po", nfl.playoffs, [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Round", f: r => r.matchup },
    { h: "Radio", f: r => r.radio },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  renderTable("tbl-ncaaf", ncaaf.verified_rows.filter(r => !r.date.endsWith("TBD")), [
    { h: "Date", f: r => `<a href="index.html?date=${r.date}">${r.date}</a>` },
    { h: "Time (PT)", f: timeCell },
    { h: "Event", f: r => r.matchup },
    { h: "Radio", f: r => r.radio },
    { h: "Status", f: badgeEst },
    { h: "Pri", f: highCell },
    { h: "Source", f: r => srcLink(r.source) },
  ]);
  const vc = document.getElementById("tbl-vac");
  if (vc) {
    const rows = [];
    for (const y of ["2027", "2028", "2029"]) for (const v of (vac.years[y] || [])) rows.push({ y, ...v });
    renderTable("tbl-vac", rows, [
      { h: "Year", f: r => r.y },
      { h: "Start", f: r => `<a href="index.html?date=${r.start}">${r.start}</a>` },
      { h: "End", f: r => `<a href="index.html?date=${r.end}">${r.end}</a>` },
      { h: "Days", f: r => r.days },
      { h: "Fits 1 wk", f: r => r.max_1wk ? "&#9989;" : "&ndash;" },
      { h: "Fits 2 wk", f: r => r.max_2wk ? "&#9989;" : "&ndash;" },
      { h: "Fits 3 wk", f: r => r.max_3wk ? "&#9989;" : "&ndash;" },
    ]);
  }
  const fl = document.getElementById("tbl-flags");
  if (fl) {
    renderTable("tbl-flags", flags.flags.map((t, i) => ({ i: i + 1, t })), [
      { h: "#", f: r => r.i },
      { h: "Flag for review", f: r => r.t },
    ]);
  }
  const rd = document.getElementById("tbl-radio");
  if (rd) {
    renderTable("tbl-radio", radio.bay_area_stations, [
      { h: "Station", f: r => `<b>${r.station}</b>` },
      { h: "Carries", f: r => (r.carries || []).join("; ") },
      { h: "Overflow/notes", f: r => r.conflict_overflow || "&ndash;" },
      { h: "Source", f: r => srcLink(r.source) },
    ]);
    document.getElementById("radio-note").innerHTML = radio.note || "";
  }
  const dz = document.getElementById("tbl-dur");
  if (dz) {
    const rows = [
      { l: "MLB regular season", v: dur.mlb_regular_min + " min (2:45)" },
      { l: "MLB postseason / All-Star", v: dur.mlb_postseason_min + " min (3:00)" },
      { l: "NFL (incl. halftime)", v: dur.nfl_min + " min (3:15)" },
      { l: "NCAAF (incl. halftime)", v: dur.ncaaf_min + " min (3:25)" },
    ];
    renderTable("tbl-dur", rows, [
      { h: "League", f: r => r.l },
      { h: "Busy-window length used", f: r => r.v },
    ]);
    document.getElementById("dur-note").innerHTML = "Basis: " + dur.basis.mlb + " " + dur.basis.nfl + " " + dur.basis.ncaaf;
  }
}

boot().catch(err => {
  document.body.insertAdjacentHTML("afterbegin",
    `<div class="note">Failed to load data files: ${err.message}. If you opened this page from the filesystem, serve it over HTTP instead.</div>`);
});
