async function loadCSV(path) {
  const res = await fetch(path);
  const text = await res.text();
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.map(line => {
    const cols = line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/); // naive CSV split
    const row = {};
    headers.forEach((h, i) => row[h] = cols[i] ? cols[i].replace(/^"|"$/g, "") : "");
    return row;
  });
}

function derivePracticeStatus(aoRows) {
  if (aoRows.length === 0) return "Not Assessed";
  const statuses = new Set(aoRows.map(r => r.Status));
  if (statuses.size === 1 && statuses.has("Implemented")) return "Implemented";
  if (statuses.has("Implemented")) return "Partially Implemented";
  if (statuses.has("Not Applicable")) return "Partially Implemented";
  return "Not Implemented";
}

async function initDashboard() {
  const practices = await loadCSV("../controls/L2_Practices_110.csv");
  const impl = await loadCSV("../evidence/Implementation_Status.csv");

  const implByPractice = {};
  impl.forEach(row => {
    const pid = row.PracticeID;
    if (!implByPractice[pid]) implByPractice[pid] = [];
    implByPractice[pid].push(row);
  });

  const practiceStatus = {};
  practices.forEach(p => {
    const pid = p.PracticeID;
    practiceStatus[pid] = derivePracticeStatus(implByPractice[pid] || []);
  });

  // Summary counts
  const total = practices.length;
  let implemented = 0, partial = 0, notImpl = 0;

  Object.values(practiceStatus).forEach(st => {
    if (st === "Implemented") implemented++;
    else if (st === "Partially Implemented") partial++;
    else if (st === "Not Implemented") notImpl++;
  });

  document.getElementById("total-practices").textContent = total;
  document.getElementById("implemented-practices").textContent = implemented;
  document.getElementById("partial-practices").textContent = partial;
  document.getElementById("not-practices").textContent = notImpl;

  // Domain table
  const domainStats = {};
  practices.forEach(p => {
    const d = p.Domain || "Unknown";
    const pid = p.PracticeID;
    const st = practiceStatus[pid] || "Not Assessed";
    if (!domainStats[d]) {
      domainStats[d] = { total: 0, impl: 0, partial: 0, notImpl: 0 };
    }
    domainStats[d].total++;
    if (st === "Implemented") domainStats[d].impl++;
    else if (st === "Partially Implemented") domainStats[d].partial++;
    else if (st === "Not Implemented") domainStats[d].notImpl++;
  });

  const tbody = document.querySelector("#domain-table tbody");
  tbody.innerHTML = "";
  Object.entries(domainStats).forEach(([domain, s]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${domain}</td>
      <td>${s.total}</td>
      <td>${s.impl}</td>
      <td>${s.partial}</td>
      <td>${s.notImpl}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.addEventListener("DOMContentLoaded", initDashboard);
