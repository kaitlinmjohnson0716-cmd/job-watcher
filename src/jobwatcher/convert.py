"""Convert each ATS's raw JSON into the common history columns."""
from datetime import datetime, timezone

COLUMNS = ["posting_id", "source", "source_id", "employer", "title", "location",
           "department", "posted_date", "url"]


def _row(source, employer, source_id, title, location, department, posted_date, url):
    source_id = str(source_id)
    return {
        "posting_id": f"{source}:{source_id}", "source": source, "source_id": source_id,
        "employer": employer, "title": (title or "").strip(),
        "location": (location or "").strip(), "department": (department or "").strip(),
        "posted_date": posted_date or "", "url": url or "",
    }


def _iso_date(value):
    """'2026-11-02T03:52:24-05:00' -> '2026-11-02' (UTC date)."""
    if not value:
        return ""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.date().isoformat()


def _ms_date(ms):
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()


def greenhouse(source, employer, data):
    return [_row(source, employer, j["id"], j.get("title"),
                 (j.get("location") or {}).get("name"), "",
                 _iso_date(j.get("first_published")), j.get("absolute_url"))
            for j in data.get("jobs", [])]


def lever(source, employer, data):
    return [_row(source, employer, j["id"], j.get("text"),
                 (j.get("categories") or {}).get("location"),
                 (j.get("categories") or {}).get("department"),
                 _ms_date(j.get("createdAt")), j.get("hostedUrl"))
            for j in data]


def ashby(source, employer, data):
    return [_row(source, employer, j["id"], j.get("title"), j.get("location"),
                 j.get("department"), _iso_date(j.get("publishedAt")), j.get("jobUrl"))
            for j in data.get("jobs", []) if j.get("isListed", True)]


CONVERTERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby}
