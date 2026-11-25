// Checks: every page and asset referenced exists; every relative href/src resolves; every JSON used by the app parses.
const fs = require("fs"), path = require("path");
const docs = path.join(__dirname, "../verified");
let errors = [];
const htmls = fs.readdirSync(docs).filter(f => f.endsWith(".html"));
for (const f of htmls) {
  const html = fs.readFileSync(path.join(docs, f), "utf8");
  const refs = [...html.matchAll(/(?:href|src)="([^"]+)"/g)].map(m => m[1]).filter(r => !/^(https?:|#|mailto:)/.test(r));
  for (const r of refs) { const p = path.join(docs, r.split("?")[0]); if (!fs.existsSync(p)) errors.push(f + " -> missing " + r); }
}
// data JSON used by app.js
const appjs = fs.readFileSync(path.join(docs, "assets/app.js"), "utf8");
const dataRefs = new Set([...appjs.matchAll(/"(data\/[^"]+\.json)"/g)].map(m => m[1]).concat([...appjs.matchAll(/base \+ "(data\/[^"]+\.json)"/g)].map(m => m[1])));
for (const r of dataRefs) { const p = path.join(docs, r); if (!fs.existsSync(p)) errors.push("app.js -> missing " + r); else { try { JSON.parse(fs.readFileSync(p, "utf8")); } catch (e) { errors.push(r + " invalid JSON: " + e.message); } } }
// raw files
for (const r of ["data/raw/mlb-teams.json", "data/raw/mlb-seasons-2026.json", "data/raw/mlb-seasons-2027.json", "data/raw/mlb-2027-giants-daily.json", "data/raw/mlb-2027-athletics-daily.json", "data/raw/mlb-2027-regular-season-daily.json", "data/raw/mlb-2027-spring-training-daily.json"]) {
  const p = path.join(docs, r); if (!fs.existsSync(p)) errors.push("missing " + r); else JSON.parse(fs.readFileSync(p, "utf8"));
}
if (errors.length) { console.log("ERRORS:\n" + errors.join("\n")); process.exit(1); }
console.log("site check ok:", htmls.length, "pages, all local links and data files resolve");
