"""Build data/status.json describing the latest run."""
import json
from datetime import datetime, timezone


def build_status(rows, days, results, run_time=None):
    """rows: history rows; days: dates with raw files; results: [{name, ok, count}] of latest run."""
    run_time = run_time or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dates = sorted(days)
    latest = dates[-1] if dates else ""
    return {
        "run_time": run_time,
        "first_run_date": dates[0] if dates else "",
        "days_with_success": len(dates),
        "open": sum(r["status"] == "open" for r in rows),
        "new_today": sum(r["first_seen"] == latest and not r["first_run"] for r in rows),
        "removed_today": sum(r["removed_date"] == latest for r in rows),
        "sources": results,
    }


def write_status(status, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2)
        fh.write("\n")
