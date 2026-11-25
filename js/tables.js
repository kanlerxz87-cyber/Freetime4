/* generic filterable, paginated game table */
(function () {
  const cfg = window.TABLE_CONFIG || { years: [2027], sports: ["MLB"] };
  let rows = [], page = 0;
  const PAGE_SIZE = 60;

  const $ = (id) => document.getElementById(id);

  async function load() {
    let all = [];
    for (const y of cfg.years) {
      const d = await loadYear(y);
      all = all.concat(d.games || []);
    }
    rows = all.filter(e => cfg.sports.includes(e.sport) && (cfg.category ? cfg.category(e) : true));
    rows.sort((a, b) => (a.date + (a.time || "") < b.date + (b.time || "")) ? -1 : 1);
    $("count").textContent = `${rows.length.toLocaleString()} entries`;
    render();
  }

  function filtered() {
    const q = ($("q").value || "").toLowerCase().trim();
    const cat = $("cat").value;
    const prio = $("prio").checked;
    const ver = $("veronly").checked;
    return rows.filter(e => {
      if (q && !(e.label || "").toLowerCase().includes(q)) return false;
      if (cat !== "all" && e.category !== cat) return false;
      if (prio && !e.priority) return false;
      if (ver && !e.verified) return false;
      return true;
    });
  }

  function render() {
    const f = filtered();
    const pages = Math.max(1, Math.ceil(f.length / PAGE_SIZE));
    if (page >= pages) page = pages - 1;
    const slice = f.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
    let h = `<table><thead><tr><th>Date</th><th>Time (PST)</th><th>Game / window</th><th>Flags</th><th>Radio</th><th>Source</th></tr></thead><tbody>`;
    for (const e of slice) {
      h += `<tr>
        <td>${esc(e.date)}${e.dateEnd ? " → " + esc(e.dateEnd) : ""}</td>
        <td>${timeCell(e)}</td>
        <td>${esc(e.label)}${e.venue ? `<div class="muted small">${esc(e.venue)}</div>` : ""}</td>
        <td>${e.priority ? '<span class="badge hi">HIGH</span> ' : ""}${e.westwoodOne ? '<span class="badge ww">WW1</span> ' : ""}${verBadge(e)}</td>
        <td class="small">${e.radio ? esc(e.radio) : '<span class="muted">—</span>'}</td>
        <td class="src"><a href="${esc(e.source)}" target="_blank" rel="noopener">source</a></td>
      </tr>`;
    }
    h += "</tbody></table>";
    $("rows").innerHTML = h;

    let p = `<span class="muted small">Page ${page + 1} / ${pages} (${f.length.toLocaleString()} filtered)</span> `;
    p += `<button data-p="${page - 1}" ${page === 0 ? "disabled" : ""}>‹ Prev</button> `;
    for (let i = Math.max(0, page - 2); i <= Math.min(pages - 1, page + 2); i++) {
      p += `<button data-p="${i}" class="${i === page ? "cur" : ""}">${i + 1}</button> `;
    }
    p += `<button data-p="${page + 1}" ${page >= pages - 1 ? "disabled" : ""}>Next ›</button>`;
    $("pager").innerHTML = p;
    $("pager").querySelectorAll("button[data-p]").forEach(b => b.onclick = () => {
      const p2 = Number(b.dataset.p);
      if (p2 >= 0 && p2 < pages) { page = p2; render(); window.scrollTo({ top: 120 }); }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    ["q", "cat", "prio", "veronly"].forEach(id => {
      const el = $(id);
      el.addEventListener("input", () => { page = 0; render(); });
      el.addEventListener("change", () => { page = 0; render(); });
    });
    load();
  });
})();
