from jobwatcher import convert


def test_greenhouse():
    data = {"jobs": [{"id": 1, "title": " Data Analyst ", "location": {"name": "Remote"},
                      "first_published": "2026-11-02T22:30:00-05:00",
                      "absolute_url": "https://x/1"}]}
    r = convert.greenhouse("airbnb", "Airbnb", data)[0]
    assert r["posting_id"] == "airbnb:1" and r["title"] == "Data Analyst"
    assert r["location"] == "Remote" and r["department"] == ""
    assert r["posted_date"] == "2026-11-03"  # converted to UTC
    assert r["url"] == "https://x/1"


def test_lever():
    data = [{"id": "abc", "text": "Analyst", "categories": {"location": "NYC", "department": "Ops"},
             "createdAt": 1792767640768, "hostedUrl": "https://l/abc"}]
    r = convert.lever("spotify", "Spotify", data)[0]
    assert r["posting_id"] == "spotify:abc" and r["department"] == "Ops"
    assert r["location"] == "NYC" and r["posted_date"] == "2026-10-23"


def test_ashby_skips_unlisted():
    data = {"jobs": [
        {"id": "a", "title": "T", "location": "SF", "department": "Eng",
         "publishedAt": "2026-08-24T14:44:49.699+00:00", "jobUrl": "https://a/a"},
        {"id": "b", "title": "Hidden", "isListed": False}]}
    rows = convert.ashby("notion", "Notion", data)
    assert [r["source_id"] for r in rows] == ["a"]
    assert rows[0]["posted_date"] == "2026-08-24"


def test_missing_fields_are_empty():
    r = convert.greenhouse("x", "X", {"jobs": [{"id": 5}]})[0]
    assert r["title"] == "" and r["location"] == "" and r["posted_date"] == ""
