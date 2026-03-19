"""
split_evidence_units.py

Reads an xlsx file containing "Evidence Units" in the filename from the current directory,
parses Evidence Units and Q&A mappings, groups EUs by (Domain_Broad, Domain_13FV),
randomises order within each group, and outputs de-identified CSVs into a
'grouped_domains' subfolder.

Key design decisions:
- EU IDs (EU_001 etc.) are NOT unique across rows; uniqueness is tracked via
  (row_index, eu_label) so every EU from every row is preserved.
- Grouping is by Domain_Broad + Domain_13FV only (Domain_Framework excluded).
- Subject ID column is never read or written — fully de-identified output.

Usage:
    python split_evidence_units.py
"""

import re
import glob
import random
import pandas as pd
from pathlib import Path


# ─────────────────────────────────────────────
# 1. LOCATE THE INPUT FILE
# ─────────────────────────────────────────────

def find_input_file() -> str:
    matches = glob.glob("*Evidence Units*.xlsx") + glob.glob("*Evidence_Units*.xlsx")
    if not matches:
        raise FileNotFoundError(
            "No xlsx file containing 'Evidence Units' found in the current directory."
        )
    if len(matches) > 1:
        print(f"Multiple matches found: {matches}\nUsing first: {matches[0]}")
    return matches[0]


# ─────────────────────────────────────────────
# 2. PARSE EVIDENCE UNITS FROM A CELL
# ─────────────────────────────────────────────

