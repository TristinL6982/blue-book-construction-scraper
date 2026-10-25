#!/usr/bin/env python3
"""Fetch Dodge (construction.com) public "Projects for Bid" data.

The /projects/ page is an Angular SPA — all content is fetched at runtime
from a public JSON API (no auth, no API key):

  Search (list):  https://www.construction.com/api/1.0/search/public/projects/search
      GET params: query, trade, page (0-based), hitsPerPage (max 20),
                  country, state, actionStage, published, projectType,
                  county, City
  Detail:         https://www.construction.com/api/1.0/search/public/project/{dr}

Example:
  python fetch_all_projects.py                     # full export (31k+ projects)
  python fetch_all_projects.py --state TEXAS --project-type "Storm Sewer"
  python fetch_all_projects.py --pages 5           # first 5 pages only
  python fetch_all_projects.py --query "bridge" --out bridges.csv
"""
import argparse, csv, json, sys, time, urllib.parse, urllib.request

BASE = "https://www.construction.com/api/1.0/search/public/projects/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
COLS = ["dr", "projectName", "actionStage", "projectType", "valuation",
        "city", "county", "state", "country", "publishDate", "bidDate",
        "addressLine1", "addressLine2", "statusText", "ownerType", "trades"]


def get(url, tries=4):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(2 * (a + 1))
    raise SystemExit(f"GET failed after {tries} tries: {url} ({last})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dodge_projects_all.csv")
    ap.add_argument("--pages", type=int, default=0, help="0 = all pages")
    ap.add_argument("--delay", type=float, default=0.7, help="seconds between requests")
    ap.add_argument("--query")
    ap.add_argument("--trade")
    ap.add_argument("--state", action="append", default=[])
    ap.add_argument("--county", action="append", default=[])
    ap.add_argument("--country", action="append", default=[])
    ap.add_argument("--city")
    ap.add_argument("--project-type", action="append", default=[])
    ap.add_argument("--action-stage", action="append", default=[])
    ap.add_argument("--published", action="append", default=[])
    a = ap.parse_args()
    global page

    params = {"page": 0, "hitsPerPage": 20}
    if a.query: params["query"] = a.query
    if a.trade: params["trade"] = a.trade
    if a.city: params["City"] = a.city
    for k, v in (("country", a.country), ("state", a.state), ("county", a.county),
                 ("projectType", a.project_type), ("actionStage", a.action_stage),
                 ("published", a.published)):
        if v: params[k] = v

    seen, rows, nb_hits = set(), [], None
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        while True:
            params["page"] = page
            url = BASE + "?" + urllib.parse.urlencode(params, doseq=True)
            d = get(url)
            hits = d.get("hits") or []
            if nb_hits is None:
                nb_hits = d.get("nbHits", 0)
                nb_pages = d.get("nbPages", 0)
                limit = nb_pages if not a.pages else min(a.pages, nb_pages)
                print(f"nbHits={nb_hits} nbPages={nb_pages} limit={limit} -> {a.out}", file=sys.stderr)
            if not hits:
                break
            new = [h for h in hits if h.get("dr") not in seen]
            for h in new:
                h["statusText"] = " | ".join(h.get("statusText") or [])
                h["ownerType"] = ", ".join(h.get("ownerType") or [])
                h["trades"] = ", ".join(h.get("trades") or [])
                seen.add(h["dr"])
                w.writerow(h)
            rows += new
            print(f"  page {page}: {len(new)} new ({len(seen)}/{nb_hits})", file=sys.stderr)
            page += 1
            if page >= limit:
                break
            time.sleep(a.delay)
    print(f"Done: {len(seen)} unique projects written to {a.out}", file=sys.stderr)


if __name__ == "__main__":
    page = 0
    main()
