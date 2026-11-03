"""Open (or update) the dated GitHub Issue and close earlier ones.

Usage: uv run python -m jobwatcher.issue   (needs the gh CLI and GH_TOKEN)
"""
import csv
import json
import subprocess

from .build import DATA


def issue_body(rows, status):
    day = status["run_time"][:10]
    new = [r for r in rows if r["first_seen"] == day and r["first_run"] != "true"]
    gone = [r for r in rows if r["removed_date"] == day]

    def lines(rs):
        if not rs:
            return ["_None._"]
        return [f"- [{r['employer']}: {r['title']}]({r['url']})"
                f"{' (' + r['location'] + ')' if r['location'] else ''}"
                for r in sorted(rs, key=lambda r: (r["employer"], r["title"]))]

    failed = [s["name"] for s in status["sources"] if not s["ok"]]
    out = [f"{status['open']} open postings, {len(new)} new, {len(gone)} removed.", ""]
    if failed:
        out += [f"Failed sources: {', '.join(failed)}", ""]
    return "\n".join(out + [f"## New ({len(new)})"] + lines(new) +
                     ["", f"## Removed ({len(gone)})"] + lines(gone))


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main():
    status = json.loads((DATA / "status.json").read_text())
    rows = list(csv.DictReader(open(DATA / "history.csv", encoding="utf-8")))
    day = status["run_time"][:10]
    body = issue_body(rows, status)
    existing = json.loads(gh("issue", "list", "--state", "all", "--search", f"{day} in:title",
                             "--json", "number,title", "--limit", "20"))
    same = [i for i in existing if i["title"] == day]
    if same:  # a second run on the same day updates that day's issue
        number = str(same[0]["number"])
        gh("issue", "edit", number, "--body", body)
        gh("issue", "reopen", number)
    else:
        url = gh("issue", "create", "--title", day, "--body", body).strip()
        number = url.rsplit("/", 1)[-1]
    for i in json.loads(gh("issue", "list", "--state", "open", "--json", "number", "--limit", "100")):
        if str(i["number"]) != number:
            gh("issue", "close", str(i["number"]))
    print(f"issue #{number} for {day}")


if __name__ == "__main__":
    main()
