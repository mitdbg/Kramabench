"""
How many frauds were reported by FTC over the web between 2022 and 2024 in total.
 -- easy
 -- number
 -- 2024_Data_Contributors.csv
"""
import pandas as pd
import re
from io import StringIO
from bs4 import BeautifulSoup
import os


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


data_path = "./data/legal/input/"
df = read_clean_numeric_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Data_Contributors.csv")

mask = (
    df["Year"].between(2022, 2024) &
    df["Data Contributor"].str.contains("FTC - Web Reports \(Fraud & Other\)", regex=True)
)

# Sum the relevant reports
total_fraud_web_reports = df.loc[mask, "# of Reports"].sum()
print(total_fraud_web_reports)

