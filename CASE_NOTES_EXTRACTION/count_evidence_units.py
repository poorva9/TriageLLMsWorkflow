"""
count_evidence_units.py

Reads an xlsx file containing "Evidence Units" in the filename from the current directory
and prints a count of Evidence Units per row.

Handles two storage formats:
  - EUs separated by real newlines  (\\n in file = actual line break)
  - EUs stored as a single string with literal '\\n' escape sequences

Usage:
    python count_evidence_units.py
"""

import re
import glob
import pandas as pd


def find_input_file() -> str:
    matches = glob.glob("*Evidence Units*.xlsx") + glob.glob("*Evidence_Units*.xlsx")
    if not matches:
        raise FileNotFoundError(
            "No xlsx file containing 'Evidence Units' found in the current directory."
        )
    if len(matches) > 1:
        print(f"Multiple matches found: {matches}\nUsing first: {matches[0]}")
    return matches[0]


def count_eus_in_cell(raw_text) -> int:
    """
    Count EU entries in a cell regardless of whether EUs are separated by:
      - real newlines  (\n characters)
      - literal backslash-n escape sequences (\\n stored as text)
    Counts by finding all occurrences of the pattern EU_<digits> at the
    start of each logical line.
    """
    if not isinstance(raw_text, str):
        return 0

    # Normalise: replace literal '\n' text sequences with a real newline
    normalised = raw_text.replace("\\n", "\n")

    # Count lines that begin with EU_ (after stripping whitespace)
    return sum(
        1 for line in normalised.splitlines()
        if re.match(r"^EU_\d+", line.strip())
    )


def main():
    input_path = find_input_file()
    print(f"Reading: {input_path}\n")
    df = pd.read_excel(input_path)

    # Auto-detect EU column
    eu_col = None
    for col in df.columns:
        lc = col.lower().replace(" ", "_")
        if "evidence_unit" in lc and "linked" not in lc:
            eu_col = col
            break
    if eu_col is None:
        eu_col = df.columns[1]
        print(f"Warning: EU column not auto-detected; using '{eu_col}'\n")

    # Try to find a subject/patient ID column
    id_col = None
    for col in df.columns:
        lc = col.lower().replace(" ", "_")
        if "subject" in lc or "patient" in lc or lc == "id":
            id_col = col
            break

    print(f"EU column : {eu_col}")
    print(f"ID column : {id_col if id_col else '(none detected — using row index)'}\n")
    print(f"{'Row':<6} {'Subject ID':<20} {'EU Count'}")
    print("-" * 40)

    total = 0
    for row_idx, row in df.iterrows():
        count   = count_eus_in_cell(row.get(eu_col, ""))
        subject = str(row[id_col]) if id_col else f"Row {row_idx}"
        print(f"{row_idx:<6} {subject:<20} {count}")
        total  += count

    print("-" * 40)
    print(f"{'TOTAL':<27} {total}")
    print(f"\n{len(df)} row(s) processed. {total} EUs counted in total.")


if __name__ == "__main__":
    main()
