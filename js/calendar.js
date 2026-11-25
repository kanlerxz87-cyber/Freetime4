/* calendar / scoreboard day view */
(function () {
  const params = new URLSearchParams(location.search);
  let iso = (location.hash || "").replace("#", "") || params.get("date") || "";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const now = new Date().toISOString().slice(0, 10);
    iso = (now >= "2026-11-25" && now <= "2029-12-31") ? now : "2026-11-25";
  }
  let scenario = "core";

  const $ = (id) => document.getElementById(id);

  async function gamesFor(iso) {
    const y = iso.slice(0, 4);
    const prev = String(Number(y) - 1);
    const a = await loadYear(y);
    const b = await loadYear(prev);
    return [...(a.games || []), ...(b.games || [])];
  }

  function renderBar(blocks) {
    const bar = $("freebar");
    bar.innerHTML = "";
    for (const b of blocks) {
      const seg = document.createElement("div");
      seg.className = b.type === "free" ? "seg-free" : "seg-busy";
      seg.style.flex = String(Math.max(0.2, b.to - b.from));
      seg.title = `${b.type === "free" ? "FREE" : "BUSY"} ${fmtTime(b.from)}–${fmtTime(b.to)} PST`;
      bar.appendChild(seg);
    }
  }

  function groupLabel(e) {
    const map = { MLB: "MLB Baseball", NFL: "NFL Football", NCAAF: "College Football (Stanford / Cal)" };
    return map[e.sport] || e.sport;
  }

  async function render() {
    $("dateBig").textContent = isoPretty(iso) + "  ·  PST";
    const games = await gamesFor(iso);
    const events = dayEvents(games, iso, scenario).sort((a, b) =>
      (a.time || "00:00") < (b.time || "00:00") ? -1 : 1);
    const { blocks, merged, warns } = freeBlocks(events);
    renderBar(blocks);

    // free blocks summary
    const freeList = blocks.filter(b => b.type === "free" && (b.to - b.from) >= 30);
    const busyList = merged;
    let html = "";
    if (busyList.length === 0 && warns.length === 0) {
      html += `<div class="goodbox"><b>ALL DAY FREE — no scheduled games under this scenario.</b> Nothing on the radio, nothing scheduled to be played.</div>`;
    }
    html += `<h3>Free time blocks (PST)</h3>`;
    if (freeList.length === 0) html += `<div class="blockrow busy">No free block ≥ 30 minutes under this scenario.</div>`;
    for (const b of freeList) {
      html += `<div class="blockrow free"><span><b>FREE</b> — do anything</span><span>${fmtTime(b.from)} – ${fmtTime(b.to)} PST</span></div>`;
    }
    for (const e of warns) {
      html += `<div class="blockrow warn"><span>⚠ <b>${esc(e.label)}</b> — possible/uncertain event (not counted as busy)</span><span>${e.dateEnd ? e.date + " → " + e.dateEnd : e.time || ""}</span></div>`;
    }
    const provisional = events.filter(e => e.timeEstimated && e.blocking !== false);
    if (provisional.length) {
      html += `<div class="flagbox">⚠ <b>Provisional blocks:</b> ${provisional.length} entr${provisional.length > 1 ? "ies" : "y"} on this day have estimated start times (official times TBD). Free blocks may shift once times are confirmed.</div>`;
    }
    $("blocks").innerHTML = html;

    // game list
    if (events.length === 0) {
      $("games").innerHTML = `<div class="goodbox">No games in the dataset for this date. This is a free day for AM/FM sports radio in San Francisco.</div>`;
    } else {
      const byLeague = {};
      for (const e of events) {
        const k = groupLabel(e);
        (byLeague[k] = byLeague[k] || []).push(e);
      }
      let g = "";
      for (const [league, list] of Object.entries(byLeague)) {
        g += `<h3>${esc(league)} <span class="muted small">(${list.length} entr${list.length > 1 ? "ies" : "y"})</span></h3><table><thead><tr>
          <th>Time (PST)</th><th>Game / window</th><th>Flags</th><th>Radio (SF Bay Area AM/FM)</th><th>Source</th></tr></thead><tbody>`;
        for (const e of list) {
          g += `<tr>
            <td>${timeCell(e)}</td>
            <td>${esc(e.label)}${e.blocking === false ? ' <span class="badge est">possible</span>' : ""}${e.category === "spring" ? ' <span class="badge est">spring training</span>' : ""}${e.category === "postseason" ? ' <span class="badge busy">postseason</span>' : ""}</td>
            <td>${e.priority ? '<span class="badge hi">HIGH PRIORITY</span> ' : ""}${e.westwoodOne ? '<span class="badge ww">Westwood One</span> ' : ""}${verBadge(e)}</td>
            <td>${e.radio ? esc(e.radio) : '<span class="muted">not carried on SF AM/FM (or unconfirmed)</span>'}</td>
            <td class="src"><a href="${esc(e.source)}" target="_blank" rel="noopener">official source</a></td>
          </tr>`;
        }
        g += "</tbody></table>";
      }
      $("games").innerHTML = g;
    }
  }

  function go(delta) { iso = isoAdd(iso, delta); location.hash = iso; render(); }

  document.addEventListener("DOMContentLoaded", () => {
    $("prev").onclick = () => go(-1);
    $("next").onclick = () => go(1);
    $("today").onclick = () => {
      const now = new Date().toISOString().slice(0, 10);
      iso = (now >= "2026-11-25" && now <= "2029-12-31") ? now : "2026-11-25";
      location.hash = iso; render();
    };
    $("datepick").value = iso;
    $("datepick").onchange = (e) => { iso = e.target.value; location.hash = iso; render(); };
    $("scenario").onchange = (e) => { scenario = e.target.value; render(); };
    window.addEventListener("hashchange", () => {
      const h = location.hash.replace("#", "");
      if (/^\d{4}-\d{2}-\d{2}$/.test(h) && h !== iso) { iso = h; $("datepick").value = iso; render(); }
    });
    render();
  });
})();
