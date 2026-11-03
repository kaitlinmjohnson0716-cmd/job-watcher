// Every number here is computed in the browser from data/history.csv.
function median(a) {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
function countBy(list, key) {
  const m = new Map(); list.forEach(r => m.set(key(r), (m.get(key(r)) || 0) + 1)); return m;
}
function section(h, p, chart) { return `<h2>${h}</h2><p>${p}</p>${chart}`; }

(async () => {
  let rows;
  try { rows = await loadHistory(); } catch (e) { document.getElementById("intro").innerHTML = '<span class="err">Could not load data.</span>'; return; }
  const last = lastRunDate(rows), lastN = dayNum(last);
  const first = rows.reduce((m, r) => r.first_seen < m ? r.first_seen : m, last);
  const days = []; for (let n = dayNum(first); n <= lastN; n++) days.push(dayStr(n));
  const open = rows.filter(r => r.status === "open");
  const nonFirst = rows.filter(r => !r.first_run);
  document.getElementById("intro").textContent = `${rows.length} postings tracked from ${first} to ${last}. Postings already open when a source was first read are left out of the new-posting and days-open measures.`;
  const out = [];

  // 1. New postings per day
  const newAll = countBy(nonFirst, r => r.first_seen), newRole = countBy(nonFirst.filter(r => r.in_role), r => r.first_seen);
  const tAll = nonFirst.length, tRole = nonFirst.filter(r => r.in_role).length;
  out.push(section(`${tAll} new postings so far, ${tRole} in my role`,
    `Postings first seen on each day after a source's first read. In-role postings use the title rule (analysis word plus marketing word).`,
    barChart(days, [{name: "All postings", cls: "bar", values: days.map(d => newAll.get(d) || 0)},
                    {name: "In my role", cls: "bar2", values: days.map(d => newRole.get(d) || 0)}], {label: "New postings per day"})));

  // 2. Removed per day
  const removed = rows.filter(r => r.removed_date), rm = countBy(removed, r => r.removed_date);
  out.push(section(`${removed.length} postings removed so far`,
    `Postings whose source stopped listing them, counted on the day the removal was seen.`,
    barChart(days, [{name: "Removed", cls: "bar3", values: days.map(d => rm.get(d) || 0)}], {label: "Removed postings per day"})));

  // 3. Open per employer
  const emp = [...countBy(open, r => r.employer)].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  out.push(section(emp.length ? `${emp[0][0]} has the most open postings (${emp[0][1]})` : "No open postings",
    `Open postings per employer as of ${last}, ${open.length} in total.`,
    barChart(emp.map(e => e[0]), [{name: "Open", cls: "bar", values: emp.map(e => e[1])}], {label: "Open postings per employer", rotate: 50})));

  // 4. Days open (median)
  const dOpen = nonFirst.filter(r => r.removed_date).map(r => dayNum(r.removed_date) - dayNum(r.first_seen));
  const med = median(dOpen);
  const buckets = ["0-1", "2-3", "4-7", "8-14", "15-30", "31+"], lim = [1, 3, 7, 14, 30, Infinity];
  const bc = buckets.map(() => 0); dOpen.forEach(d => bc[lim.findIndex(l => d <= l)]++);
  out.push(section(med === null ? "Days open: no removed postings yet" : `Median posting stays open ${med} day${med === 1 ? "" : "s"}`,
    `Removed date minus first-seen date, for removed postings that are not first-run postings (${dOpen.length} so far). ${dOpen.length ? "" : "This fills in once postings start being removed."}`,
    barChart(buckets, [{name: "Removed postings", cls: "bar", values: bc}], {label: "Days open, removed postings", rotate: 0})));

  // 5. Share removed within seven days
  const elig = nonFirst.filter(r => lastN - dayNum(r.first_seen) >= 7);
  const quick = elig.filter(r => r.removed_date && dayNum(r.removed_date) - dayNum(r.first_seen) <= 7);
  const share = elig.length ? quick.length / elig.length : null;
  out.push(section(share === null ? "Share removed within 7 days: not enough history yet" : `${(share * 100).toFixed(1)}% of postings are removed within 7 days`,
    `Among non-first-run postings first seen at least 7 days before ${last}: ${quick.length} of ${elig.length} were removed within 7 days of first seen.`,
    barChart(["Within 7 days", "Later or still open"], [{name: "Postings", cls: "bar2", values: [quick.length, elig.length - quick.length]}], {label: "Share removed within seven days", rotate: 0})));

  // 6. Top locations
  const locs = [...countBy(open.filter(r => r.location), r => r.location)].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 10);
  out.push(section(locs.length ? `${locs[0][0]} leads open postings (${locs[0][1]})` : "No locations",
    `Top ${locs.length} locations among the ${open.length} open postings, as the employer wrote them.`,
    barChart(locs.map(l => l[0]), [{name: "Open", cls: "bar", values: locs.map(l => l[1])}], {label: "Top locations", rotate: 50})));

  document.getElementById("out").innerHTML = out.join("");
})();
