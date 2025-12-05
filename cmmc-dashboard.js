// Load CSV with basic parsing
async function loadCSV(url) {
  const text = await fetch(url).then(res => res.text());
  const rows = text.trim().split("\n").map(r => r.split(","));
  const header = rows.shift().map(h => h.trim().toLowerCase());

  const col = {
    id: header.indexOf("practice id"),
    domain: header.indexOf("domain"),
    name: header.indexOf("practice name"),
    description: header.indexOf("description"),
    source: header.indexOf("source")
  };

  return rows.map(r => ({
    id: r[col.id]?.trim(),
    domain: r[col.domain]?.trim(),
    name: r[col.name]?.trim(),
    description: r[col.description]?.trim(),
    source: r[col.source]?.trim(),
  }));
}

// Globals
let all = [];
let filtered = [];
let selectedIndex = null;

// UI refs
const tableBody = document.getElementById("tableBody");
const emptyState = document.getElementById("emptyState");
const domainFilter = document.getElementById("domainFilter");
const searchInput = document.getElementById("searchInput");
const levelChips = document.getElementById("levelChips");

const totalCount = document.getElementById("totalCount");
const level1Count = document.getElementById("level1Count");
const level2Count = document.getElementById("level2Count");
const domainCount = document.getElementById("domainCount");

async function init() {
  const L1 = await loadCSV("cmmc-playbook/controls/L1_Practices.csv");
  const L2 = await loadCSV("cmmc-playbook/controls/L2_Practices.csv");

  // Tag levels
  L1.forEach(p => p.level = "L1");
  L2.forEach(p => p.level = "L2");

  all = [...L1, ...L2];

  updateStats();
  populateDomains();
  applyFilters();
}

function updateStats() {
  totalCount.textContent = all.length;
  level1Count.textContent = all.filter(p => p.level === "L1").length;
  level2Count.textContent = all.filter(p => p.level === "L2").length;

  const domains = new Set(all.map(p => p.domain));
  domainCount.textContent = domains.size;
}

function populateDomains() {
  const domains = [...new Set(all.map(p => p.domain))].sort();

  domains.forEach(d => {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = d;
    domainFilter.appendChild(opt);
  });
}

function getLevelFilter() {
  const active = levelChips.querySelector(".chip-active");
  return active ? active.dataset.level : "all";
}

function applyFilters() {
  const level = getLevelFilter();
  const domain = domainFilter.value;
  const q = searchInput.value.toLowerCase();

  filtered = all.filter(p => {
    if (level !== "all" && p.level !== level) return false;
    if (domain !== "all" && p.domain !== domain) return false;

    const text = `${p.id} ${p.domain} ${p.name} ${p.description} ${p.source}`.toLowerCase();
    if (q && !text.includes(q)) return false;

    return true;
  });

  renderTable();
}

function renderTable() {
  tableBody.innerHTML = "";

  if (filtered.length === 0) {
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;

  filtered.forEach((p, i) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${p.level}</td>
      <td>${p.id}</td>
      <td>${p.domain}</td>
      <td>${p.name}</td>
      <td>${p.description}</td>
      <td>${p.source}</td>
    `;

    tr.onclick = () => selectPractice(i);
    tableBody.appendChild(tr);
  });

  selectPractice(0);
}

function selectPractice(i) {
  selectedIndex = i;
  const p = filtered[i];

  document.getElementById("detailId").textContent = p.id;
  document.getElementById("detailLevel").textContent = p.level;
  document.getElementById("detailDomain").textContent = p.domain;
  document.getElementById("detailName").textContent = p.name;
  document.getElementById("detailDescription").textContent = p.description;
  document.getElementById("detailSource").textContent = p.source;

  [...tableBody.children].forEach((tr, idx) => {
    tr.classList.toggle("selected-row", idx === i);
  });
}

levelChips.onclick = e => {
  if (e.target.classList.contains("chip")) {
    [...levelChips.children].forEach(c => c.classList.remove("chip-active"));
    e.target.classList.add("chip-active");
    applyFilters();
  }
};

domainFilter.onchange = applyFilters;
searchInput.oninput = applyFilters;

init();
