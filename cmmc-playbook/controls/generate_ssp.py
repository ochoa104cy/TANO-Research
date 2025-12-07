import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CONTROLS = BASE_DIR / "controls"
EVIDENCE = BASE_DIR / "evidence"
TEMPLATES = BASE_DIR / "templates"
OUTPUT = BASE_DIR / "evidence" / "SSP_Generated.html"

def load_practices():
    practices = {}
    with open(CONTROLS / "L2_Practices_110.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            practices[row["PracticeID"]] = row
    return practices

def load_impl_status():
    impl = defaultdict(list)
    path = EVIDENCE / "Implementation_Status.csv"
    if not path.exists():
        return impl
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl[row["PracticeID"]].append(row)
    return impl

def load_evidence():
    ev = defaultdict(list)
    path = EVIDENCE / "Evidence_Register.csv"
    if not path.exists():
        return ev
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ev[row["PracticeID"]].append(row)
    return ev

def render_practice_block(p, impl_rows, ev_rows):
    pid = p["PracticeID"]
    title = p["PracticeTitle"]
    domain = p["Domain"]
    text = p["PracticeText"]

    # simple derived status: if all AOs Implemented -> Implemented, else Partial/Not
    if not impl_rows:
        overall_status = "Not Assessed"
    else:
        statuses = {r["Status"] for r in impl_rows}
        if statuses == {"Implemented"}:
            overall_status = "Implemented"
        elif "Implemented" in statuses:
            overall_status = "Partially Implemented"
        else:
            overall_status = "Not Implemented"

    impl_html = ""
    for r in impl_rows:
        impl_html += f"""
        <tr>
          <td>{r.get("AO_ID","")}</td>
          <td>{r.get("Status","")}</td>
          <td>{r.get("ControlOwner","")}</td>
          <td>{r.get("Justification","")}</td>
        </tr>
        """

    ev_html = ""
    for e in ev_rows:
        ev_html += f"""
        <tr>
          <td>{e.get("EvidenceID","")}</td>
          <td>{e.get("EvidenceName","")}</td>
          <td>{e.get("EvidenceType","")}</td>
          <td>{e.get("Location","")}</td>
          <td>{e.get("ReviewDate","")}</td>
        </tr>
        """

    return f"""
    <section class="practice">
      <h2>{pid} – {title}</h2>
      <p><strong>Domain:</strong> {domain}</p>
      <p><strong>Requirement:</strong> {text}</p>
      <p><strong>Overall Status:</strong> {overall_status}</p>

      <h3>Assessment Details</h3>
      <table class="impl-table">
        <thead><tr><th>AO</th><th>Status</th><th>Owner</th><th>Notes</th></tr></thead>
        <tbody>{impl_html}</tbody>
      </table>

      <h3>Evidence</h3>
      <table class="evidence-table">
        <thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Location</th><th>Review Date</th></tr></thead>
        <tbody>{ev_html}</tbody>
      </table>
    </section>
    """

def main():
    practices = load_practices()
    impl = load_impl_status()
    evidence = load_evidence()

    with open(TEMPLATES / "SSP_Template.html", encoding="utf-8") as f:
        template = f.read()

    practice_blocks = []
    for pid in sorted(practices.keys()):
        p = practices[pid]
        practice_blocks.append(
            render_practice_block(p, impl.get(pid, []), evidence.get(pid, []))
        )

    html = template.replace("{{GENERATED_DATE}}", str(date.today()))
    html = html.replace("{{PRACTICE_BLOCKS}}", "\n".join(practice_blocks))

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"SSP generated at {OUTPUT}")

if __name__ == "__main__":
    main()
