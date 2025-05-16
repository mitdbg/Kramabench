"""
Are the report counts of for "frauds and other data" in 2024 consistent for the Metropolitan area of Miami-Fort Lauderdale-West Palm Beach?
 -- State MSA Fraud And Other Data/Floria.csv
 -- CSN_Metropolitan_Areas_Fraud_and_Other_Reports.csv
 -- bool
 -- hard: Not utf-8 decodable.
 -- (answer: True)
"""

import re
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


df1 = read_clean_numeric_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Fraud and Other data/Florida.csv", encoding="ISO-8859-1")
df2 = read_clean_numeric_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Metropolitan_Areas_Fraud_and_Other_Reports.csv", encoding="ISO-8859-1")

# Normalize function to match similar area names
def normalize_area(name):
    return re.sub(r"[^\w]", "", name).lower()

# Normalize target area
target_area_1 = normalize_area("Miami-Fort Lauderdale-West Palm Beach, FL Metropolitan Statistical Area")
target_area_2 = normalize_area("Miami-Fort Lauderdale-West Palm Beach FL Metropolitan Statistical Area")

# Get row from df1
row1 = df1[df1["Metropolitan Area"].apply(normalize_area) == target_area_1]
# Get row from df2
row2 = df2[df2["Metropolitan Area"].apply(normalize_area) == target_area_2]

# Check and compare
if row1.empty:
    print(False)
elif row2.empty:
    print(False)
else:
    reports_1 = int(row1["# of Reports"].iloc[0])
    reports_2 = int(row2["# of Reports"].iloc[0])
    per_100k = int(row2["Reports per 100K Population"].iloc[0])
    
    print(reports_1 == reports_2)
