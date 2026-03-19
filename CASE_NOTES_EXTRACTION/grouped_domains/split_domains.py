#!/usr/bin/env python3
"""
split_domains.py

Splits all CSV files in the current directory into chunks of 50 data rows each.
Output files are saved into a 'split_domains' folder created in the current directory.

Usage:
    python3 split_domains.py
"""

import csv
import os
import sys


CHUNK_SIZE = 50
OUTPUT_FOLDER = "split_domains"


def split_csv(filepath, output_dir):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            print(f"  Skipping {filename} — empty file.")
            return 0

        rows = list(reader)

    total_rows = len(rows)

    if total_rows == 0:
        print(f"  Skipping {filename} — no data rows.")
        return 0

    if total_rows <= CHUNK_SIZE:
        print(f"  Skipping {filename} — only {total_rows} rows, no split needed.")
        return 0

    num_parts = (total_rows + CHUNK_SIZE - 1) // CHUNK_SIZE

    for part_num in range(1, num_parts + 1):
        start = (part_num - 1) * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk = rows[start:end]

        output_filename = f"{name}_part{part_num}{ext}"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "w", newline="", encoding="utf-8") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(chunk)

    print(f"  {filename}: {total_rows} rows → {num_parts} parts")
    return num_parts


def main():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, OUTPUT_FOLDER)

    # Create output folder
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output folder: {output_dir}\n")

    # Find all CSV files in current directory (not recursively)
    csv_files = [
        os.path.join(current_dir, f)
        for f in os.listdir(current_dir)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(current_dir, f))
    ]

    if not csv_files:
        print("No CSV files found in the current directory.")
        sys.exit(0)

    print(f"Found {len(csv_files)} CSV file(s):\n")

    total_parts = 0
    for filepath in sorted(csv_files):
        total_parts += split_csv(filepath, output_dir)

    print(f"\nDone. {total_parts} part file(s) written to '{OUTPUT_FOLDER}/'.")


if __name__ == "__main__":
    main()
