from jobwatcher.issue import issue_body


def row(pid, **kw):
    base = {"employer": "Acme", "title": pid, "url": f"https://x/{pid}", "location": "",
            "first_seen": "2026-01-01", "first_run": "true", "removed_date": ""}
    return base | kw


def test_issue_lists_new_and_removed_and_ignores_first_run():
    rows = [row("old"), row("new", first_seen="2026-01-02", first_run="false"),
            row("gone", removed_date="2026-01-02")]
    st = {"run_time": "2026-01-02T06:00:00Z", "open": 2, "sources": [
        {"name": "A", "ok": True, "count": 1}, {"name": "B", "ok": False, "count": 0}]}
    body = issue_body(rows, st)
    assert "## New (1)" in body and "[Acme: new](https://x/new)" in body
    assert "## Removed (1)" in body and "[Acme: gone](https://x/gone)" in body
    assert "[Acme: old]" not in body and "Failed sources: B" in body


def test_empty_day_still_has_body():
    st = {"run_time": "2026-01-02T06:00:00Z", "open": 0, "sources": []}
    assert issue_body([], st).count("_None._") == 2
