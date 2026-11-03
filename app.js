// Shared helpers: nav, data loading, CSV parsing, charts.
const PAGES = [["index.html", "Today"], ["browse.html", "Browse"], ["market.html", "Market"]];

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
}
function safeUrl(u) { return /^https?:\/\//i.test(u) ? u : "#"; }

function renderNav() {
  const here = location.pathname.split("/").pop() || "index.html";
  document.body.insertAdjacentHTML("afterbegin",
    `<nav><span class="logo">Job Watcher</span>${PAGES.map(([h, t]) =>
      `<a href="${h}"${h === here ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>`);
}

function parseCSV(text) {
  const rows = []; let row = [], f = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
    else if (c !== "\r") f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  const head = rows.shift() || [];
  return rows.filter(r => r.length === head.length).map(r => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

async function loadHistory() {
  const rows = parseCSV(await (await fetch("data/history.csv")).text());
  for (const r of rows) { r.in_role = r.in_role === "true"; r.first_run = r.first_run === "true"; }
  return rows;
}
async function loadStatus() { return (await fetch("data/status.json")).json(); }

const DAY = 86400000;
function dayNum(s) { return Math.round(Date.parse(s + "T00:00:00Z") / DAY); }
function dayStr(n) { return new Date(n * DAY).toISOString().slice(0, 10); }
function lastRunDate(rows) { return rows.reduce((m, r) => r.last_seen > m ? r.last_seen : m, ""); }

// Vertical bar chart. series: [{name, cls, values}] sharing labels.
function barChart(labels, series, opts = {}) {
  const W = Math.max(480, labels.length * 26 * series.length + 60), H = 220, L = 36, B = 44, T = 10;
  const max = Math.max(1, ...series.flatMap(s => s.values));
  const slot = (W - L - 8) / Math.max(1, labels.length), bw = Math.max(3, slot * 0.8 / series.length);
  let g = "";
  for (let k = 0; k <= 4; k++) {
    const v = Math.round(max * k / 4), y = H - B - (H - B - T) * k / 4;
    g += `<line x1="${L}" x2="${W}" y1="${y}" y2="${y}" stroke="currentColor" opacity=".12"/><text x="${L - 4}" y="${y + 4}" text-anchor="end">${v}</text>`;
  }
  labels.forEach((lab, i) => {
    series.forEach((s, j) => {
      const h = (H - B - T) * s.values[i] / max, x = L + i * slot + slot * 0.1 + j * bw;
      g += `<rect class="${s.cls}" x="${x}" y="${H - B - h}" width="${bw}" height="${h}"><title>${esc(lab)}: ${s.values[i]} (${esc(s.name)})</title></rect>`;
    });
    if (labels.length <= 14 || i % Math.ceil(labels.length / 14) === 0)
      g += `<text transform="translate(${L + i * slot + slot / 2},${H - B + 12}) rotate(${opts.rotate ?? 40})" text-anchor="start">${esc(lab.length > 22 ? lab.slice(0, 21) + "…" : lab)}</text>`;
  });
  const legend = series.length > 1 ? `<p class="legend">${series.map(s => `<span style="color:var(--${s.cls === "bar" ? "brand" : "good"})">■</span> ${esc(s.name)}`).join(" &nbsp; ")}</p>` : "";
  return `<div class="chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.label || "chart")}">${g}</svg>${legend}</div>`;
}

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
document.addEventListener("DOMContentLoaded", renderNav);
