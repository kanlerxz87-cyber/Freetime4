(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const href = (value) => {
    try { const url = new URL(value, window.location.href); return url.protocol === 'https:' ? url.href : ''; }
    catch (_) { return ''; }
  };
  const fullDate = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const shortDate = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', month: 'short', day: 'numeric', year: 'numeric' });
  const dataUrl = '../data/schedules.json';
  const category = document.body.dataset.category;

  function dateObject(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || '')) return null;
    const [year, month, day] = iso.split('-').map(Number);
    return new Date(Date.UTC(year, month - 1, day, 12));
  }
  function dateLabel(iso, long = false) {
    const date = dateObject(iso);
    return date ? (long ? fullDate : shortDate).format(date) : 'Date to be announced';
  }
  function timeLabel(time) {
    if (!/^\d{2}:\d{2}$/.test(time || '')) return '';
    const [h, m] = time.split(':').map(Number);
    return `${h % 12 || 12}:${String(m).padStart(2, '0')} ${h >= 12 ? 'PM' : 'AM'} PT`;
  }
  function link(url, label, css = 'category-card-source') {
    const safe = href(url);
    return safe ? `<a class="${css}" href="${esc(safe)}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a>` : '';
  }
  function card({ date, title, meta = '', note = '', status = '', sourceUrl = '', sourceUrls = [], undated = false }) {
    const dateText = date ? dateLabel(date) : 'DATE TBD';
    const metaText = meta || status;
    const sources = [sourceUrl, ...sourceUrls].filter(Boolean);
    const sourceLinks = sources.map((url, index) => link(url, sources.length > 1 ? `OPEN SOURCE ${index + 1}` : 'OPEN OFFICIAL SOURCE')).join('');
    return `<article class="category-card${undated ? ' status-undated' : ''}"><div class="category-card-date">${esc(dateText)}<small>${esc(status || 'SOURCE CHECKED')}</small></div><div><div class="category-card-title">${esc(title)}</div>${metaText ? `<div class="category-card-meta">${esc(metaText)}</div>` : ''}${note ? `<div class="category-card-note">${esc(note)}</div>` : ''}${sourceLinks}</div></article>`;
  }
  function reviewCards(items) {
    const root = $('#categoryReviews');
    if (!root) return;
    root.innerHTML = items.length ? items.map((item) => {
      const sourceLinks = (item.sourceUrls || []).map((url, index) => link(url, `SOURCE ${index + 1}`, 'category-card-source')).join('');
      const mark = item.severity === 'high' ? '!' : item.severity === 'medium' ? '·' : 'i';
      return `<article class="review-card" data-severity="${esc(item.severity)}"><span class="review-severity" aria-hidden="true">${mark}</span><div><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p><div class="review-links">${sourceLinks}</div></div></article>`;
    }).join('') : '<div class="empty-state">No review flags are attached to this category in the current audit.</div>';
  }
  function stationTag(station) {
    const text = String(station.availability || '').toLowerCase();
    if (text.includes('stream') || text.includes('online')) return 'STREAM ONLY';
    if (text.includes('sacramento')) return 'OUTSIDE TARGET';
    if (text.includes('bay area')) return 'BAY AREA LISTING';
    return 'VERIFY LOCALLY';
  }
  function renderStations(data) {
    const root = $('#categoryStations');
    if (!root) return;
    root.innerHTML = (data.radioStations || []).map((station) => {
      const sourceLinks = (station.sourceUrls || []).map((url, i) => link(url, `SOURCE ${i + 1}`, 'station-source')).join('');
      return `<article class="station-card"><div class="station-frequency">${esc(station.station)}<small>${esc(stationTag(station))}</small></div><div class="station-description"><b>${esc(station.programming)}</b><br>${esc(station.availability)}<div class="station-links">${sourceLinks}</div></div></article>`;
    }).join('');
    const note = document.createElement('p');
    note.className = 'category-footer-note';
    note.textContent = 'All radio listings are source snapshots, not a guarantee that the station will clear a particular game. For the Athletics, the checked 2026 terrestrial listings are in Sacramento; no San Francisco English AM/FM affiliate was confirmed. A’s Cast and Varsity Network are online options, not terrestrial coverage.';
    root.after(note);
  }
  function renderMlb(data) {
    const coverage = $('#categoryCoverage');
    if (coverage) coverage.innerHTML = `<b>Coverage note:</b> ${esc(data.mlbCoverage?.detail || 'The bundled file contains selected MLB event dates only.')}`;
    const root = $('#categoryEvents');
    const items = data.mlbEvents || [];
    root.innerHTML = items.map((event) => card({
      date: event.date,
      title: event.title,
      meta: [event.location, event.timePT ? timeLabel(event.timePT) : 'Start time not confirmed'].filter(Boolean).join(' · '),
      note: event.note,
      status: event.status,
      sourceUrl: event.sourceUrl,
      sourceUrls: event.supportingSourceUrls || [],
      undated: !event.date
    })).join('');
    reviewCards((data.reviewItems || []).filter((item) => item.id.startsWith('mlb') || item.id === 'a-radio'));
  }
  function renderNfl(data) {
    const records = [...(data.fortyNiners || [])].sort((a, b) => (a.date || '9999').localeCompare(b.date || '9999'));
    const root = $('#categoryEvents');
    root.innerHTML = records.map((event) => {
      const date = event.date || null;
      const location = [event.venue, event.homeAway].filter(Boolean).join(' · ');
      const meta = [event.phase, event.week, location, event.timePT ? timeLabel(event.timePT) : ''].filter(Boolean).join(' · ');
      return card({
        date, title: `San Francisco 49ers ${event.homeAway === 'Home' ? 'vs' : 'at'} ${event.opponent}`,
        meta, note: event.timeNote || (event.status === 'completed' ? 'Completed. Kickoff time is not shown because it was not retained in the reviewed source extract.' : ''),
        status: event.status === 'completed' ? 'FINAL' : event.status === 'date-and-time-tbd' ? 'WEEK 18 · DATE/TIME TBD' : event.timePT ? 'UPCOMING · TIME LISTED' : 'SCHEDULED · TIME TBD',
        sourceUrl: event.sourceUrl, undated: !date
      });
    }).join('');
    const next = records.filter((item) => item.date && item.date >= data.asOf && item.status !== 'completed').length;
    const tbd = records.filter((item) => !item.date || item.status.includes('tbd')).length;
    $('#categoryStats').innerHTML = `<div class="category-stat"><b>${records.length}</b><span>2026 SCHEDULE ROWS</span></div><div class="category-stat"><b>${next}</b><span>DATED UPCOMING MATCHUPS</span></div><div class="category-stat"><b>${tbd}</b><span>DATE / TIME GAPS</span></div>`;
    const leagueRoot = $('#categoryLeagueDates');
    if (leagueRoot) {
      leagueRoot.innerHTML = (data.leagueDates || []).map((item) => card({
        date: item.date, title: item.title,
        meta: item.subtitle || item.program || 'League-wide date',
        note: item.note || '', status: 'LEAGUE WINDOW · NOT A 49ERS FIXTURE',
        sourceUrl: item.sourceUrl
      })).join('');
    }
    reviewCards((data.reviewItems || []).filter((item) => item.id.startsWith('49ers') || item.id === 'broadcast-end-times'));
  }
  function renderCollege(data) {
    const records = [...(data.collegeFootball || [])];
    const canonical = (value) => String(value || '').replace(/^California(?: \(Big Game\))?$/, 'Cal').trim();
    const seen = new Set();
    const deduped = records.filter((item) => {
      if (!item.date) return true;
      const pair = [canonical(item.team), canonical(item.opponent)].sort().join('|');
      const key = `${item.date}|${pair}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    const dated = deduped.filter((item) => item.date).sort((a, b) => a.date.localeCompare(b.date) || a.team.localeCompare(b.team));
    const undated = deduped.filter((item) => !item.date).sort((a, b) => a.seasonYear - b.seasonYear || a.team.localeCompare(b.team) || a.opponent.localeCompare(b.opponent));
    $('#categoryEvents').innerHTML = dated.map((event) => {
      const side = event.homeAway === 'Home' ? 'vs' : 'at';
      const title = `${event.team} ${side} ${event.opponent}`;
      const meta = [event.seasonYear, event.homeAway, event.venue, event.timePT ? timeLabel(event.timePT) : ''].filter(Boolean).join(' · ');
      return card({
        date: event.date, title, meta,
        note: event.timeNote || (event.status === 'completed' ? 'Past game; kickoff time omitted from this source extract.' : ''),
        status: event.status === 'completed' ? 'FINAL' : event.timePT ? 'UPCOMING · TIME LISTED' : 'DATE CONFIRMED · TIME TBD',
        sourceUrl: event.sourceUrl
      });
    }).join('');
    $('#categoryUndated').innerHTML = undated.map((event) => {
      const legacy = event.status.includes('legacy');
      const title = `${event.team} ${event.homeAway === 'Home' ? 'hosts' : 'visits'} ${event.opponent}`;
      const meta = [event.seasonYear, event.venue || 'Venue not confirmed'].join(' · ');
      return card({ date: null, title, meta, note: event.timeNote || (legacy ? 'Historical series date/opponent listing needs revalidation.' : 'Official opponent is known; game date, kickoff and complete venue details are TBD.'), status: legacy ? 'LEGACY · REVALIDATION NEEDED' : 'OPPONENT CONFIRMED · DATE TBD', sourceUrl: event.sourceUrl, undated: true });
    }).join('');
    const legacy = data.legacyOpponentGrids || [];
    if (legacy.length) {
      const heading = document.createElement('div');
      heading.className = 'category-legacy-heading';
      heading.innerHTML = '<span class="category-index">ARCHIVED GRID · NOT A CURRENT DATED SCHEDULE</span><h3>Eight-game ACC opponent grids from 2023</h3><p>Shown for provenance only; later scheduling moved to a nine-game model.</p>';
      const block = document.createElement('div');
      block.className = 'category-legacy-grid';
      block.innerHTML = legacy.map((item) => `<article class="category-card status-undated"><div class="category-card-date">${esc(item.seasonYear)}<small>ARCHIVED · VERIFY</small></div><div><div class="category-card-title">${esc(item.team)} · ACC opponents</div><div class="category-card-meta"><b>Home:</b> ${esc(item.home)}<br><b>Away:</b> ${esc(item.away)}</div><div class="category-card-note">${esc(item.note)}</div>${link(item.sourceUrl, 'OPEN ARCHIVED SOURCE')}</div></article>`).join('');
      $('#categoryUndated').after(heading, block);
    }
    $('#categoryStats').innerHTML = `<div class="category-stat"><b>${dated.filter((item) => item.seasonYear === 2026).length}</b><span>2026 DATED TEAM ROWS</span></div><div class="category-stat"><b>${undated.filter((item) => item.seasonYear === 2027 && !item.status.includes('legacy')).length}</b><span>2027 OPPONENTS · DATE TBD</span></div><div class="category-stat"><b>${undated.filter((item) => item.status.includes('legacy')).length + legacy.length}</b><span>LEGACY / NEEDS REVALIDATION</span></div>`;
    reviewCards((data.reviewItems || []).filter((item) => item.id.startsWith('college-') || item.id === 'broadcast-end-times'));
  }
  function renderSources(data) {
    const root = $('#categorySources');
    if (!root) return;
    const catalog = [
      { heading: 'MLB · league schedule & broadcasts', keys: [
        ['mlbApi', 'MLB Stats API · 2027 schedule', 'League schedule source. The static site does not bundle all 2,430 regular-season games.'],
        ['mlbSpringTraining2027', 'MLB Stats API · Feb 19, 2027', 'Spring-training day-level query; 17 games were listed, but individual rows are not bundled.']
        ['mlb2027AllStar', 'MLB · future All-Star locations', '2027 host confirmation; start time remains TBD.'],
        ['mlb2027AllStarDate', 'MLB Stats API · 2027 All-Star date', 'Date check for the July 13 game; no start time assigned.'],
        ['mlb2027FieldOfDreams', 'MLB · Field of Dreams 2027', 'Royals–Red Sox event announcement; API separately supplies the listed PT start.'],
        ['mlb2027FieldOfDreamsDate', 'MLB Stats API · Field of Dreams date', 'Date and listed Pacific start-time check.']
        ['mlb2028AllStar', 'MLB · 2028 All-Star host', 'Oracle Park is confirmed; date not confirmed in the checked source.'],
        ['mlbRadio2026', 'MLB · 2026 team broadcast guide', 'Current club broadcast and affiliate listings.'],
        ['giantsRadio', 'San Francisco Giants · radio schedule', 'Giants terrestrial radio listing.'],
        ['athleticsRadioAffiliate', 'Athletics · radio affiliates', 'Athletics affiliate page; check local market carriage.'],
        ['athleticsStreaming', 'Athletics · in-market audio', 'A’s Cast / online audio option, not an AM/FM transmitter.']
      ]},
      { heading: 'NFL · 49ers & Westwood One', keys: [
        ['fortyNinersSchedule', 'San Francisco 49ers · 2026 schedule', 'Official matchups, venues and Pacific kickoff times when published.'],
        ['fortyNinersRadio', 'San Francisco 49ers · TV and radio partners', '49ers broadcast partner listing.'],
        ['fortyNinersRadioPartner', '49ers · KNBR partnership', 'Official KNBR relationship announcement.'],
        ['nflTeamSchedule', 'NFL · 49ers team schedule', 'League schedule cross-check.'],
        ['nflWeek18', 'NFL · Week 18 schedule', 'Week 18 opponent and TBD timing reference.'],
        ['nfl2027Schedule', 'NFL · future team schedule page', 'Checked future schedule endpoint; no 2027 team rows returned.'],
        ['nflDates', 'NFL · important dates 2026–27', 'League-wide postseason date windows; not a 49ers fixture.'],
        ['wwoSchedule', 'Westwood One · NFL schedule', 'Network broadcast windows listed in ET.'],
        ['wwoStationFinder', 'Westwood One · NFL station finder', 'Directory labeled 2025; not a 2026–29 carriage guarantee.'],
        ['knbrShows', 'KNBR · station and programming', 'Station programming reference.']
      ]},
      { heading: 'College football · Stanford & Cal', keys: [
        ['stanford2026Schedule', 'Stanford Athletics · 2026 schedule', 'Stanford football schedule and next game.'],
        ['stanford2027Opponents', 'Stanford Athletics · 2027 ACC opponents', 'Opponent grid without dates/times for most games.'],
        ['stanfordFutureNonconference', 'Stanford Athletics · historical future-schedule table', '2015 schedule table; old future entries are not revalidated.'],
        ['stanfordNotreDame', 'Stanford–Notre Dame · dates added', 'Confirmed 2027 and 2028 series dates.'],
        ['stanfordBostonCollege', 'Stanford–Boston College series', '2016 announcement; future dates require revalidation.'],
        ['stanfordLegacyAccGrid', 'Stanford · archived ACC model', '2023 eight-game model; retained as legacy context only.'],
        ['stanfordRadio', 'Stanford Athletics · 2026 radio team', '2026 Stanford football radio listing.'],
        ['cal2026Schedule', 'Cal Athletics · 2026 schedule', 'Cal football schedule and Nov 28 finale.'],
        ['cal2027Opponents', 'Cal Athletics · 2027 ACC opponents', 'Opponent grid; conference dates/times remain TBD.'],
        ['cal2027Nonconference', 'Cal Athletics · 2027 nonconference', 'Sacramento State and Old Dominion dates.'],
        ['calFutureSchedules', 'Cal–UCLA · four scheduled dates', 'Official dates from 2026 through 2029.'],
        ['calLegacyAccGrid', 'Cal · archived ACC opponent grid', '2023 eight-game model; retained as legacy context only.'],
        ['calRadioGuide', 'Cal Athletics · 2026 football info guide', '2026 frequency and online audio reference; call-sign branding conflicts.'],
        ['calPittTime', 'Cal–Pittsburgh · regular-season finale', 'Cal’s Nov 28, 2026 game time announcement.']
      ]}
    ];
    root.innerHTML = catalog.map((group) => `<section class="category-source-group"><div class="category-index">${esc(group.heading)}</div><div class="category-source-grid">${group.keys.map(([key, name, note]) => {
      const url = data.sources?.[key];
      return url ? `<article class="category-card"><div><div class="category-card-title">${esc(name)}</div><div class="category-card-note">${esc(note)}</div>${link(url, 'OPEN OFFICIAL SOURCE')}</div></article>` : '';
    }).join('')}</div></section>`).join('');
    reviewCards(data.reviewItems || []);
  }

  async function init() {
    try {
      const response = await fetch(dataUrl, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Schedule data request failed (${response.status})`);
      const data = await response.json();
      if (category === 'mlb') renderMlb(data);
      if (category === 'nfl') renderNfl(data);
      if (category === 'college') renderCollege(data);
      if (category === 'radio') {
        renderStations(data);
        reviewCards((data.reviewItems || []).filter((item) => ['a-radio', 'cal-radio-brand', 'wwo-affiliates', 'broadcast-end-times'].includes(item.id)));
      }
      if (category === 'sources') renderSources(data);
    } catch (error) {
      document.querySelectorAll('.loading-state').forEach((node) => { node.textContent = `${error.message}. Reload through GitHub Pages or a local web server; opening this file directly may block data loading.`; });
    }
  }
  document.addEventListener('DOMContentLoaded', init, { once: true });
})();
