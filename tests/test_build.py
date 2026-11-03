from jobwatcher.build import build_history
from jobwatcher.status import build_status


def gh(*ids):
    return {"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "X"},
                      "absolute_url": f"https://x/{i}"} for i in ids]}


def by_id(rows):
    return {r["source_id"]: r for r in rows}


def test_first_seen_last_seen_and_first_run():
    days = {"2026-01-01": {"airbnb": gh(1, 2)}, "2026-01-02": {"airbnb": gh(1, 2, 3)}}
    r = by_id(build_history(days))
    assert r["1"]["first_run"] and r["1"]["first_seen"] == "2026-01-01"
    assert r["1"]["last_seen"] == "2026-01-02" and r["1"]["status"] == "open"
    assert not r["3"]["first_run"] and r["3"]["first_seen"] == "2026-01-02"


def test_removed_and_relisted():
    days = {"2026-01-01": {"airbnb": gh(1, 2)},
            "2026-01-02": {"airbnb": gh(1)},
            "2026-01-03": {"airbnb": gh(1, 2)}}
    r = by_id(build_history({k: v for k, v in days.items() if k <= "2026-01-02"}))
    assert r["2"]["status"] == "removed" and r["2"]["removed_date"] == "2026-01-02"
    assert r["2"]["last_seen"] == "2026-01-01"
    r = by_id(build_history(days))
    assert r["2"]["status"] == "open" and r["2"]["removed_date"] == ""
    assert r["2"]["first_seen"] == "2026-01-01"


def test_missing_source_file_does_not_remove():
    days = {"2026-01-01": {"airbnb": gh(1), "reddit": gh(9)},
            "2026-01-02": {"reddit": gh(9)}}
    r = build_history(days)
    assert all(x["status"] == "open" for x in r)


def test_rows_sorted_and_deterministic():
    days = {"2026-01-01": {"reddit": gh(2, 1), "airbnb": gh(5)}}
    ids = [r["posting_id"] for r in build_history(days)]
    assert ids == sorted(ids)
    assert build_history(days) == build_history(days)


def test_new_source_later_is_its_own_first_run():
    days = {"2026-01-01": {"airbnb": gh(1)}, "2026-01-02": {"airbnb": gh(1), "reddit": gh(7)}}
    assert by_id(build_history(days))["7"]["first_run"]


def test_status_counts():
    days = {"2026-01-01": {"airbnb": gh(1, 2)}, "2026-01-02": {"airbnb": gh(1, 3)}}
    rows = build_history(days)
    st = build_status(rows, days, [{"name": "Airbnb", "ok": True, "count": 2}], "t")
    assert (st["days_with_success"], st["open"], st["new_today"], st["removed_today"]) == (2, 2, 1, 1)
    assert st["first_run_date"] == "2026-01-01"