def parse_evidence_units(raw_text: str, row_idx: int) -> list[dict]:
    """
    Parse the pipe/newline-delimited Evidence_Units cell into a list of EU dicts.
    Expected line format:
      EU_001|EvidenceType=symptom|Tier=CORE|Text=...|13FV=...|Broad=...|Framework=...

    A globally unique key (_uid) is built from (row_idx, position_in_row) so that
    EU_001 from row 0 is always distinct from EU_001 from row 1.
    """
    units = []
    if not isinstance(raw_text, str):
        return units

    # Normalise: convert literal '\n' escape sequences into real newlines
    raw_text = raw_text.replace("\\n", "\n")

    for pos, line in enumerate(raw_text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        eu_label = parts[0].strip()  # e.g. EU_001 — NOT globally unique

        fields = {}
        for part in parts[1:]:
            if "=" in part:
                key, _, val = part.partition("=")
                fields[key.strip()] = val.strip()

        units.append({
            "_uid":                  (row_idx, eu_label),   # internal unique key scoped to row
            "EvidenceUnitID":        eu_label,               # original label, used for Q&A lookup
            "EvidenceType":          fields.get("EvidenceType", ""),
            "RelevanceTier":         fields.get("Tier", ""),
            "EvidenceText_Internal": fields.get("Text", ""),
            "Domain_13FV":           fields.get("13FV", ""),
            "Domain_Broad":          fields.get("Broad", ""),
            "Domain_Framework":      fields.get("Framework", ""),
        })

    return units


# ─────────────────────────────────────────────
# 3. PARSE Q&A SECTION
# ─────────────────────────────────────────────

def parse_qa(raw_text: str) -> list[dict]:
    """
    Parse the Evidence_Linked_Q&A cell into a list of Q dicts.
    Expected line format:
      Q01|Section=...|Question=...|AnswerEUs=EU_001;EU_002|...
    """
    qa_list = []
    if not isinstance(raw_text, str):
        return qa_list

    # Normalise: convert literal '\n' escape sequences into real newlines
    raw_text = raw_text.replace("\\n", "\n")

    for line in raw_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        q_id = parts[0].strip()  # e.g. Q01

        fields = {}
        for part in parts[1:]:
            if "=" in part:
                key, _, val = part.partition("=")
                fields[key.strip()] = val.strip()

        answer_eus = [
            eu.strip()
            for eu in fields.get("AnswerEUs", "").split(";")
            if eu.strip()
        ]

        qa_list.append({
            "QuestionID": q_id,
            "Section":    fields.get("Section", ""),
            "Question":   fields.get("Question", ""),
            "AnswerEUs":  answer_eus,
        })

    return qa_list


# ─────────────────────────────────────────────
# 4. BUILD (row_idx, eu_label) → Q MAPPING
# ─────────────────────────────────────────────

def build_uid_to_qa_map(
    qa_list: list[dict],
    row_idx: int,
) -> dict[tuple, list[dict]]:
    """
    Returns a dict: (row_idx, eu_label) -> list of {QuestionID, Section, Question}.
    Scoped to a single row so EU_001 in row 0 only maps to that row's Q&A.
    """
    mapping: dict[tuple, list[dict]] = {}
    for qa in qa_list:
        for eu_label in qa["AnswerEUs"]:
            uid = (row_idx, eu_label)
            mapping.setdefault(uid, []).append({
                "QuestionID": qa["QuestionID"],
                "Section":    qa["Section"],
                "Question":   qa["Question"],
            })
    return mapping


# ─────────────────────────────────────────────
# 5. SAFE FILENAME HELPER
# ─────────────────────────────────────────────

def safe_name(s: str) -> str:
    return re.sub(r'[^\w]', '_', s)


# ─────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────

def main():
    # --- Locate and load xlsx ---
    input_path = find_input_file()
    print(f"Reading: {input_path}")
    df = pd.read_excel(input_path)

    # --- Auto-detect EU and Q&A columns ---
    col_map = {}
    for col in df.columns:
        lc = col.lower().replace(" ", "_")
        if "evidence_unit" in lc and "linked" not in lc:
            col_map["eu_col"] = col
        elif "evidence_linked" in lc or ("linked" in lc and "q" in lc):
            col_map["qa_col"] = col

    if "eu_col" not in col_map:
        col_map["eu_col"] = df.columns[1]
        print(f"  Warning: EU column not auto-detected; using '{col_map['eu_col']}'")
    if "qa_col" not in col_map:
        col_map["qa_col"] = df.columns[2]
        print(f"  Warning: Q&A column not auto-detected; using '{col_map['qa_col']}'")

    print(f"  EU column  : {col_map['eu_col']}")
    print(f"  Q&A column : {col_map['qa_col']}")

    # --- Collect ALL EUs and build per-row Q&A mapping ---
    all_eus: list[dict] = []
    uid_to_qa: dict[tuple, list[dict]] = {}

    for row_idx, row in df.iterrows():
        row_eus = parse_evidence_units(row.get(col_map["eu_col"], ""), row_idx)
        row_qa  = parse_qa(row.get(col_map["qa_col"], ""))

        all_eus.extend(row_eus)
        uid_to_qa.update(build_uid_to_qa_map(row_qa, row_idx))

    if not all_eus:
        raise ValueError("No evidence units were parsed. Check the column names in your xlsx.")

    print(f"  Total EUs collected (all rows, all subjects): {len(all_eus)}")

    # --- Group by (Domain_Broad, Domain_13FV) only ---
    groups: dict[tuple, list[dict]] = {}
    for eu in all_eus:
        key = (eu["Domain_Broad"], eu["Domain_13FV"])
        groups.setdefault(key, []).append(eu)

    # --- Output folder ---
    output_dir = Path("grouped_domains")
    output_dir.mkdir(exist_ok=True)
    print(f"\nWriting CSVs to: {output_dir.resolve()}\n")

    # --- Write one CSV per domain group ---
    for (broad, fv13), eu_list in sorted(groups.items()):

        # Randomise EU order within group
        random.shuffle(eu_list)

        rows = []
        for eu in eu_list:
            uid        = eu["_uid"]
            qa_entries = uid_to_qa.get(uid, [])

            base = {
                "EvidenceType":          eu["EvidenceType"],
                "RelevanceTier":         eu["RelevanceTier"],
                "EvidenceText_Internal": eu["EvidenceText_Internal"],
                "Domain_13FV":           eu["Domain_13FV"],
                "Domain_Broad":          eu["Domain_Broad"],
                "Domain_Framework":      eu["Domain_Framework"],
            }

            if qa_entries:
                for qa in qa_entries:
                    rows.append({**base,
                        "QuestionID": qa["QuestionID"],
                        "Section":    qa["Section"],
                        "Question":   qa["Question"],
                    })
            else:
                rows.append({**base,
                    "QuestionID": "",
                    "Section":    "",
                    "Question":   "",
                })

        out_df = pd.DataFrame(rows, columns=[
            "EvidenceType",
            "RelevanceTier",
            "EvidenceText_Internal",
            "Domain_13FV",
            "Domain_Broad",
            "Domain_Framework",
            "QuestionID",
            "Section",
            "Question",
        ])

        filename = f"{safe_name(broad)}_{safe_name(fv13)}.csv"
        out_path = output_dir / filename
        out_df.to_csv(out_path, index=False)
        print(f"  [{len(eu_list):>3} EUs]  {filename}")

    print(f"\nDone. {len(groups)} domain group CSV(s) written to '{output_dir}/'.")


if __name__ == "__main__":
    main()