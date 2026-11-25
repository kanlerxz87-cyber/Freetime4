// Verifies every source ID referenced in docs/data resolves to sources.json, and every JSON file parses.
const fs = require("fs"), path = require("path");
const dir = path.join(__dirname, "../docs/data");
const sources = JSON.parse(fs.readFileSync(path.join(dir, "sources.json"), "utf8")).sources.map(s => s.id);
const ids = new Set(sources);
const bad = [];
function walk(v, file, p) {
  if (Array.isArray(v)) v.forEach((x, i) => walk(x, file, p + "[" + i + "]"));
  else if (v && typeof v === "object") Object.keys(v).forEach(k => {
    if (/^(source|sources|secondary_source|corroboration|nfl_com_source|source_override)$/.test(k)) {
      const vals = Array.isArray(v[k]) ? v[k] : [v[k]];
      vals.forEach(x => { if (typeof x === "string" && /^S-/.test(x) && !ids.has(x)) bad.push(file + " " + p + "." + k + " -> " + x); });
    }
    walk(v[k], file, p + "." + k);
  });
}
const files = fs.readdirSync(dir).filter(f => f.endsWith(".json"));
for (const f of files) { const j = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); walk(j, f, ""); }
// also check ids used directly in arrays named sources / source ids in vacation windows and flags
for (const f of ["vacation-windows.json", "flags.json"]) {
  const j = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
  (j.windows || j.flags || []).forEach(x => (x.sources || []).forEach(s => { if (!ids.has(s)) bad.push(f + " " + x.id + " -> " + s); }));
}
// Each referenced ID must resolve; list unused sources for information.
if (bad.length) { console.log("UNRESOLVED:\n" + bad.join("\n")); process.exit(1); }
console.log("all source IDs resolve;", ids.size, "sources;", files.length, "json files parse");
