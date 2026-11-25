/* Shared helpers for every page. Reads ../data/site.json (built by scripts/build.py + analyze.py). */
const FREE = {
  data: null,
  async load() {
    if (this.data) return this.data;
    const r = await fetch('data/site.json', {cache: 'no-store'});
    this.data = await r.json();
    return this.data;
  },
  esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); },
  fmtDate(iso) {
    const [y,m,d] = iso.split('-').map(Number);
    return new Date(Date.UTC(y, m-1, d)).toLocaleDateString('en-US',
      {weekday:'short', month:'short', day:'numeric', year:'numeric', timeZone:'UTC'});
  },
  fmtDateShort(iso) {
    const [y,m,d] = iso.split('-').map(Number);
    return new Date(Date.UTC(y, m-1, d)).toLocaleDateString('en-US',
      {month:'short', day:'numeric', timeZone:'UTC'});
  },
  /* "2026-11-25T16:00:00-08:00" -> "4:00 PM" */
  clock(iso) {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', {hour:'numeric', minute:'2-digit', timeZone:'America/Los_Angeles'});
  },
  clockHM(hm) {
    const [h,m] = hm.split(':').map(Number);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const hh = h % 12 === 0 ? 12 : h % 12;
    return `${hh}:${String(m).padStart(2,'0')} ${ampm}`;
  },
  dtype(g) {
    if (g.league === 'MLB') return g.subtype || 'MLB';
    if (g.league === 'NFL') return g.group || 'NFL';
    if (g.league === 'NCAAF') return g.high_side || 'NCAAF';
    if (g.league === 'WWO') return 'Westwood One · ' + (g.subtype || '');
    return g.league;
  },
  sportColor(g) {
    return {MLB:'var(--teal)', NFL:'var(--amber)', NCAAF:'var(--purple)', WWO:'var(--blue)'}[g.league] || 'var(--muted)';
  },
  verifiedPill(g) {
    if (g.verified === 'verified') return '<span class="pill ok">Verified</span>';
    if (g.verified === 'cross-checked') return '<span class="pill cross">Cross-checked</span>';
    if (g.verified === 'estimated') return '<span class="pill est">Estimated</span>';
    if (g.verified === 'unreleased') return '<span class="pill est">Not released</span>';
    return '<span class="pill norm">—</span>';
  },
  priorityPill(g) {
    return g.priority === 'high' ? '<span class="pill hi">High priority</span>'
                                 : '<span class="pill norm">Normal</span>';
  },
  srcLink(g) {
    if (!g.source) return '<span class="mini">—</span>';
    const host = new URL(g.source).hostname.replace('www.','');
    return `<a href="${this.esc(g.source)}" target="_blank" rel="noopener">${this.esc(host)}</a>`;
  },
  /* live clock in Pacific */
  startClock(el) {
    const tick = () => {
      el.textContent = new Date().toLocaleString('en-US',
        {timeZone:'America/Los_Angeles', weekday:'short', month:'short', day:'numeric',
         hour:'numeric', minute:'2-digit'}) + ' PT';
    };
    tick(); setInterval(tick, 30000);
  },
  nav(active) {
    const items = [
      ['index.html','Summary'], ['calendar.html','Calendar'], ['vacation.html','Vacation windows'],
      ['mlb.html','MLB'], ['nfl.html','NFL'], ['ncaaf.html','NCAAF'], ['radio.html','Radio'],
      ['sources.html','Sources'], ['flagged.html','Flagged for review']
    ];
    return items.map(([h,l]) => `<a href="${h}" class="${h===active?'on':''}">${l}</a>`).join('');
  },
  header(active) {
    return `<header class="top"><div class="wrap topbar">
      <div class="brand">FREE TIME <span>VACATION</span></div>
      <nav class="main">${this.nav(active)}</nav>
      <div class="clock" id="clock"></div>
    </div></header>`;
  },
  footer(extra='') {
    return `<footer><div class="wrap">
      <div>Generated from official league/club pages · Pacific Time (PST/PDT) · Outer Sunset, San Francisco 94122</div>
      <div class="mini" style="margin-top:6px">${extra}Estimates are clearly labelled. Nothing is invented: unverified values are blank and listed on the
      <a href="flagged.html">Flagged for review</a> page.</div>
    </div></footer>`;
  }
};
