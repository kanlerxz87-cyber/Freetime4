// Renders each page from the JSON in docs/data. Every row cites a source ID; source IDs resolve to official URLs in sources.json.
(function () {
  "use strict";
  var base = "";
  var S = {};            // source id -> source object
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "class") n.className = attrs[k]; else if (k === "text") n.textContent = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function get(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error(url + " " + r.status); return r.json(); }); }
  function tag(status) {
    var s = (status || "").toUpperCase(), cls = "";
    if (s.indexOf("VERIFIED") === 0) cls = "verified";
    else if (s.indexOf("CONFLICT") === 0) cls = "conflict";
    else if (s.indexOf("UNVERIFIED") === 0 || s.indexOf("REVIEW") === 0 || s.indexOf("INCOMPLETE") === 0 || s.indexOf("NOT ") === 0 || s.indexOf("IRREGULAR") === 0 || s.indexOf("SECONDARY") === 0) cls = "unverified";
    else if (s.indexOf("ESTIMATE") === 0) cls = "estimate";
    else cls = "bad";
    return el("span", { class: "tag " + cls, text: status || "" });
  }
  function srcLink(id) {
    var s = S[id];
    if (!s) return el("span", { class: "muted small", text: id + " (missing)" });
    return el("a", { href: s.url, target: "_blank", rel: "noopener", text: s.title.length > 60 ? s.title.slice(0, 58) + "…" : s.title });
  }
  function srcCell(ids) {
    var td = el("td", { class: "small" });
    (ids || []).forEach(function (id, i) { if (i) td.appendChild(document.createTextNode(" · ")); td.appendChild(srcLink(id)); });
    if (!ids || !ids.length) td.appendChild(el("span", { class: "muted", text: "no official source" }));
    return td;
  }
  function table(headers, rows) {
    var t = el("table"), thead = el("tr");
    headers.forEach(function (h) { thead.appendChild(el("th", { text: h })); });
    t.appendChild(el("thead", null, [thead]));
    var tb = el("tbody");
    rows.forEach(function (r) { if (r instanceof Node) { tb.appendChild(r); return; } var tr = el("tr"); r.forEach(function (c) { tr.appendChild(c instanceof Node ? c : el("td", { text: c == null ? "" : String(c) })); }); tb.appendChild(tr); });
    t.appendChild(tb);
    return el("div", { class: "panel" }, [t]);
  }
  function td(x) { return el("td", { text: x == null ? "" : String(x) }); }
  function h2(t) { return el("h2", { text: t }); }
  function lead(t) { return el("p", { class: "lead", text: t }); }
  function note(t) { return el("div", { class: "flagnote", text: t }); }
  function fmtDate(s) {
    if (!s) return "";
    var d = new Date(s + "T12:00:00Z");
    return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
  }
  function timeCell(t) { return td(t || ""); }
  function loadSources() { return get(base + "data/sources.json").then(function (j) { j.sources.forEach(function (s) { S[s.id] = s; }); return j; }); }

  // ---------- pages ----------
  var pages = {};

  pages.mlb = function (root) {
    root.appendChild(lead("MLB (all 30 active clubs). Giants and Athletics are high priority. Official data: MLB Stats API. Game times are not yet in the workspace; only game counts per date are verified."));
    return Promise.all([get(base + "data/raw/mlb-teams.json"), get(base + "data/raw/mlb-seasons-2027.json"),
      get(base + "data/raw/mlb-seasons-2026.json"), get(base + "data/raw/mlb-2027-giants-daily.json"),
      get(base + "data/raw/mlb-2027-athletics-daily.json"), get(base + "data/raw/mlb-2027-regular-season-daily.json"),
      get(base + "data/raw/mlb-2027-spring-training-daily.json")]).then(function (a) {
      var teams = a[0].teams, s27 = a[1].seasons[0], s26 = a[2].seasons[0];
      var sum = function (j) { return j.dates.reduce(function (x, d) { return x + d.totalGames; }, 0); };
      root.appendChild(h2("Priority clubs (2027 spring training + regular season)"));
      var rows = [];
      [["San Francisco Giants (ID 137)", a[3], "S-MLB-GIANTS-2027", "High priority"], ["Athletics (ID 133, API location: Sacramento)", a[4], "S-MLB-ATH-2027", "High priority"]].forEach(function (x) {
        var dates = x[1].dates, first = dates[0].date, last = dates[dates.length - 1].date;
        var tr = el("tr", null, [td(x[0]), td(x[3]), td(sum(x[1])), td(x[1].totalGames), td(dates.length + " game dates, " + first + " to " + last), srcCell([x[2], "S-MLB-SEASON-2027"])]);
        rows.push(tr);
      });
      root.appendChild(table(["Club", "Priority", "Games (sum of dates)", "API total", "Date span (2027)", "Source"], rows.map(function (r) { return r; })));
      root.appendChild(h2("League totals, 2027"));
      root.appendChild(table(["Set", "Games", "Source", "Note"], [
        el("tr", null, [td("Spring training (2027-02-19 to 2027-03-23)"), td(sum(a[6])), srcCell(["S-MLB-S-2027"]), td("Counts are per date from the API")]),
        el("tr", null, [td("Regular season (2027-03-24 to 2027-09-26)"), td(sum(a[5])), srcCell(["S-MLB-R-2027"]), td("Only zero-game days: 07-12, 07-13, 07-14 (All-Star Game 07-13 is a separate game type)")]),
        el("tr", null, [td("All-Star Game (2027-07-13)"), td(1), srcCell(["S-MLB-ASG-2027"]), td("Game type A")])
      ]));
      root.appendChild(h2("Season calendar (MLB Stats API)"));
      root.appendChild(table(["Season", "Spring", "Regular season", "All-Star", "Postseason", "Source"], [
        el("tr", null, [td("2026"), td(s26.springStartDate + " to " + s26.springEndDate), td(s26.regularSeasonStartDate + " to " + s26.regularSeasonEndDate), td(s26.allStarDate), td(s26.postSeasonStartDate + " to " + s26.postSeasonEndDate), srcCell(["S-MLB-SEASON-2026"])]),
        el("tr", null, [td("2027"), td(s27.springStartDate + " to " + s27.springEndDate), td(s27.regularSeasonStartDate + " to " + s27.regularSeasonEndDate), td(s27.allStarDate), td(s27.postSeasonStartDate + " to " + s27.postSeasonEndDate), srcCell(["S-MLB-SEASON-2027"])]),
        el("tr", null, [td("2028"), td("NOT PUBLISHED"), td("NOT PUBLISHED"), td(""), td(""), srcCell(["S-MLB-SEASON-2028"])]),
        el("tr", null, [td("2029"), td("NOT PUBLISHED"), td("NOT PUBLISHED"), td(""), td(""), srcCell(["S-MLB-SEASON-2029"])])
      ]));
      root.appendChild(note("F-18: the 2027 API lists the first day of the second half as 2027-07-16, while league daily counts show games on 07-15. F-19: 2028 and 2029 are not published."));
      root.appendChild(h2("All 30 active clubs"));
      root.appendChild(table(["Club", "Abbrev.", "Location (API)", "Venue", "League / Division", "Priority", "Source"], teams.map(function (t) {
        var pr = /Giants|Athletics/.test(t.name) ? "High" : "";
        return el("tr", null, [td(t.name), td(t.abbreviation), td(t.locationName), td(t.venue && t.venue.name), td(t.league.name + " / " + t.division.name), td(pr), srcCell(["S-MLB-TEAMS"])]);
      })));
    });
  };

  pages.nfl = function (root) {
    root.appendChild(lead("NFL: 49ers (high priority), Westwood One national radio broadcasts, and the Super Bowl. All times Pacific unless noted; Westwood One times are Eastern as printed."));
    return Promise.all([get(base + "data/nfl-49ers-2026.json"), get(base + "data/nfl-national-radio.json"), get(base + "data/nfl-calendar.json")]).then(function (a) {
      root.appendChild(h2("49ers 2026 (high priority)"));
      root.appendChild(table(["Date", "Type", "Wk", "Opponent", "Home/Away", "Kickoff (PT)", "Result", "TV", "Flag", "Source"], a[0].games.map(function (g) {
        return el("tr", null, [td(g.date ? fmtDate(g.date) : "TBD"), td(g.type), td(g.week || ""), td(g.opponent), td(g.home_away || ""), timeCell(g.time_pt), td(g.result), td(g.tv || ""),
          el("td", { class: "small" }, [g.flag ? tag("CONFLICT") : null, g.flag ? document.createTextNode(" " + g.flag) : null]), srcCell(["S-49ERS"])]);
      })));
      root.appendChild(h2("Westwood One national NFL radio (events 548xxx)"));
      root.appendChild(note("Blank time or date means not confirmed on the listing and is left blank on purpose. Times are Eastern as printed. NFL.com times (Thanksgiving week) are shown for comparison."));
      root.appendChild(table(["Date", "Time (ET)", "Game", "Slot", "Event", "NFL.com (where shown)", "Flag", "Source"], a[1].events.map(function (e) {
        return el("tr", null, [td(e.date ? fmtDate(e.date) : "UNCONFIRMED"), td(e.time_et), td(e.matchup), td(e.slot || ""), td(e.event_id),
          td(e.nfl_com ? e.nfl_com.time + " (" + e.nfl_com.network + ")" : ""),
          el("td", { class: "small" }, [e.flag ? tag("REVIEW") : null, e.flag ? document.createTextNode(" " + e.flag) : null]),
          srcCell(e.nfl_com ? ["S-WWO-NFL", "S-NFL-2026-REG14"] : ["S-WWO-NFL"])]);
      })));
      root.appendChild(h2("Super Bowl and calendar items"));
      root.appendChild(table(["Item", "Value", "Status", "Note", "Source"], a[2].items.map(function (it) {
        return el("tr", null, [td(it.item), td(it.value), el("td", null, [tag(it.status)]), td(it.note || ""), srcCell(it.source ? [it.source] : [])]);
      })));
    });
  };

  pages.ncaaf = function (root) {
    root.appendChild(lead("Stanford and California football (high priority). Results and schedules from each school's athletics site. College game duration has not been verified, so no free time is computed for these games."));
    return get(base + "data/college-football-2026.json").then(function (j) {
      [["Stanford Cardinal", j.stanford, "S-STANFORD", "gostanford.com"], ["California Golden Bears", j.cal, "S-CAL", "calbears.com"]].forEach(function (t) {
        root.appendChild(h2(t[0] + " 2026 (high priority)"));
        root.appendChild(note("Radio: " + t[1].radio_note));
        root.appendChild(table(["Date", "Opponent", "Home/Away", "Kickoff (PT)", "Result", "Flag", "Source"], t[1].games.map(function (g) {
          return el("tr", null, [td(fmtDate(g.date)), td(g.opponent), td(g.home_away), timeCell(g.time_pt), td(g.result), el("td", { class: "small" }, [g.flag ? tag("CONFLICT") : null, g.flag ? document.createTextNode(" " + g.flag) : null]), srcCell([t[2]])]);
        })));
      });
    });
  };

  pages.radio = function (root) {
    root.appendChild(lead("AM/FM radio for Bay Area sports. Coverage at 94122 (Outer Sunset) has not been checked for any station. Use the FCC link to verify before relying on reception."));
    return get(base + "data/radio.json").then(function (j) {
      root.appendChild(table(["Program", "Station", "Status", "Note", "Source"], j.networks.map(function (n) {
        return el("tr", null, [td(n.program), td(n.station), el("td", null, [tag(n.status)]), td(n.note || ""), srcCell([n.source].concat(n.secondary_source ? [n.secondary_source] : []).filter(Boolean))]);
      })));
      root.appendChild(h2("Coverage check"));
      root.appendChild(note(j.coverage_check.status + ". " + j.coverage_check.how_to_verify));
      root.appendChild(el("p", { class: "small" }, [document.createTextNode("FCC station search: "), el("a", { href: "https://www.fcc.gov/media/radio", target: "_blank", rel: "noopener", text: "fcc.gov/media/radio" })]));
    });
  };

  pages.vacation = function (root) {
    root.appendChild(lead("Free windows where no in-scope game is on air. A window is shown only if the official data supports it. Estimates and unpublished periods are labeled and carry no dates."));
    return get(base + "data/vacation-windows.json").then(function (j) {
      root.appendChild(note(j.scope_conflict));
      root.appendChild(note("Scope: " + j.scope_note));
      root.appendChild(table(["Window", "Scope", "Result", "Status", "Source"], j.windows.map(function (w) {
        return el("tr", null, [td(w.period), td(w.scope), td(w.result), el("td", null, [tag(w.status)]), srcCell(w.sources)]);
      })));
    });
  };

  pages.flagged = function (root) {
    root.appendChild(lead("Items that conflict, are unverified, or were not retrieved. Flags do not block the site; each one links to the sources that show the conflict."));
    return get(base + "data/flags.json").then(function (j) {
      root.appendChild(table(["ID", "Category", "Item", "Status", "Sources"], j.flags.map(function (f) {
        return el("tr", null, [td(f.id), td(f.category), td(f.item), el("td", null, [tag(f.status)]), srcCell(f.sources)]);
      })));
    });
  };

  pages.sources = function (root) {
    root.appendChild(lead("Every source used. Type: official = league, team, school, venue, or the MLB Stats API. Secondary sources are used only where no official value exists, and are flagged."));
    return get(base + "data/sources.json").then(function (j) {
      root.appendChild(table(["ID", "Type", "Source", "Used for", "Link"], j.sources.map(function (s) {
        return el("tr", null, [td(s.id), el("td", null, [tag(s.type === "official" ? "VERIFIED" : "SECONDARY")]), td(s.title), td(s.used_for || ""), el("td", { class: "small" }, [el("a", { href: s.url, target: "_blank", rel: "noopener", text: s.url })])]);
      })));
    });
  };

  // ---------- scoreboard ----------
  function toMin(hhmm) { var p = hhmm.split(":"); return parseInt(p[0], 10) * 60 + parseInt(p[1], 10); }
  function fmtHM(min) { var h = Math.floor(min / 60), m = min % 60; return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0"); }
  pages.scoreboard = function (root) {
    root.appendChild(lead("Day view in Pacific time. Game blocks run from kickoff for the verified duration. Free time = the gaps between game blocks. Durations: NFL 183 min (secondary average, see Flagged). College durations are not verified, so no free time is shown on those days."));
    var params = new URLSearchParams(location.search);
    var start = params.get("date") || "2026-11-25";
    var controls = el("div", { class: "daybar" });
    var prev = el("button", { text: "◀ Previous day" }), next = el("button", { text: "Next day ▶" });
    var input = el("input", { type: "date", value: start });
    controls.appendChild(prev); controls.appendChild(input); controls.appendChild(next);
    root.appendChild(controls);
    var body = el("div"); root.appendChild(body);
    function shift(d, n) { var x = new Date(d + "T12:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); }
    function go(d) { history.replaceState(null, "", "?date=" + d); input.value = d; render(d); }
    prev.onclick = function () { go(shift(input.value, -1)); };
    next.onclick = function () { go(shift(input.value, 1)); };
    input.onchange = function () { go(input.value); };
    var mlbCache = null;
    function mlb() {
      if (mlbCache) return Promise.resolve(mlbCache);
      return Promise.all([get(base + "data/raw/mlb-2027-giants-daily.json"), get(base + "data/raw/mlb-2027-athletics-daily.json"), get(base + "data/raw/mlb-2027-regular-season-daily.json"), get(base + "data/raw/mlb-2027-spring-training-daily.json")]).then(function (a) {
        var map = function (j) { var m = {}; j.dates.forEach(function (d) { m[d.date] = d.totalGames; }); return m; };
        mlbCache = { giants: map(a[0]), ath: map(a[1]), league: Object.assign({}, map(a[2]), map(a[3])) };
        return mlbCache;
      });
    }
    function render(d) {
      body.innerHTML = "";
      Promise.all([get(base + "data/scoreboard.json"), mlb(), loadSources()]).then(function (a) {
        var sb = a[0], m = a[1];
        var events = sb.events.filter(function (e) { return e.date === d; });
        var hd = el("h2", { text: fmtDate(d) + " (Pacific)" });
        body.appendChild(hd);
        var mlbLine = el("p", { class: "small" });
        var gcount = m.giants[d] || 0, acount = m.ath[d] || 0, lcount = m.league[d] || 0;
        var mtxt; if (d < "2027-02-19") mtxt = "MLB: no games. The 2026 season ended 2026-10-28 and 2027 spring training starts 2027-02-19."; else if (d > "2027-09-26") mtxt = "MLB: no 2027 data for this date (the 2027 postseason runs to 2027-10-31, and 2028 is not published)."; else mtxt = "MLB (spring + regular season, verified daily counts): " + lcount + " league games. Giants: " + gcount + ". Athletics: " + acount + ". MLB game times are not yet verified, so no MLB blocks are shown."; mlbLine.appendChild(document.createTextNode(mtxt));
        body.appendChild(mlbLine);
        if (!events.length) { body.appendChild(note("No verified NFL or college game for this date in the workspace data.")); }
        // timeline 00:00-24:00 PT
        var bar = el("div", { class: "timeline" });
        var blocks = [], problems = [];
        events.forEach(function (e) {
          if (!e.start_pt) { problems.push("Start time TBA: " + e.title); return; }
          if (e.duration_min == null) { problems.push("Duration not verified: " + e.title + " (" + e.start_pt + " PT)"); return; }
          blocks.push({ s: toMin(e.start_pt), e: toMin(e.start_pt) + e.duration_min, t: e.title });
        });
        blocks.sort(function (x, y) { return x.s - y.s; });
        var canFree = problems.length === 0;
        var merged = [];
        blocks.forEach(function (b) { if (merged.length && b.s < merged[merged.length - 1].e) merged[merged.length - 1].e = Math.max(merged[merged.length - 1].e, b.e); else merged.push({ s: b.s, e: b.e }); });
        var pct = function (x) { return (x / 1440 * 100) + "%"; };
        var frees = [];
        if (canFree) {
          var cur = 0; merged.forEach(function (b) { if (b.s > cur) frees.push({ s: cur, e: b.s }); cur = Math.max(cur, b.e); }); if (cur < 1440) frees.push({ s: cur, e: 1440 });
        }
        if (canFree) frees.forEach(function (f) { var x = el("div", { class: "blk free", text: "FREE " + fmtHM(f.s) + "–" + fmtHM(f.e) }); x.style.left = pct(f.s); x.style.width = pct(f.e - f.s); bar.appendChild(x); });
        blocks.forEach(function (b) { var x = el("div", { class: "blk game", text: fmtHM(b.s) + " " + b.t }); x.style.left = pct(b.s); x.style.width = pct(Math.min(1440, b.e) - b.s); bar.appendChild(x); });
        if (events.length) body.appendChild(bar);
        if (events.length) body.appendChild(el("div", { class: "axis" }, ["00:00", "06:00", "12:00", "18:00", "24:00"].map(function (t) { return el("span", { text: t }); })));
        if (events.length && !canFree) body.appendChild(note("Free time is not computed for this day because: " + problems.join("; ") + "."));
        if (events.length) body.appendChild(table(["Start (PT)", "Game", "League", "Duration", "Source", "Flag"], events.map(function (e) {
          var dur = e.duration_min == null ? "not verified" : e.duration_min + " min";
          return el("tr", null, [td(e.start_pt ? e.start_pt + (e.start_as_printed ? " (printed " + e.start_as_printed + ")" : "") : "TBA"), td(e.title), td(e.league), td(dur), el("td", { class: "small" }, [srcLink(e.source === "49ers.com" ? "S-49ERS" : e.source.indexOf("Westwood") === 0 ? "S-WWO-NFL" : e.source.indexOf("Stanford") === 0 ? "S-STANFORD" : "S-CAL")]), td(e.flag || "")]);
        })));
        if (canFree) body.appendChild(el("p", { class: "small" }, [document.createTextNode("Free blocks are estimates: they assume the game lasts exactly the verified average, and that no other in-scope game falls in the gap.")]));
      }).catch(function (err) { body.appendChild(note("Could not load data: " + err.message)); });
    }
    render(start);
    return Promise.resolve();
  };

  // ---------- landing ----------
  pages.index = function (root) {
    root.appendChild(lead("A free-time planner for an Outer Sunset (94122) listener: when is there no live Bay Area radio sports coverage, and when is there a free week for a vacation? Official schedules are used where they exist. Anything unverified is left blank and flagged."));
    var cards = [
      ["Scoreboard (day view)", "scoreboard.html", "Pacific-time day view with previous and next buttons, game blocks, and free time."],
      ["MLB (30 clubs)", "mlb.html", "Giants and Athletics (high priority), season calendars, and league game counts."],
      ["NFL and Westwood One", "nfl.html", "49ers (high priority), national radio games, and the Super Bowl."],
      ["College (Stanford, Cal)", "ncaaf.html", "Stanford and California football (high priority)."],
      ["Radio stations", "radio.html", "KNBR, KSAN, KSFN, and station conflicts. Coverage not yet checked."],
      ["Vacation windows", "vacation.html", "Week, 2-week, and 3-week windows for 2026-2029, with what is verified and what is not."],
      ["Flagged for Review", "flagged.html", "Conflicts and unverified items, each linked to its sources."],
      ["Sources", "sources.html", "Every official and secondary source used, with links."]
    ];
    var g = el("div", { class: "cards" });
    cards.forEach(function (c) { g.appendChild(el("div", { class: "card" }, [el("a", { href: c[1], text: c[0] }), el("p", { text: c[2] })])); });
    root.appendChild(g);
    root.appendChild(note("Headline: no verified week-long window exists in 2027 when all 30 MLB clubs and the other in-scope sports are considered. The only verified MLB-free stretch within the season is Jul 12-15 for the Giants and Athletics (4 days). See the Vacation page."));
    root.appendChild(note("Timekeeping: all times are Pacific. Westwood One times (Eastern) are converted by subtracting three hours."));
    return loadSources();
  };

  // ---------- boot ----------
  var page = document.body.getAttribute("data-page");
  var main = document.getElementById("main");
  var fn = pages[page];
  if (fn) {
    Promise.resolve(loadSources()).then(function () { return fn(main); }).catch(function (err) {
      main.appendChild(el("div", { class: "flagnote", text: "Error loading data: " + err.message }));
    });
  }
})();
