(() => {
  'use strict';

  const DATA_URL = 'site/data/schedules.json';
  const DATE_FMT = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', weekday: 'short', month: 'short', day: 'numeric' });
  const DATE_LONG_FMT = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const MONTH_FMT = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', month: 'long', year: 'numeric' });
  const CATEGORY_NAMES = { mlb: 'MLB special event', nfl: 'NFL / 49ers & league dates', college: 'College football', wwo: 'Westwood One national radio' };
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  let data;
  let events = [];
  let eventById = new Map();
  let activeFilter = 'all';
  let activeView = 'calendar';
  let currentMonth;
  let searchText = '';
  let todayISO = '2026-11-25';

  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  }

  function safeURL(value) {
    try {
      const parsed = new URL(value, window.location.href);
      return parsed.protocol === 'https:' ? parsed.href : '';
    } catch (_) {
      return '';
    }
  }

  function dateParts(iso) {
    if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return null;
    const [year, month, day] = iso.split('-').map(Number);
    return { year, month, day };
  }

  function utcDate(iso) {
    const parts = dateParts(iso);
    return parts ? new Date(Date.UTC(parts.year, parts.month - 1, parts.day, 12)) : null;
  }

  function formatDate(iso, long = false) {
    const date = utcDate(iso);
    if (!date) return 'Date to be announced';
    return (long ? DATE_LONG_FMT : DATE_FMT).format(date);
  }

  function formatTime(time) {
    if (!time || !/^\d{2}:\d{2}$/.test(time)) return '';
    const [hour, minute] = time.split(':').map(Number);
    const suffix = hour >= 12 ? 'PM' : 'AM';
    const twelveHour = hour % 12 || 12;
    return `${twelveHour}:${String(minute).padStart(2, '0')} ${suffix} PT`;
  }

  function fmtCount(value) {
    return new Intl.NumberFormat('en-US').format(value);
  }

  function canonicalTeam(value) {
    return String(value || '').replace(/^California(?: \(Big Game\))?$/, 'Cal').trim();
  }

  function normaliseData(source) {
    const out = [];
    const push = (event) => {
      if (!event || !event.date || !dateParts(event.date)) return;
      event.id = `${event.kind}-${event.idSeed}`;
      out.push(event);
    };

    (source.mlbEvents || []).forEach((item, index) => {
      push({
        kind: 'mlb', idSeed: `mlb-${index}`, date: item.date, timePT: item.timePT || null,
        title: item.title, subtitle: item.location || 'MLB event', venue: item.location || '', status: item.status,
        sourceUrl: item.sourceUrl, supportingSourceUrls: item.supportingSourceUrls || [], note: item.note || '', category: 'mlb', phase: 'Special event',
        seasonYear: item.seasonYear, label: item.timePT ? 'MLB' : 'MLB · TIME TBD'
      });
    });

    (source.fortyNiners || []).forEach((item, index) => {
      if (!item.date) return;
      const side = item.homeAway === 'Home' ? 'vs' : 'at';
      push({
        kind: 'nfl', idSeed: `49ers-${index}`, date: item.date, timePT: item.timePT || null,
        title: `49ers ${side} ${item.opponent}`, subtitle: `${item.week} · ${item.phase}`,
        venue: item.venue || '', status: item.status, sourceUrl: item.sourceUrl,
        note: item.timeNote || '', category: 'nfl', seasonYear: item.seasonYear,
        label: `49ERS · ${item.week}`
      });
    });

    (source.leagueDates || []).forEach((item, index) => {
      push({
        kind: 'league', idSeed: `nfl-league-${index}`, date: item.date, timePT: item.timePT || null,
        title: item.title, subtitle: item.subtitle || item.program || 'NFL league calendar', venue: item.venue || '',
        status: item.status || 'league-window', sourceUrl: item.sourceUrl, note: item.note || '',
        category: 'nfl', seasonYear: Number(item.date.slice(0, 4)), label: 'NFL LEAGUE DATE'
      });
    });

    const seenCollege = new Set();
    (source.collegeFootball || []).forEach((item, index) => {
      if (!item.date) return;
      const team = canonicalTeam(item.team);
      const opponent = canonicalTeam(item.opponent);
      const pairing = [team, opponent].sort((a, b) => a.localeCompare(b)).join('|');
      const key = `${item.date}|${pairing}`;
      if (seenCollege.has(key)) return;
      seenCollege.add(key);
      const side = item.homeAway === 'Home' ? 'vs' : 'at';
      push({
        kind: 'college', idSeed: `college-${index}`, date: item.date, timePT: item.timePT || null,
        title: `${team} ${side} ${opponent}`, subtitle: `${item.team} football · ${item.seasonYear}`,
        venue: item.venue || '', status: item.status, sourceUrl: item.sourceUrl,
        note: item.timeNote || '', category: 'college', seasonYear: item.seasonYear,
        label: `${team.toUpperCase()} FOOTBALL`
      });
    });

    (source.westwoodOne || []).forEach((item, index) => {
      push({
        kind: 'wwo', idSeed: `wwo-${index}`, date: item.date, timePT: item.timePT || null,
        title: item.matchup, subtitle: `${item.program} · network slot`, venue: '', status: 'network-window',
        sourceUrl: item.sourceUrl, note: 'Westwood One listed airtime start, converted from Eastern to Pacific Time. This is a broadcast slot, not a guaranteed kickoff or local affiliate clearance.',
        category: 'wwo', phase: item.program, seasonYear: Number(item.date.slice(0, 4)), label: 'WESTWOOD ONE'
      });
    });

    return out.sort((a, b) => a.date.localeCompare(b.date) || (a.timePT || '99:99').localeCompare(b.timePT || '99:99'));
  }

  function getFilteredEvents() {
    return events.filter((event) => {
      const categoryMatches = activeFilter === 'all' || event.category === activeFilter;
      if (!categoryMatches) return false;
      if (!searchText) return true;
      const haystack = [event.title, event.subtitle, event.venue, event.note, event.label].join(' ').toLowerCase();
      return haystack.includes(searchText);
    });
  }

  function statusLabel(event) {
    if (event.status === 'completed' || (event.date < todayISO && event.kind !== 'wwo')) return 'Completed';
    if (event.timePT) return event.kind === 'wwo' ? 'Network airtime start' : 'Scheduled start';
    return 'Date confirmed · time TBD';
  }

  function eventClock(event) {
    if (event.timePT) return formatTime(event.timePT);
    if (event.status === 'completed' || event.date < todayISO) return 'TIME NOT RETAINED';
    return 'TIME TBD';
  }

  function openEvent(event) {
    const dialog = $('#eventDialog');
    if (!dialog || !event) return;
    const body = $('.dialog-body', dialog);
    const sourceHrefs = [event.sourceUrl, ...(event.supportingSourceUrls || [])].map(safeURL).filter(Boolean);
    body.innerHTML = `
      <div class="dialog-kicker">${escapeHTML(CATEGORY_NAMES[event.category] || 'Schedule event')} · ${escapeHTML(event.label || '')}</div>
      <h2 id="dialogTitle">${escapeHTML(event.title)}</h2>
      <p class="dialog-date">${escapeHTML(formatDate(event.date, true))}${event.timePT ? ` · ${escapeHTML(formatTime(event.timePT))}` : ' · Time not confirmed'}</p>
      <div class="dialog-facts">
        ${event.subtitle ? `<div><span>DETAIL</span><b>${escapeHTML(event.subtitle)}</b></div>` : ''}
        ${event.venue ? `<div><span>LOCATION</span><b>${escapeHTML(event.venue)}</b></div>` : ''}
        <div><span>STATUS</span><b>${escapeHTML(statusLabel(event))}</b></div>
      </div>
      <p class="dialog-note">${escapeHTML(event.note || 'No additional source note was recorded.')}</p>
      ${sourceHrefs.map((sourceHref, index) => `<a class="dialog-source" href="${escapeHTML(sourceHref)}" target="_blank" rel="noopener noreferrer">${sourceHrefs.length > 1 ? `Open source ${index + 1}` : 'Open official source'} ↗</a>`).join(' ')}`;
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  }

  function bindEventOpeners(root) {
    $$('[data-event-id]', root).forEach((button) => {
      button.addEventListener('click', () => openEvent(eventById.get(button.dataset.eventId)));
    });
  }

  function renderCalendar() {
    const grid = $('#calendarGrid');
    if (!grid) return;
    const monthStart = new Date(Date.UTC(currentMonth.getUTCFullYear(), currentMonth.getUTCMonth(), 1, 12));
    const offset = (monthStart.getUTCDay() + 6) % 7;
    const start = new Date(Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth(), 1 - offset, 12));
    const monthEnd = new Date(Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth() + 1, 0, 12));
    const monthISO = `${monthStart.getUTCFullYear()}-${String(monthStart.getUTCMonth() + 1).padStart(2, '0')}`;
    const visibleEvents = getFilteredEvents();
    const byDate = new Map();
    visibleEvents.forEach((event) => {
      if (!event.date.startsWith(monthISO)) return;
      if (!byDate.has(event.date)) byDate.set(event.date, []);
      byDate.get(event.date).push(event);
    });

    const cells = [];
    for (let i = 0; i < 42; i += 1) {
      const date = new Date(start.getTime() + i * 86400000);
      const iso = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
      const isOutside = date.getUTCMonth() !== monthStart.getUTCMonth();
      const dayEvents = byDate.get(iso) || [];
      const isToday = iso === todayISO;
      const eventMarkup = dayEvents.slice(0, 2).map((event) => {
        const time = event.timePT ? formatTime(event.timePT).replace(' PT', '') : (event.kind === 'wwo' ? 'AIR TIME' : event.status === 'completed' ? 'PAST GAME' : 'TIME TBD');
        return `<button class="day-event ${escapeHTML(event.category)} ${event.timePT ? '' : 'tbd'}" type="button" data-event-id="${escapeHTML(event.id)}" aria-label="${escapeHTML(`${event.title}, ${formatDate(event.date, true)}, ${event.timePT ? formatTime(event.timePT) : 'time not confirmed'}`)}"><span><span class="event-time">${escapeHTML(time)}</span><span class="event-title">${escapeHTML(event.title)}</span></span></button>`;
      }).join('');
      const more = dayEvents.length > 2 ? `<div class="more-events">+${dayEvents.length - 2} more</div>` : '';
      cells.push(`<div class="calendar-cell${isOutside ? ' outside' : ''}${isToday ? ' is-today' : ''}" data-date="${iso}"><div class="day-number"><span>${date.getUTCDate()}</span>${isToday ? '<span class="today-pill">TODAY</span>' : ''}</div>${eventMarkup}${more}</div>`);
    }
    grid.innerHTML = cells.join('');
    const periodTitle = $('#periodTitle');
    if (periodTitle) periodTitle.textContent = MONTH_FMT.format(monthStart);
    const startCaption = $('#resultSummary');
    const filtered = visibleEvents.filter((event) => event.date.startsWith(monthISO));
    const undated = activeFilter === 'college' ? (data.collegeFootball || []).filter((event) => !event.date && event.status === 'opponent-confirmed-date-time-tbd').length : 0;
    if (startCaption) {
      let label = `${fmtCount(filtered.length)} dated ${filtered.length === 1 ? 'event' : 'events'} in this view`;
      if (activeFilter === 'mlb') label += ' · selected MLB dates only; full 2027 slate is not bundled';
      if (activeFilter === 'college') label += ` · ${fmtCount(undated)} confirmed opponents remain undated`;
      if (activeFilter === 'all') label += ' · unknown dates and times are not inferred';
      startCaption.textContent = label;
    }
    const countAll = $('#countAll');
    if (countAll) countAll.textContent = fmtCount(events.length);
    grid.classList.toggle('hidden', activeView === 'list');
    $('#calendarShell')?.classList.toggle('hidden', activeView === 'list');
    $('#eventList')?.classList.toggle('hidden', activeView !== 'list');
    if (activeView === 'list') renderEventList(filtered);
    bindEventOpeners(grid);
  }

  function renderEventList(monthEvents) {
    const list = $('#eventList');
    if (!list) return;
    if (!monthEvents.length) {
      list.innerHTML = '<div class="empty-state">No dated items match this period and filter. A blank calendar is not a verified free window; see the coverage notes below.</div>';
      return;
    }
    list.innerHTML = monthEvents.map((event) => {
      const sourceHref = safeURL(event.sourceUrl);
      return `<article class="event-row ${escapeHTML(event.category)}"><div class="event-row-date">${escapeHTML(formatDate(event.date))}</div><div><button type="button" class="event-open" data-event-id="${escapeHTML(event.id)}">${escapeHTML(event.title)}</button><div class="event-row-meta">${escapeHTML(event.subtitle || '')}${event.venue ? ` · ${escapeHTML(event.venue)}` : ''}</div></div><div class="event-row-action"><span class="event-row-time">${escapeHTML(eventClock(event))}</span>${sourceHref ? `<a class="event-source" href="${escapeHTML(sourceHref)}" target="_blank" rel="noopener noreferrer">SOURCE ↗</a>` : ''}</div></article>`;
    }).join('');
    bindEventOpeners(list);
  }

  function updateMonth(offset = 0) {
    currentMonth = new Date(Date.UTC(currentMonth.getUTCFullYear(), currentMonth.getUTCMonth() + offset, 1, 12));
    renderCalendar();
  }

  function upcomingGames() {
    return events.filter((event) => event.category !== 'wwo' && event.kind !== 'league' && event.date >= todayISO && event.status !== 'completed')
      .sort((a, b) => a.date.localeCompare(b.date) || (a.timePT || '99:99').localeCompare(b.timePT || '99:99'));
  }

  function renderNextEvent() {
    const root = $('#nextEvent');
    if (!root) return;
    const next = upcomingGames()[0];
    if (!next) {
      root.innerHTML = '<div class="empty-state">No future team event has a verified date in this dataset.</div>';
      return;
    }
    const sourceHref = safeURL(next.sourceUrl);
    root.innerHTML = `<span class="next-kicker">${escapeHTML(CATEGORY_NAMES[next.category] || 'CONFIRMED EVENT')}</span><b class="next-title">${escapeHTML(next.title)}</b><span class="next-date">${escapeHTML(formatDate(next.date, true))}${next.timePT ? ` · ${escapeHTML(formatTime(next.timePT))}` : ' · time TBD'}</span><span class="next-detail">${escapeHTML([next.subtitle, next.venue].filter(Boolean).join(' · '))}</span>${sourceHref ? `<a class="next-source" href="${escapeHTML(sourceHref)}" target="_blank" rel="noopener noreferrer">SOURCE RECORD ↗</a>` : ''}`;
  }

  function renderTicker() {
    const root = $('#tickerContent');
    if (!root) return;
    const next = upcomingGames()[0];
    const duration = data.durationAssumptions || {};
    const items = [
      `<span class="ticker-item"><i></i><span><b>${next ? escapeHTML(next.title) : 'No dated game'}</b> · ${next ? escapeHTML(formatDate(next.date)) : 'Check the coverage flags'}</span></span>`,
      '<span class="ticker-item"><i></i><span><b>NO VERIFIED ALL-CLEAR WINDOW</b> · future schedule coverage is incomplete</span></span>',
      `<span class="ticker-item"><i></i><span><b>MLB</b> · ${escapeHTML(duration.mlb?.label || 'planning baseline')}</span></span>`,
      '<span class="ticker-item"><i></i><span><b>A’S RADIO</b> · Bay Area terrestrial affiliate not confirmed</span></span>'
    ];
    root.innerHTML = items.join('');
  }

  function renderWestwoodOne() {
    const root = $('#wwoEvents');
    if (!root) return;
    const upcoming = (data.westwoodOne || []).filter((event) => event.date >= todayISO).slice(0, 6);
    if (!upcoming.length) {
      root.innerHTML = '<div class="empty-state">No upcoming network window in the reviewed schedule.</div>';
      return;
    }
    root.innerHTML = upcoming.map((event) => `<div class="wwo-event"><div class="wwo-event-date">${escapeHTML(formatDate(event.date))}<br>${escapeHTML(event.timePT ? formatTime(event.timePT).replace(' PT', '') : 'TIME TBD')}</div><div class="wwo-event-match">${escapeHTML(event.matchup)}<span class="wwo-event-program">${escapeHTML(event.program)}</span></div></div>`).join('');
  }

  function stationTag(station) {
    const text = String(station.availability || '').toLowerCase();
    if (text.includes('stream') || text.includes('online')) return 'STREAM ONLY';
    if (text.includes('sacramento')) return 'OUTSIDE TARGET';
    if (text.includes('bay area')) return 'BAY AREA LISTING';
    return 'VERIFY LOCALLY';
  }

  function renderStations() {
    const root = $('#stationList');
    if (!root) return;
    const stations = data.radioStations || [];
    root.innerHTML = stations.map((station) => {
      const links = (station.sourceUrls || []).map((url, index) => {
        const href = safeURL(url);
        if (!href) return '';
        return `<a href="${escapeHTML(href)}" target="_blank" rel="noopener noreferrer">SOURCE ${index + 1} ↗</a>`;
      }).join('');
      return `<article class="station-card"><div class="station-frequency">${escapeHTML(station.station)}<small>${escapeHTML(stationTag(station))}</small></div><div class="station-description"><b>${escapeHTML(station.programming)}</b><br>${escapeHTML(station.availability)}<div class="station-links">${links}</div></div></article>`;
    }).join('');
  }

  function renderHorizon() {
    const stats = $('#horizonStats');
    const list = $('#reviewList');
    const reviewItems = data.reviewItems || [];
    if (stats) {
      const highCount = reviewItems.filter((item) => item.severity === 'high').length;
      stats.innerHTML = [
        `<div class="horizon-stat"><b class="stat-number">0</b><span class="stat-label">VERIFIED ALL-CLEAR<br>VACATION WINDOWS</span></div>`,
        `<div class="horizon-stat"><b class="stat-number">${fmtCount(data.mlbCoverage?.officialRegularSeasonGames || 0)}</b><span class="stat-label">2027 MLB REGULAR-SEASON GAMES<br>NOT INCLUDED AS GAME ROWS</span></div>`,
        `<div class="horizon-stat"><b class="stat-number">${fmtCount(highCount)}</b><span class="stat-label">HIGH-PRIORITY COVERAGE FLAGS<br>TO RESOLVE BEFORE PLANNING</span></div>`
      ].join('');
    }
    if (!list) return;
    list.innerHTML = reviewItems.map((item) => {
      const refs = (item.sourceUrls || []).map((url, index) => {
        const href = safeURL(url);
        return href ? `<a href="${escapeHTML(href)}" target="_blank" rel="noopener noreferrer">SOURCE ${index + 1} ↗</a>` : '';
      }).join('');
      const sign = item.severity === 'high' ? '!' : item.severity === 'medium' ? '·' : 'i';
      return `<article class="review-card" data-severity="${escapeHTML(item.severity)}"><span class="review-severity" aria-hidden="true">${sign}</span><div><h3>${escapeHTML(item.title)}</h3><p>${escapeHTML(item.detail)}</p><div class="review-links">${refs}</div></div></article>`;
    }).join('');
  }

  function renderMethods() {
    const root = $('#methodCards');
    if (!root) return;
    const mlb = data.durationAssumptions?.mlb || {};
    const football = data.durationAssumptions?.football || {};
    const sources = data.sources || {};
    const cards = [
      {
        index: '01 / PRIMARY DATA', title: 'Official schedule pages',
        text: 'League and athletics schedule pages are the event record. We use the date and time shown there and keep TBDs blank. Westwood One’s network slot is kept distinct from kickoff and local carriage.',
        links: [['MLB Stats API', sources.mlbApi], ['49ers schedule', sources.fortyNinersSchedule], ['Stanford Athletics', sources.stanford2026Schedule], ['Cal Athletics', sources.cal2026Schedule]]
      },
      {
        index: '02 / TIME BUDGET', title: 'End times are estimates',
        text: `${mlb.label || 'MLB average'}: ${mlb.basis || ''} Football: ${football.label || 'planning estimate'}; ${football.basis || ''} Neither value determines an actual broadcast end or affiliate sign-off.`,
        links: [['MLB game-time context', mlb.sourceUrl], ['NFL rulebook', football.sourceUrl]]
      },
      {
        index: '03 / LIMITS', title: 'No fake free-time claim',
        text: 'An empty day means only that this file has no dated row for the selected leagues. Future team schedules, station conflicts, postseason and local pre/postgame windows may be missing. We do not recommend a vacation window until coverage is complete.',
        links: [['NFL dates', sources.nflDates], ['Westwood One schedule', sources.wwoSchedule], ['Station finder', sources.wwoStationFinder]]
      }
    ];
    root.innerHTML = cards.map((card) => {
      const links = card.links.map(([label, url]) => {
        const href = safeURL(url);
        return href ? `<a href="${escapeHTML(href)}" target="_blank" rel="noopener noreferrer">${escapeHTML(label)} ↗</a>` : '';
      }).join('');
      return `<article class="method-card"><span class="method-card-index">${escapeHTML(card.index)}</span><h3>${escapeHTML(card.title)}</h3><p>${escapeHTML(card.text)}</p><div class="method-links">${links}</div></article>`;
    }).join('');
  }

  function setupControls() {
    $$('#sportFilters [data-filter]').forEach((button) => {
      button.addEventListener('click', () => {
        activeFilter = button.dataset.filter;
        $$('#sportFilters [data-filter]').forEach((tab) => {
          const selected = tab === button;
          tab.classList.toggle('active', selected);
          tab.setAttribute('aria-pressed', String(selected));
        });
        renderCalendar();
      });
    });
    $$('[data-view]').forEach((button) => {
      button.addEventListener('click', () => {
        activeView = button.dataset.view;
        $$('[data-view]').forEach((view) => {
          const selected = view === button;
          view.classList.toggle('active', selected);
          view.setAttribute('aria-pressed', String(selected));
        });
        renderCalendar();
      });
    });
    $('#prevPeriod')?.addEventListener('click', () => updateMonth(-1));
    $('#nextPeriod')?.addEventListener('click', () => updateMonth(1));
    $('#todayButton')?.addEventListener('click', () => {
      const today = dateParts(todayISO);
      currentMonth = new Date(Date.UTC(today.year, today.month - 1, 1, 12));
      renderCalendar();
    });
    $('#scheduleSearch')?.addEventListener('input', (event) => {
      searchText = event.target.value.trim().toLowerCase();
      renderCalendar();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        event.preventDefault();
        $('#scheduleSearch')?.focus();
      }
      if (event.key === 'Escape') $('#eventDialog')?.close?.();
    });
    const dialog = $('#eventDialog');
    dialog?.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
    $$('.dialog-close').forEach((button) => button.addEventListener('click', () => dialog?.close()));
  }

  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Schedule data request failed (${response.status})`);
      data = await response.json();
      todayISO = data.asOf || todayISO;
      const asOf = $('#asOfLabel');
      if (asOf) {
        asOf.dateTime = todayISO;
        asOf.textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', month: 'short', day: '2-digit', year: 'numeric' }).format(utcDate(todayISO)).toUpperCase();
      }
      currentMonth = (() => { const part = dateParts(todayISO); return new Date(Date.UTC(part.year, part.month - 1, 1, 12)); })();
      events = normaliseData(data);
      eventById = new Map(events.map((event) => [event.id, event]));
      setupControls();
      renderCalendar();
      renderNextEvent();
      renderTicker();
      renderWestwoodOne();
      renderStations();
      renderHorizon();
      renderMethods();
    } catch (error) {
      const message = 'The schedule data could not be loaded. Use the source links and the methodology notes in the repository to verify the latest schedules.';
      const summary = $('#resultSummary');
      if (summary) summary.textContent = message;
      const grid = $('#calendarGrid');
      if (grid) grid.innerHTML = `<div class="empty-state">${escapeHTML(error.message)}. Reload this page from a local web server or GitHub Pages; opening the file directly may block JSON loading.</div>`;
      console.error('Gameplan data load failed:', error);
    }
  }

  document.addEventListener('DOMContentLoaded', init, { once: true });
})();
