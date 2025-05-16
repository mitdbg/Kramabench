"""
Report the average number of reported identity thefts for all metropolitan areas 
that are larger than one million in population in 2023. 

 - If you don't have their population size in 2023, 
   use two years where you know the censuses (or an estimate of the censurs) and 
   linearly interpolate between them to estimate the 2023 population size. 

 - Be sure to robustly match the names of metropolitan areas: 
   Use only the city and state portion of the name, ignoring suffixes like 
   "Metropolitan Statistical Area" or "MSA" and normalizing punctuation. Drop entries 
   where there's no match in the html for the areas fraud reports.

 --- hard, 
 --- number
 --- html, State MSA Identitiy Theft Data/ *
"""

import pandas as pd
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


# ===============================================================
# Parse html
# ===============================================================
def parse_out_table_from_html():
    table_title = "The 387 metropolitan statistical areas of the United States"
    html_path = f"{data_path}/metropolitan_statistics.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')

    # Find all tables
    tables = soup.find_all('table')
    for idx, table in enumerate(tables):
        caption = table.find('caption')
        if caption and table_title.lower() in caption.text.lower():
            # Convert to string and read with pandas
            return pd.read_html(str(table))[0]
    
    raise ValueError(f"Table with title containing '{table_title}' not found.")


def add_interpolated_2023_pop(df):
    # Linear interpolation for 2023
    df["2023 interpolated"] = df["2020 census"] + (3 / 4) * (df["2024 estimate"] - df["2020 census"])
    df["2023 interpolated"] = df["2023 interpolated"].astype(int)  # optional: convert to integer


def get_absolute_population_df():
    df = parse_out_table_from_html()
    add_interpolated_2023_pop(df)
    return df


# ===============================================================
# Read per state reports.
# ===============================================================
def get_fraud_number_across_states():
    state_dfs = []
    state_dir = f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft data/"
    for f in os.listdir(state_dir):
        f = os.path.join(state_dir, f)
        state_dfs.append(read_clean_numeric_csv(f).head())
    return pd.concat(state_dfs, ignore_index=True)


df_reports = get_fraud_number_across_states()
df_population = get_absolute_population_df()


# Normalize names
def normalize_name(name):
    name = name.lower()
    name = re.sub(r'\s*(metropolitan statistical area|msa)$', '', name)
    name = re.sub(r'[^a-z0-9]+', '', name)
    return name

# Normalize the metropolitan area names.
df_reports['msa_key'] = df_reports['Metropolitan Area'].apply(normalize_name)
df_population['msa_key'] = df_population['Metropolitan statistical area'].apply(normalize_name)

# Merge on msa_key.
df_merged = pd.merge(df_reports, df_population, on='msa_key', how='inner')

# Filter for MSAs with >1M population
df_large = df_merged[df_merged['2023 interpolated'] > 1_000_000]

# Compute average number of reports per 100K
avg_reports_per_100k = df_large['# of Reports'].mean()

print(avg_reports_per_100k)
