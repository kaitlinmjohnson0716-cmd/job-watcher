"""Build data/history.csv from the raw files alone (deterministic).

Usage: uv run python -m jobwatcher.build
"""
import csv
import gzip
import json
from pathlib import Path

from .convert import CONVERTERS
from .rules import in_role
from .sources import SOURCES

DATA = Path(__file__).resolve().parents[2] / "data"
HISTORY_COLUMNS = ["posting_id", "source", "source_id", "employer", "title", "location",
                   "department", "posted_date", "url", "in_role", "first_run",
                   "first_seen", "last_seen", "status", "removed_date"]
BY_SLUG = {slug: (name, ats) for name, ats, slug in SOURCES}


def load_days(raw_dir):
    """{date: {slug: parsed json}} for every raw file present."""
    days = {}
    for day_dir in sorted(p for p in Path(raw_dir).iterdir() if p.is_dir()):
        for f in sorted(day_dir.glob("*.json.gz")):
            slug = f.name[: -len(".json.gz")]
            with gzip.open(f, "rt", encoding="utf-8") as fh:
                days.setdefault(day_dir.name, {})[slug] = json.load(fh)
    return days


def build_history(days):
    """days: {date: {slug: raw json}} -> list of history rows sorted by posting_id."""
    hist = {}
    seen_sources = set()
    for date in sorted(days):
        for slug, raw in sorted(days[date].items()):
            employer, ats = BY_SLUG[slug]
            rows = CONVERTERS[ats](slug, employer, raw)
            first_run = slug not in seen_sources
            seen_sources.add(slug)
            listed = set()
            for r in rows:
                pid = r["posting_id"]
                listed.add(pid)
                h = hist.get(pid)
                if h is None:
                    h = hist[pid] = {"first_run": first_run, "first_seen": date}
                h.update(r)
                h.update(in_role=in_role(r["title"]), last_seen=date,
                         status="open", removed_date="")
            for pid, h in hist.items():
                if h["source"] == slug and pid not in listed and h["status"] == "open":
                    h["status"] = "removed"
                    h["removed_date"] = date
    return [hist[k] for k in sorted(hist)]


def write_history(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, HISTORY_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            out = dict(r)
            out["in_role"] = str(r["in_role"]).lower()
            out["first_run"] = str(r["first_run"]).lower()
            w.writerow({c: out[c] for c in HISTORY_COLUMNS})


def main():
    rows = build_history(load_days(DATA / "raw"))
    write_history(rows, DATA / "history.csv")
    print(f"wrote {len(rows)} rows to data/history.csv")


if __name__ == "__main__":
    main()
