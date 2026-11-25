// Generates the static HTML shells in docs/. All content is rendered client-side from docs/data by docs/assets/app.js.
const fs = require("fs"), path = require("path");
const out = path.join(__dirname, "../docs");
const nav = [["scoreboard.html", "Scoreboard"], ["mlb.html", "MLB"], ["nfl.html", "NFL"], ["ncaaf.html", "College"], ["radio.html", "Radio"], ["vacation.html", "Vacation"], ["flagged.html", "Flagged for Review"], ["sources.html", "Sources"]];
const pages = [
  ["index.html", "index", "Freetime Planner - Outer Sunset, SF 94122"],
  ["scoreboard.html", "scoreboard", "Scoreboard (day view)"],
  ["mlb.html", "mlb", "MLB (30 clubs)"],
  ["nfl.html", "nfl", "NFL and Westwood One"],
  ["ncaaf.html", "ncaaf", "College (Stanford, Cal)"],
  ["radio.html", "radio", "Radio stations"],
  ["vacation.html", "vacation", "Vacation windows"],
  ["flagged.html", "flagged", "Flagged for Review"],
  ["sources.html", "sources", "Sources"]
];
for (const [file, id, title] of pages) {
  const links = nav.map(([href, label]) => `<a href="${href}">${label}</a>`).join("");
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title} · Freetime Planner</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="${id}">
<header><a href="index.html">Freetime Planner · SF 94122</a><nav>${links}</nav></header>
<main id="main"><h1>${title}</h1></main>
<footer>Times are Pacific. Official sources linked on every row. Last checked 2026-11-25. Unverified values are blank and flagged.</footer>
<script src="assets/app.js"></script>
</body>
</html>
`;
  fs.writeFileSync(path.join(out, file), html);
}
console.log("wrote", pages.length, "pages");
