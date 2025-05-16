"""
What is the ratio of reported credit card frauds between 2024 and 2020? (2024 reports ) / (2020 reports)
 -- CSN_Top_Three_Identity_Theft_Reports_by_Year.csv
 -- number
 -- hard: Columns are named wrong
"""
import pandas as pd
import re
from io import StringIO
from bs4 import BeautifulSoup
import os

data_path = "./data/legal/input/"

# ===============================================================
# Read messy csv files
# ===============================================================
def convert_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip().replace(",", "")
        if val == "":
            return None
        if val.startswith("$"):
            val = val[1:]
        match = re.match(r"^([\d.]+)([MK]?)$", val, re.IGNORECASE)
        if match:
            num, suffix = match.groups()
            try:
                num = float(num)
                if suffix.upper() == "M":
                    num *= 1_000_000
                elif suffix.upper() == "K":
                    num *= 1_000
                return int(num) if num.is_integer() else num
            except ValueError:
                return val
        try:
            return float(val) if '.' in val else int(val)
        except:
            return val
    return val


def read_clean_numeric_csv(path, encoding="utf-8"):
    # Read lines and clean up
    with open(path, "r", encoding=encoding) as f:
        lines = [line.strip() for line in f if line.strip()]

    # Find header line (first with 2+ non-empty columns)
    header_idx = None
    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(",")]
        if sum(1 for p in parts if p) >= 2:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("No suitable header row found.")

    # Keep rows until the first row with fewer than 2 non-empty cells *after* the header
    data_lines = []
    for line in lines[header_idx:]:
        parts = [p.strip() for p in line.split(",")]
        if sum(1 for p in parts if p) < 2:
            break
        data_lines.append(line)

    # Use pandas to read from the in-memory string
    csv_text = "\n".join(data_lines)
    df = pd.read_csv(StringIO(csv_text))

    # Clean up numbers
    for col in df.columns:
        df[col] = df[col].apply(convert_value)

    return df



df = read_clean_numeric_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Top_Three_Identity_Theft_Reports_by_Year.csv")

# Normalize theft type strings
df["Year"] = df["Year"].str.strip().str.lower()

# Get values safely with corrected logic
def get_reports(theft_type, year):
    match = df[(df["Theft Type"] == year) & (df["Year"] == theft_type.lower())]
    if not match.empty:
        return match["# of Reports"].iloc[0]
    else:
        raise ValueError(f"No data found for theft type '{theft_type}' and year {year}")

try:
    cc_2020 = get_reports("Credit Card", 2020)
    cc_2024 = get_reports("Credit Card", 2024)
    ratio = cc_2024 / cc_2020
    print(ratio)
except ValueError as e:
    print(e)

