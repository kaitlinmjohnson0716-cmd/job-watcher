"""Fetch raw JSON from each applicant tracking system (no login, JSON only)."""
import requests

URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


def fetch(ats, slug, timeout=60):
    resp = requests.get(URLS[ats].format(slug=slug), timeout=timeout,
                        headers={"User-Agent": "job-watcher/0.1 (course project)"})
    resp.raise_for_status()
    return resp.json()
