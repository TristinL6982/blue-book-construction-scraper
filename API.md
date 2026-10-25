# Dodge / construction.com — Public "Projects for Bid" API Reference

Documented from the Angular client of <https://www.construction.com/projects/>
(bundle `main-es2015.142b77f5a350ad100e1f.js`, October 2026).

> Public endpoint, no authentication, no API key. JSON over HTTPS.
> This is **their** API — see the [README disclaimer](README.md#disclaimer) and
> [Responsible Use](README.md#responsible-use).

---

## 1. Search (list) endpoint

```
GET https://www.construction.com/api/1.0/search/public/projects/search
```

### Query parameters

| Parameter | Type | Notes |
|---|---|---|
| `page` | int (0-based) | Page number. Omit or `0` for the first page. |
| `hitsPerPage` | int | **Max 20.** Values above 20 → `400 Bad Request`. Default 20. |
| `query` | string | Free-text search (project name, etc.) |
| `trade` | string | Trade facet filter (e.g. `Pipeline Contractors`) |
| `projectType` | string, repeatable | e.g. `Storm Sewer`, `Paving`, `Water Line` |
| `actionStage` | string, repeatable | Project stage, e.g. `Bidding` |
| `published` | string, repeatable | Publication period filter |
| `state` | string, repeatable | 2-letter US state, e.g. `TX`, `OH` |
| `county` | string, repeatable | County name, e.g. `DOUGLAS` |
| `country` | string, repeatable | e.g. `USA` |
| `City` | string | City name (note the capital **C**) |
| `country`/`state`/`county` as empty | — | Empty/blank values are ignored by the server |

### Example

```
GET https://www.construction.com/api/1.0/search/public/projects/search?page=0&hitsPerPage=20&state=TX&projectType=Storm+Sewer
```

### Response envelope

```jsonc
{
  "nbHits": 31220,        // total matching projects
  "page": 0,              // echoed page
  "hitsPerPage": 20,      // echoed page size
  "nbPages": 1561,        // total pages
  "hits": [ /* project objects, see below */ ],
  "facets": {             // available facet values + counts
    "pcountryid_exact": {...},
    "pstateid_exact": {...},
    "pcountyname_exact": {...},
    "stage_exact": {...},
    "projtype_exact": {...}
  },
  "sisterLinks": {        // filter option lists (names + slugs)
    "states":  [...],     // 65 entries
    "counties":[...],
    "trades":  [...],     // 100 entries
    "projectTypes": [...] // 100 entries
  }
}
```

### Hit (project) object

| Field | Type | Example | Notes |
|---|---|---|---|
| `dr` | string | `"202600428478"` | Project ID — key for the detail endpoint |
| `projectName` | string | `"16' Large Valve Replacements"` | |
| `actionStage` | string | `"Bidding"` | |
| `projectType` | string | `"Water Line"` | |
| `valuation` | string | `"$1,000,000 ~ $2,999,999"` | Valuation band |
| `city` / `county` / `state` / `country` | string | `OMAHA / DOUGLAS / NE / USA` | Uppercase |
| `publishDate` | ISO 8601 | `"2026-10-24T00:00:00Z"` | Date the project was published |
| `bidDate` | ISO 8601 | `"2026-11-12T00:00:00Z"` | Bid opening date |
| `bidTimestampText` | string | `""` | Sometimes carries an explicit time |
| `targetBidDate` | string | `""` | Occasionally populated |
| `statusText` | string[] | `["Bids to Owner Public - Local November 12 at 02:00 PM (CST)"]` | **Human-readable bid instructions incl. exact time + time zone** |
| `addressLine1` / `addressLine2` | string | `"various locations"` | |
| `trades` | string[] | `["Pipeline Contractors", "Concrete Pipe", …] | All trades/contracts associated with the project (DBE/WBE variants included) |
| `itemCategory` | string[] | `[]` | |
| `ownerType` | string[] | `["Local Government"]` | e.g. Local Government, State Government, Utility |
| `reportType` | string | `"Project"` | |
| `lastUpdated` | ISO 8601 | `"2026-10-23T00:00:00Z"` | |

### Pagination behaviour

- Page size is hard-capped at **20** — full dataset export is `nbPages` sequential requests
  (≈1561 requests for the ~31k-project default feed; ≈15–20 minutes at 0.7 s spacing).
- Pages can drift when new projects are published mid-export; dedupe by `dr`.

---

## 2. Detail endpoint

```
GET https://www.construction.com/api/1.0/search/public/project/{dr}
```

`{dr}` = project ID from a search hit. Returns `{"hits": [ <same project object> ]}`
(the listing's fields; no additional private fields are exposed publicly).

```
GET https://www.construction.com/api/1.0/search/public/project/202600428478
```

---

## 3. Discovering current filter values

The `sisterLinks` block in any search response carries the current lists of
states, counties, trades, and project types, so scripts can adapt to whatever
the site currently supports without hard-coding values.
