# Free Time Vacation

Static, GitHub Pages-ready dashboard for planning Bay Area vacations around live sports that may be heard on AM/FM radio. The dashboard has day navigation, schedule coverage, official source links, a vacation-horizon overview, and a clearly labeled review register.

## Accuracy / current limits

This first implementation does **not** contain a complete verified game feed. It intentionally shows “not enough verified data” rather than translating missing rows into a no-games/free determination. The only year-specific announcement summarized in the dashboard is MLB's official 2027 regular-season schedule announcement (linked in the site). No made-up 2028/2029 matchups, kickoff times, game lengths, or radio station airings are included.

See [Flagged for Review](#) on the site for gaps and caveats. Every competition row links to the relevant official schedule or broadcaster. Radio carriage and reception in San Francisco's Outer Sunset must be checked independently from league schedules.

## Publish with GitHub Pages

The repository is a plain static site. In GitHub, open **Settings → Pages**, select **Deploy from a branch**, choose `main` and `/ (root)`, then save. No build step is required. If publishing via Actions, deploy the repository root as the Pages artifact.

## Files

- `index.html` — dashboard, status tables, sources, and review register
- `styles.css` — responsive dashboard styles
- `app.js` — date navigation (does not invent events)
- `COORDINATION.md` — shared task board and verification log
