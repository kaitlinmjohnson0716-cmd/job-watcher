"""Daily pipeline: fetch every source, save raw files, rebuild history and status.

Usage: uv run python -m jobwatcher.run
"""
import gzip
import json
import shutil
from datetime import datetime, timezone

from . import build, status
from .fetch import fetch
from .sources import SOURCES

DATA = build.DATA


def fetch_all(day_dir, fetcher=fetch):
    """Save each source's JSON; a failing source writes no file. Returns per-source results."""
    results = []
    for name, ats, slug in SOURCES:
        try:
            raw = fetcher(ats, slug)
            with gzip.open(day_dir / f"{slug}.json.gz", "wt", encoding="utf-8") as fh:
                json.dump(raw, fh)
            count = len(raw if isinstance(raw, list) else raw.get("jobs", []))
            results.append({"name": name, "ok": True, "count": count})
        except Exception as exc:  # one source failing must not stop the run
            print(f"FAILED {name}: {exc}")
            results.append({"name": name, "ok": False, "count": 0})
    return results


def main():
    now = datetime.now(timezone.utc)
    day_dir = DATA / "raw" / now.strftime("%Y-%m-%d")
    if day_dir.exists():  # a second run on the same day replaces that day's files
        shutil.rmtree(day_dir)
    day_dir.mkdir(parents=True)
    results = fetch_all(day_dir)
    (day_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    days = build.load_days(DATA / "raw")
    rows = build.build_history(days)
    build.write_history(rows, DATA / "history.csv")
    st = status.build_status(rows, days, results, now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    status.write_status(st, DATA / "status.json")
    print(f"{st['open']} open, {st['new_today']} new, {st['removed_today']} removed; "
          f"{sum(r['ok'] for r in results)}/{len(results)} sources ok")


if __name__ == "__main__":
    main()
