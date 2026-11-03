# Job Watcher

![tests](https://github.com/kaitlinmjohnson0716-cmd/job-watcher/actions/workflows/tests.yml/badge.svg)

Watches open **Marketing Data Analyst** roles. Every day GitHub Actions pulls the job boards of 22 employers, compares them with the day before, records what is new and what is gone, opens a GitHub Issue, and publishes the result to a GitHub Pages site.

## Build the history from the raw files

```
uv run python -m jobwatcher.build
```

`data/history.csv` depends only on `data/raw/`, so this reproduces the same file and any rule change applies to every day.
Daily run (fetch, build, status): `uv run python -m jobwatcher.run`. Tests: `uv run pytest`.

## Title rule

A posting is **in role** when its title contains an analysis word (`analyst`, `analytics`, `insight(s)`, `measurement`, `data scientist`) **and** a marketing word (`marketing`, `growth`, `acquisition`, `lifecycle`, `campaign(s)`, `brand`, `crm`, `martech`, `advertising`, `demand gen(eration)`, `customer analytics`, `digital`, `seo`, `sem`). Whole words, case-insensitive. Every posting is kept; the rule only sets `in_role`.

## Sources (all return JSON with no login; none exceeds 5,000 postings, so no search term is used)

| Employer | ATS | Board |
|---|---|---|
| Airbnb, Pinterest, Reddit, Instacart, Duolingo, Lyft, Braze, Sprout Social, Squarespace, Peloton, Twilio, Datadog, Asana, Figma, Discord, Stripe | Greenhouse | `boards-api.greenhouse.io/v1/boards/<slug>/jobs` |
| Spotify, Palantir | Lever | `api.lever.co/v0/postings/<slug>?mode=json` |
| Notion, Ramp, OpenAI, Snowflake | Ashby | `api.ashbyhq.com/posting-api/job-board/<slug>` |

## Files

| Path | What it does |
|---|---|
| `src/jobwatcher/sources.py` | The watch list: employer, ATS, board slug |
| `src/jobwatcher/fetch.py` | Requests one board's JSON |
| `src/jobwatcher/convert.py` | Converts each ATS's JSON to the common columns |
| `src/jobwatcher/rules.py` | The title rule (`in_role`) |
| `src/jobwatcher/build.py` | Builds `data/history.csv` from the raw files |
| `src/jobwatcher/status.py` | Builds `data/status.json` |
| `src/jobwatcher/run.py` | Daily pipeline: fetch, save raw, build, status |
| `src/jobwatcher/issue.py` | Opens or updates the dated Issue and closes earlier ones |
| `tests/` | pytest suite: converters, title rule, history logic, issue text |
| `.github/workflows/daily.yml` | Daily run, Issue, and commit of the data |
| `.github/workflows/tests.yml` | Runs pytest on every push |
| `data/raw/<date>/<source>.json.gz` | Raw board responses; `results.json` records every source's result |
| `data/history.csv` | One row per posting (first seen, last seen, status, removed date) |
| `data/status.json` | Latest run: time, counts, per-source status |
| `index.html` | Today page: last run, source status, counts, new and removed |
| `browse.html` | Browse page: filters, search, sort, apply links, starred shortlist |
| `market.html`, `market.js` | Market page: six findings computed in the browser from the history |
| `app.js`, `style.css` | Shared navigation, data loading, charts, fonts and colors |
| `manifest.webmanifest`, `sw.js`, `icon*` | Installable app and offline support |

## Notes

- A source that fails writes no raw file that day and is recorded as failed; the run still commits.
- A second run on the same day replaces that day's raw files and updates that day's Issue.
- Greenhouse's list endpoint gives no department, so `department` is empty for those rows.
