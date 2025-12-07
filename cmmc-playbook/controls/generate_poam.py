import csv
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVIDENCE = BASE_DIR / "evidence"
CONTROLS = BASE_DIR / "controls"
OUTPUT = EVIDENCE / "POAM_Generated.csv"

def load_practices():
    practices = {}
    with open(CONTROLS / "L2_Practices_110.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            practices[row["PracticeID"]] = row
    return practices

def main():
    practices = load_practices()
    poam_rows = []

    with open(EVIDENCE / "Implementation_Status.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row["Status"]
            if status not in ("Implemented", "Not Applicable"):
                pid = row["PracticeID"]
                ao = row.get("AO_ID", "")
                practice = practices.get(pid, {})
                weakness = f"Practice {pid} ({practice.get('PracticeTitle','')}) AO {ao} not fully implemented."
                poam_rows.append({
                    "POAM_ID": f"POAM-{len(poam_rows)+1:03}",
                    "PracticeID": pid,
                    "AO_ID": ao,
                    "WeaknessDescription": weakness,
                    "PlannedRemediation": "",
                    "MilestoneDate": "",
                    "Responsible": row.get("ControlOwner", ""),
                    "Status": "Open",
                    "DateIdentified": str(date.today()),
                    "ResidualRisk": ""
                })

    fieldnames = ["POAM_ID","PracticeID","AO_ID","WeaknessDescription",
                  "PlannedRemediation","MilestoneDate","Responsible",
                  "Status","DateIdentified","ResidualRisk"]

    with open(OUTPUT, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(poam_rows)

    print(f"POA&M generated at {OUTPUT}")

if __name__ == "__main__":
    main()
