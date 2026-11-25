// Shared site logic. Every value comes from data.json, which carries a source URL per row.
(function () {
  var page = document.body.getAttribute('data-page');
  var TODAY = '2026-11-25';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
    });
  }
  function badge(text, cls) { return '<span class="badge ' + cls + '">' + esc(text) + '</span>'; }
  function verBadge(v) {
    v = String(v || '');
    if (/CONFLICT/i.test(v)) return badge('CONFLICT', 'b-bad');
    if (/^Verified/i.test(v)) return badge('Verified', 'b-ver');
    if (/TBA|TBD/i.test(v)) return badge('Partly TBA', 'b-part');
    return badge('Partly verified', 'b-part');
  }
  function fmtTime(t) {
    if (!t || t === 'TBA' || t === 'TBD') return esc(t || 'TBA');
    var p = t.split(':'), h = +p[0], m = p[1];
    var ap = h >= 12 ? 'PM' : 'AM', hh = h % 12; if (hh === 0) hh = 12;
    return hh + ':' + m + ' ' + ap;
  }
  function minutes(t) { var p = t.split(':'); return (+p[0]) * 60 + (+p[1]); }
  function hm(mins) {
    var h = Math.floor(mins / 60), m = mins % 60;
    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
  }
  function addDays(iso, n) {
    var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0, 10);
  }
  function longDate(iso) {
    var d = new Date(iso + 'T12:00:00Z');
    return d.toLocaleDateString('en-US', {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC'});
  }
  function srcLink(url, label) {
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(label || 'Source') + '</a>';
  }

  fetch('data.json').then(function (r) { return r.json(); }).then(function (D) {
    if (page === 'index') renderIndex(D);
    if (page === 'games') renderGames(D);
    if (page === 'scoreboard') renderScoreboard(D);
    if (page === 'vacation') renderVacation(D);
    if (page === 'flagged') renderFlagged(D);
    if (page === 'sources') renderSources(D);
  }).catch(function (e) {
    var m = document.getElementById('app');
    if (m) m.innerHTML = '<div class="alert">Could not load data.json: ' + esc(e.message) + '</div>';
  });

  // ---------- INDEX ----------
  function renderIndex(D) {
    var nextUp = D.games.filter(function (g) { return g.status === 'Upcoming' && g.time_pt !== 'TBA' && g.time_pt !== 'TBD'; })
      .sort(function (a, b) { return (a.date + a.time_pt) < (b.date + b.time_pt) ? -1 : 1; }).slice(0, 4);
    var w = D.windows;
    var el = document.getElementById('kpis');
    el.innerHTML =
      '<div class="card"><div class="k">Best verified free window</div><div class="v">Feb 15 - Mar 23, 2027</div><div class="legend">' + badge('PARTLY VERIFIED', 'b-part') + ' 37 days, no MLB, NFL, Stanford or Cal games (spring training excluded)</div></div>' +
      '<div class="card"><div class="k">2028 window</div><div class="v">Feb 14 - Mar 22, 2028</div><div class="legend">' + badge('ESTIMATE', 'b-est') + ' not a released schedule</div></div>' +
      '<div class="card"><div class="k">2029 window</div><div class="v">About Feb 12 - Late Mar</div><div class="legend">' + badge('ESTIMATE', 'b-est') + ' no official source found</div></div>' +
      '<div class="card"><div class="k">Flagged for review</div><div class="v">' + D.flags.length + ' items</div><div class="legend">' + badge('Open', 'b-bad') + ' see Flagged for Review</div></div>';
    document.getElementById('upnext').innerHTML = nextUp.length ? nextUp.map(function (g) {
      return '<tr><td class="nowrap">' + esc(g.date) + '</td><td class="nowrap">' + fmtTime(g.time_pt) + '</td><td>' + esc(g.category) + '</td><td>' + esc(g.matchup) + '</td><td>' + srcLink(g.source_url) + '</td></tr>';
    }).join('') : '<tr><td colspan="5">No upcoming timed games in data.</td></tr>';
  }

  // ---------- GAMES ----------
  function renderGames(D) {
    var cats = {};
    D.games.forEach(function (g) { cats[g.category] = 1; });
    var sel = document.getElementById('cat');
    sel.innerHTML = '<option value="">All categories</option>' + Object.keys(cats).sort().map(function (c) {
      return '<option value="' + esc(c) + '">' + esc(c) + '</option>';
    }).join('');
    var rows = D.games.slice().sort(function (a, b) { return (a.date + a.time_pt) < (b.date + b.time_pt) ? -1 : 1; });
    function draw() {
      var q = document.getElementById('q').value.toLowerCase(), c = sel.value, st = document.getElementById('st').value;
      var out = rows.filter(function (g) {
        if (c && g.category !== c) return false;
        if (st && g.status !== st) return false;
        if (q && (g.matchup + ' ' + g.venue + ' ' + g.category + ' ' + g.broadcast).toLowerCase().indexOf(q) < 0) return false;
        return true;
      });
      document.getElementById('count').textContent = out.length + ' rows';
      document.getElementById('tbody').innerHTML = out.map(function (g) {
        var hi = /High/.test(g.priority) ? ' class="hi"' : '';
        return '<tr' + hi + '>' +
          '<td class="nowrap">' + esc(g.date) + '</td>' +
          '<td class="nowrap">' + fmtTime(g.time_pt) + '</td>' +
          '<td>' + esc(g.category) + '</td>' +
          '<td>' + esc(g.matchup) + '</td>' +
          '<td>' + esc(g.venue) + '</td>' +
          '<td>' + esc(g.broadcast) + '</td>' +
          '<td>' + (/High/.test(g.priority) ? badge('HIGH', 'b-hi') : badge('Standard', 'b-std')) + '</td>' +
          '<td>' + esc(g.status) + (g.result ? '<br><span class="legend">' + esc(g.result) + '</span>' : '') + '</td>' +
          '<td>' + verBadge(g.verified) + '<div class="legend">' + esc(g.verified) + '</div></td>' +
          '<td>' + srcLink(g.source_url, g.source_name) + '</td>' +
          '</tr>';
      }).join('');
    }
    ['q', 'cat', 'st'].forEach(function (id) { document.getElementById(id).addEventListener('input', draw); document.getElementById(id).addEventListener('change', draw); });
    draw();
  }

  // ---------- SCOREBOARD ----------
  function renderScoreboard(D) {
    var params = new URLSearchParams(location.search);
    var date = params.get('date') || TODAY;
    var app = document.getElementById('app');
    function go(d) { location.search = '?date=' + d; }
    document.getElementById('prev').onclick = function () { go(addDays(date, -1)); };
    document.getElementById('next').onclick = function () { go(addDays(date, 1)); };
    document.getElementById('today').onclick = function () { go(TODAY); };
    document.getElementById('pick').value = date;
    document.getElementById('pick').onchange = function () { go(this.value); };

    var dayGames = D.games.filter(function (g) { return g.date === date; });
    var timed = dayGames.filter(function (g) { return /^\d\d:\d\d$/.test(g.time_pt); });
    var tba = dayGames.filter(function (g) { return !/^\d\d:\d\d$/.test(g.time_pt); });
    var blocks = timed.map(function (g) {
      var s = minutes(g.time_pt), dur = D.durations_min[g.league] || 180, e = Math.min(1440, s + dur);
      return {g: g, s: s, e: e, dur: dur};
    }).sort(function (a, b) { return a.s - b.s; });

    // free gaps (>= 30 min) between blocks in the loaded data
    var gaps = [], cur = 0;
    blocks.forEach(function (b) { if (b.s - cur >= 30) gaps.push([cur, b.s]); cur = Math.max(cur, b.e); });
    if (1440 - cur >= 30) gaps.push([cur, 1440]);

    var tl = '<div class="timeline"><div class="hrs">' + Array.apply(null, Array(24)).map(function (_, i) {
      return '<span>' + (i % 3 === 0 ? (i === 0 ? '12a' : i < 12 ? i + 'a' : i === 12 ? '12p' : (i - 12) + 'p') : '') + '</span>';
    }).join('') + '</div>';
    gaps.forEach(function (g) {
      tl += '<div class="free" style="left:' + (g[0] / 14.4) + '%;width:' + ((g[1] - g[0]) / 14.4) + '%"></div>';
    });
    blocks.forEach(function (b) {
      tl += '<div class="blk ' + b.g.league + '" style="left:' + (b.s / 14.4) + '%;width:' + ((b.e - b.s) / 14.4) + '%" title="' + esc(b.g.matchup) + '">' + esc(b.g.matchup) + '</div>';
    });
    tl += '</div>';

    var mlbNote = '<div class="alert"><b>MLB status: NOT LOADED.</b> This planner has not loaded the full MLB daily schedule, so no day can be confirmed FREE. The gaps below use only the loaded games (NFL/NCAAF/Giants/Athletics items in the dataset).</div>';

    var gapHtml = gaps.length ? gaps.map(function (g) {
      return '<tr><td class="nowrap">' + hm(g[0]) + ' - ' + hm(g[1] === 1440 ? 1439 : g[1]) + '</td><td class="nowrap">' + Math.round((g[1] - g[0]) / 60 * 10) / 10 + ' h</td></tr>';
    }).join('') : '<tr><td colspan="2">No gap of 30+ minutes between loaded games.</td></tr>';

    var list = dayGames.length ? dayGames.map(function (g) {
      var dur = D.durations_min[g.league];
      return '<tr><td class="nowrap">' + fmtTime(g.time_pt) + '</td><td>' + esc(g.league) + '</td><td>' + esc(g.matchup) + '</td><td>' + esc(g.broadcast) + '</td><td>' + esc(g.category) + '</td><td>' + (/^\d\d:\d\d$/.test(g.time_pt) ? '~' + dur + ' min (est.)' : 'time TBA') + '</td><td>' + srcLink(g.source_url, 'Source') + '</td></tr>';
    }).join('') : '<tr><td colspan="7">No loaded games on this date. This does NOT mean the date is free; MLB is not loaded.</td></tr>';

    app.innerHTML =
      '<div class="dayTitle">' + esc(longDate(date)) + '</div>' +
      '<div class="legend">Times are Pacific Time (PT). Game length estimates: MLB ' + D.durations_min.MLB + ' min, NFL ' + D.durations_min.NFL + ' min (includes halftime), NCAAF ' + D.durations_min.NCAAF + ' min (includes 20-min halftime). Sources in the table.</div>' +
      mlbNote +
      '<h2>Day timeline</h2>' +
      '<div class="legend"><b class="sw" style="background:#1f5fbf"></b>NFL &nbsp; <b class="sw" style="background:#7a3fb0"></b>NCAAF &nbsp; <b class="sw" style="background:#1e8e4e"></b>MLB &nbsp; <b class="sw" style="background:rgba(30,142,78,.25)"></b>gap in loaded data</div>' + tl +
      '<h2>Free-time gaps (loaded data only, 30+ minutes)</h2>' +
      '<table><thead><tr><th>Free from - to (PT)</th><th>Length</th></tr></thead><tbody>' + gapHtml + '</tbody></table>' +
      '<h2>Games on this day</h2>' +
      '<table><thead><tr><th>Start (PT)</th><th>League</th><th>Matchup</th><th>Broadcast</th><th>Category</th><th>Length est.</th><th>Source</th></tr></thead><tbody>' + list + '</tbody></table>' +
      (tba.length ? '<div class="warn">Games with TBA times on this date (not placed on timeline): ' + tba.map(function (g) { return esc(g.matchup); }).join('; ') + '</div>' : '');
  }

  // ---------- VACATION ----------
  function renderVacation(D) {
    document.getElementById('wins').innerHTML = D.windows.map(function (w) {
      var cls = /PARTLY/.test(w.status) ? 'b-part' : /ESTIMATE/.test(w.status) ? 'b-est' : 'b-ver';
      return '<tr><td class="nowrap"><b>' + esc(w.year) + '</b></td><td class="nowrap">' + esc(w.window) + '</td><td>' + esc(w.days) + '</td><td>' + esc(w.weeks) + '</td><td>' + badge(w.status, cls) + '</td><td>' + esc(w.basis) + '</td><td>' + srcLink(w.source_url, w.source_name) + '</td></tr>';
    }).join('');
  }

  // ---------- FLAGGED ----------
  function renderFlagged(D) {
    document.getElementById('flags').innerHTML = D.flags.map(function (f) {
      var cls = f.severity === 'High' ? 'b-bad' : f.severity === 'Medium' ? 'b-est' : 'b-std';
      return '<tr><td>' + esc(f.id) + '</td><td>' + badge(f.severity, cls) + '</td><td><b>' + esc(f.item) + '</b></td><td>' + esc(f.detail) + '</td><td>' + f.links.map(function (l) { return srcLink(l, 'link'); }).join('<br>') + '</td></tr>';
    }).join('');
  }

  // ---------- SOURCES ----------
  function renderSources(D) {
    document.getElementById('srcs').innerHTML = D.sources.map(function (s) {
      var sec = /secondary/i.test(s.title) ? badge('secondary', 'b-est') : badge('official / team / league', 'b-ver');
      return '<tr><td>' + sec + '</td><td>' + srcLink(s.url, s.title) + '</td><td>' + esc(s.used_for) + '</td></tr>';
    }).join('');
  }
})();
