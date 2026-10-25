# 📘 The Blue Book — Building & Construction Bid Scraper

Open-source client + documentation for the **public, unauthenticated JSON API** that powers the
["Construction Projects for Bid"](https://www.construction.com/projects/) page on
[construction.com](https://www.construction.com) (Dodge / Dodge Data & Analytics).

The web page is an Angular SPA — none of the project data is present in the HTML. It all comes from
a plain JSON endpoint that requires **no API key and no login**. This repo documents that endpoint
and ships a battle-tested Python CLI to search, filter, and bulk-export it.

> [!IMPORTANT]
> **This repository does not host the API and does not host any data.** It is a client and
> reference documentation for an endpoint operated by construction.com. All project data is
> © Dodge Data & Analytics (S&P Global). Use this tool in a way that complies with
> [construction.com's Terms of Service](https://www.construction.com), and see
> [Responsible Use](#responsible-use) below.

---

## Why this exists

Most construction bid data (Dodge, ENR, Construction Week, BidNet…) is behind a paid subscription.
The *listing* data for projects currently for bid, however, is already delivered in the open to
every browser that loads the public page — the "censoring" is just client-side rendering.
The Blue Book simply points you at the JSON behind it, and gives you a polite, resumable way to
export it.

## Contents

| Path | What it is |
|---|---|
| [`fetch_all_projects.py`](fetch_all_projects.py) | Stdlib-only Python CLI: search, filter, and bulk-export projects to CSV |
| [`examples/sample_search_response.json`](examples/sample_search_response.json) | Real (trimmed) API response for reference |
| [`API.md`](API.md) | Full endpoint reference: parameters, response schema, filter values |

## Quick start

No dependencies — Python 3.8+, standard library only.

```bash
# Single page of results (20 most recent projects currently for bid)
curl 'https://www.construction.com/api/1.0/search/public/projects/search?page=0&hitsPerPage=20'

# Full export (~31k projects, ~1561 pages, ≈15–20 min at the default polite pace)
python fetch_all_projects.py

# Filtered exports
python fetch_all_projects.py --state TEXAS
python fetch_all_projects.py --project-type "Storm Sewer" --action-stage Bidding
python fetch_all_projects.py --query bridge --out bridges.csv
python fetch_all_projects.py --state OHIO --city COLUMBUS --out cleveland-area.csv
```

Each row in the output CSV contains:

`dr` (project ID) · `projectName` · `actionStage` · `projectType` · `valuation` ·
`city` · `county` · `state` · `country` · `publishDate` · `bidDate` ·
`addressLine1` · `addressLine2` · `statusText` (incl. exact bid open date/time + time zone) ·
`ownerType` · `trades` (full trade list)

See [API.md](API.md) for the complete field-by-field schema and every supported query parameter.

## CLI reference

```
python fetch_all_projects.py [--out FILE] [--pages N] [--delay SECONDS]
                             [--query TEXT] [--trade TEXT] [--city TEXT]
                             [--state S ...] [--county C ...] [--country C ...]
                             [--project-type T ...] [--action-stage A ...]
                             [--published P ...]
```

| Flag | Description |
|---|---|
| `--out` | Output CSV (default `dodge_projects_all.csv`) |
| `--pages` | Export only the first N pages (0 = all) |
| `--delay` | Seconds between requests (default `0.7`; don't lower it) |
| `--query` | Free-text search (project name, etc.) |
| `--trade` / `--project-type` / `--action-stage` / `--published` | Facet filters; repeatable |
| `--state` / `--county` / `--country` / `--city` | Geographic filters; repeatable |

Built-in: retries with exponential backoff (4 attempts), dedup by project ID, progress to stderr.

## Responsible use

- **You are sending real requests to a real production server.** The client defaults to one
  request per ~0.7 s. Do not crank it up, do not run parallel workers, do not hammer the endpoint.
- Cache results; don't re-pull everything every hour.
- Respect `429`/`5xx` responses — the client backs off, keep it that way.
- The data is public for the website's own use; systematic bulk extraction may be covered by
  construction.com's Terms of Service. Review them and accept responsibility for your own use.
  The maintainers of this repo accept no liability for how third parties use it.
- Attribution is appreciated: this data comes from Dodge's public listing feed.

## License

MIT — see [LICENSE](LICENSE). The license covers this code and documentation only.
All construction project data remains the property of its source.

## Disclaimer

Not affiliated with, endorsed by, or connected to construction.com, Dodge, or S&P Global.
Use at your own risk.
