(function () {
  "use strict";
  var PT = "America/Los_Angeles";
  var DATA = null;

  function ptToday() {
    return new Intl.DateTimeFormat("en-CA", { timeZone: PT, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  }
  function addDays(iso, n) {
    var d = new Date(iso + "T12:00:00Z");
    d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0, 10);
  }
  function toMin(hm) {
    var p = hm.split(":");
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
  }
  function fmt(min) {
    var h = Math.floor(min / 60), m = min % 60;
    var ap = h < 12 ? "AM" : "PM";
    var hh = (h % 12) || 12;
    return hh + ":" + (m < 10 ? "0" : "") + m + " " + ap;
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function longDate(iso) {
    return new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", {
      weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone: "UTC"
    });
  }

  function render(iso) {
    var out = document.getElementById("out");
    document.getElementById("dayInput").value = iso;
    var day = DATA.days.find(function (d) { return d.date === iso; });
    if (!day) {
      out.innerHTML = '<div class="banner nodata">' + esc(iso) + " is outside the loaded calendar (" +
        DATA.range[0] + " to " + DATA.range[1] + "). No schedule is loaded for this date.</div>";
      return;
    }

    var evs = day.events.map(function (e) {
      var s = e.start ? toMin(e.start) : null;
      return { e: e, s: s, en: s === null ? null : Math.min(1440, s + e.dur) };
    });
    // minute-level occupancy: first event that covers each minute
    var occ = new Array(1440).fill(null);
    evs.forEach(function (x) {
      if (x.s === null) return;
      for (var m = x.s; m < x.en; m++) if (!occ[m]) occ[m] = x.e;
    });

    var st = day.mlb.status;
    var banner;
    if (st === "verified-none") {
      banner = '<div class="banner ok"><b>No MLB games on this date</b> (all 30 clubs; MLB Stats API feed).' +
        ' NFL and college games are shown only where loaded.</div>';
    } else if (st === "has-games") {
      banner = '<div class="banner busy"><b>' + day.mlb.count + ' MLB game' + (day.mlb.count === 1 ? "" : "s") +
        " on this date.</b> Free time is not available for hours without a loaded game, because the other clubs' start times are not loaded.</div>";
    } else {
      banner = '<div class="banner nodata"><b>No published MLB schedule for this date.</b> Free time cannot be verified.</div>';
    }

    var rows = "", freeMin = 0;
    for (var h = 0; h < 24; h++) {
      var busy = 0, titles = [];
      for (var m = h * 60; m < h * 60 + 60; m++) {
        if (occ[m]) { busy++; if (titles.indexOf(occ[m].title) < 0) titles.push(occ[m].title); }
      }
      var cls, txt;
      if (st === "unpublished") {
        cls = "nodata"; txt = "No published schedule";
      } else if (busy === 60) {
        cls = "busy"; txt = "Game on air: " + titles.join("; ");
      } else if (st === "has-games") {
        if (busy > 0) { cls = "part"; txt = "Game on air " + busy + " min: " + titles.join("; ") + ". Remaining time not available."; }
        else { cls = "na"; txt = "Free time not available"; }
      } else {
        if (busy > 0) { cls = "part"; txt = "Game on air " + busy + " min (" + titles.join("; ") + "). Free " + (60 - busy) + " min."; freeMin += 60 - busy; }
        else { cls = "free"; txt = "FREE 60 min"; freeMin += 60; }
      }
      rows += '<tr class="' + cls + '"><th>' + fmt(h * 60) + "</th><td>" + txt + "</td></tr>";
    }

    // contiguous free windows (verified-none days only)
    var windowsTxt = "";
    if (st === "verified-none") {
      var wins = [], start = null;
      for (var k = 0; k <= 1440; k++) {
        var free = k < 1440 && !occ[k];
        if (free && start === null) start = k;
        if (!free && start !== null) { wins.push([start, k]); start = null; }
      }
      windowsTxt = wins.length
        ? wins.map(function (w) { return fmt(w[0]) + " to " + (w[1] >= 1440 ? "midnight" : fmt(w[1])); }).join(", ")
        : "None (games fill the day)";
    }

    var summary;
    if (st === "verified-none") {
      summary = '<div class="stat"><b>' + Math.floor(freeMin / 60) + " h " + (freeMin % 60) + ' min</b> free (no loaded game)</div>' +
        '<div class="stat"><b>Free windows:</b> ' + windowsTxt + "</div>";
    } else if (st === "has-games") {
      summary = '<div class="stat"><b>Free time not available</b> on this date (MLB games on air)</div>';
    } else {
      summary = '<div class="stat"><b>Free time unknown</b> (no published schedule)</div>';
    }

    var list = "";
    if (!day.events.length) {
      list = '<p class="note">No loaded events on this date.</p>';
    } else {
      list = '<table class="ev"><thead><tr><th>Start (PT)</th><th>Group</th><th>Event</th><th>Duration</th><th>Notes</th><th>Source</th></tr></thead><tbody>' +
        day.events.map(function (e) {
          var when = e.start ? fmt(toMin(e.start)) : "Time TBD";
          return "<tr><td>" + when + "</td><td>" + esc(e.group) + (e.priority === "High" ? ' <span class="pill ok">High</span>' : "") +
            "</td><td>" + esc(e.title) + "<br><small>" + esc(e.subgroup) + "</small></td><td>" + (e.tbd ? "" : Math.floor(e.dur / 60) + ":" + String(e.dur % 60).padStart(2, "0")) +
            "</td><td><small>" + esc(e.note) + "</small></td><td><a href=\"" + esc(e.url) + "\">Source</a></td></tr>";
        }).join("") + "</tbody></table>";
    }

    out.innerHTML =
      '<h2>' + longDate(iso) + ' <small>(Pacific time)</small></h2>' + banner + summary +
      '<div class="grid"><div><h3>Hour by hour</h3><table class="hours"><tbody>' + rows + "</tbody></table></div>" +
      "<div><h3>Events on this day</h3>" + list + "</div></div>" +
      '<p class="note">Free = no loaded game for that minute. NFL and college lists are partial (see Flagged for Review). Durations: MLB 158 min, NFL 182 min (incl. halftime), NCAAF 206 min.</p>';
  }

  function go(iso) {
    var url = new URL(window.location.href);
    url.searchParams.set("date", iso);
    window.history.replaceState(null, "", url);
    render(iso);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var params = new URLSearchParams(window.location.search);
    var current = params.get("date") || ptToday();
    document.getElementById("prev").onclick = function () { go(addDays(current, -1)); current = addDays(current, -1); };
    document.getElementById("next").onclick = function () { go(addDays(current, 1)); current = addDays(current, 1); };
    document.getElementById("today").onclick = function () { current = ptToday(); go(current); };
    document.getElementById("dayInput").onchange = function (ev) { current = ev.target.value; go(current); };
    fetch("data/calendar.json")
      .then(function (r) { return r.json(); })
      .then(function (j) { DATA = j; render(current); })
      .catch(function () {
        document.getElementById("out").innerHTML = '<div class="banner nodata">Could not load the calendar data file.</div>';
      });
  });
})();
