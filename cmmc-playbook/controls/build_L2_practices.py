import pandas as pd

# 1. Load the NIST 800-171 spreadsheet
# Make sure this filename matches your local file
xlsx_path = "C:\\SUNY Canton\\CMMC\\NIST SP 800-171 Rev 2\\sp800-171r2-security-reqs.xlsx"
df = pd.read_excel(xlsx_path, sheet_name="SP 800-171")

# 2. Map NIST "Family" to CMMC abbreviations for Practice_ID
family_to_abbrev = {
    "Access Control": "AC",
    "Awareness and Training": "AT",
    "Audit and Accountability": "AU",
    "Configuration Management": "CM",
    "Identification and Authentication": "IA",
    "Incident Response": "IR",
    "Incident response": "IR",  # some sheets use this capitalization
    "Maintenance": "MA",
    "Media Protection": "MP",
    "Personnel Security": "PS",
    "Physical Protection": "PE",
    "Risk Assessment": "RA",
    "Security Assessment": "CA",
    "System and Communications Protection": "SC",
    "System and Information Integrity": "SI",
}

def build_practice_name(requirement_text: str, max_words: int = 7) -> str:
    """Short label for the requirement using first few words."""
    if not isinstance(requirement_text, str):
        return ""
    words = requirement_text.split()
    return " ".join(words[:max_words])

rows = []

for _, r in df.iterrows():
    family = r["Family"]
    nist_ref = r["Identifier"]                # e.g., 3.1.1
    abbrev = family_to_abbrev[family]        # e.g., AC

    practice_id = f"{abbrev}.L2-{nist_ref}"  # e.g., AC.L2-3.1.1
    domain = family                          # full family name
    requirement_text = r[" Security Requirement"]

    practice_name = build_practice_name(requirement_text, max_words=7)
    practice_desc = (
        f"Implements NIST SP 800-171 control {nist_ref} "
        f"in the {family} family for protecting CUI."
    )
    ao_summary = (
        f"See NIST SP 800-171A assessment objectives for control {nist_ref} "
        f"and verify all relevant objectives are satisfied."
    )
    practice_type = "Level 2"

    rows.append(
        {
            "Practice_ID": practice_id,
            "Domain": domain,
            "NIST_Ref": nist_ref,
            "Practice_Name": practice_name,
            "Practice_Description": practice_desc,
            "Assessment_Objectives_Summary": ao_summary,
            "Type": practice_type,
        }
    )

# 3. Create the Level 2 DataFrame
l2_df = pd.DataFrame(rows)

# Optional: sort by NIST reference for nice ordering
l2_df = l2_df.sort_values(by=["NIST_Ref"]).reset_index(drop=True)

# 4. Save as CSV
output_csv = "L2_Practices.csv"
l2_df.to_csv(output_csv, index=False)

print(f"Saved {len(l2_df)} Level 2 practices to {output_csv}")
