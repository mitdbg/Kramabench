"""
Which fraud category was growing the fastest between 2020 and 2024 in relative terms?
 -- CSN_Top_Three_Identity_Theft_Reports_by_Year.csv
 -- hard: column names switched
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

# Normalize category strings
df["Year"] = df["Year"].str.strip().str.lower()

# Pivot the data to have one row per category, columns = [2020, 2024]
pivot = df[df["Theft Type"].isin([2020, 2024])].pivot_table(
    index="Year",
    columns="Theft Type",
    values="# of Reports"
)

# Drop categories not present in both years
pivot = pivot.dropna()

# Compute relative growth
pivot["growth_ratio"] = pivot[2024] / pivot[2020]

# Find the max
fastest_growing = pivot["growth_ratio"].idxmax()
ratio = pivot["growth_ratio"].max()

print(fastest_growing.title())
