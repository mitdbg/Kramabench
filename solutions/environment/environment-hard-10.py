import pandas as pd
import os
data_path = "./data/environment/input"

def prepare_beach_datasheet(fp:str) -> pd.DataFrame:
    """
    Prepare the beach datasheet for analysis.
    Args:
        fp (str): File path to the beach datasheet CSV file.
    Returns:
        pd.DataFrame: Prepared DataFrame with relevant columns.
    """
    # Step 0: Check if the file exists
    if not os.path.exists(fp):
        raise FileNotFoundError(f"File not found: {fp}")
    # Step 1: Skip first row, read the next two as headers
    df = pd.read_csv(fp, skiprows=1, header=[0, 1])

    # Step 2: Flatten multi-level columns
    cols = df.columns.to_frame()
    cols[0] = cols[0].replace(r'^Unnamed.*', None, regex=True).ffill()
    df.columns = ['_'.join(col).strip() if col[0] is not None else col[1] for col in cols.itertuples(index=False, name=None)]

    # Step 3: Identify ID columns and melt the rest
    location_cols = [col for col in df.columns if 'Tag' in col or 'Enterococcus' in col]
    id_cols = [col for col in df.columns if col not in location_cols]

    melted = df.melt(id_vars=id_cols, value_vars=location_cols, 
                    var_name='Variable', value_name='Value')

    # Step 4: Extract Location and Measure from Variable column
    melted['Location'] = melted['Variable'].apply(lambda x: x.split('_')[0])
    melted['Measure'] = melted['Variable'].apply(lambda x: x.split('_')[1])

    # Step 5: Pivot to tidy format
    df = melted.pivot(index=id_cols + ['Location'], columns='Measure', values='Value').reset_index()

    # Optional: flatten column names
    df.columns.name = None

    # Step 6: cast to numeric
    for col in df.columns:
        if col not in id_cols + ['Location', 'Tag']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

ej_df = pd.read_csv(os.path.join(data_path, 'environmental-justice-populations.csv'))
more_than_90 = ej_df[ej_df['Percent of population in EJ BGs'] > 90]
more_than_90_cities = more_than_90['Municipality'].unique()
print(f"Cities with more than 90% of the population in EJ BGs: {len(more_than_90_cities)}")

df = pd.read_csv(os.path.join(data_path, 'water-body-testing-2023.csv'))
beach_type = "Marine"
df = df[df['Beach Type Description'] == beach_type]
# Use more_than_90_cities to filter the dataframe ['County']
df1 = df[df['Community'].isin(more_than_90_cities)]
# Split the 'Beach Name' column by '@' and keep only the first part, since the second part is the location of where the sample was taken
df1["Beach Name"] = df1['Beach Name'].str.split('@').str[0]
df1['Beach Name'].unique()

beach_name = 'wollaston_beach_datasheet.csv'
df = prepare_beach_datasheet(os.path.join(data_path, beach_name))
# Impute missing values in '1-Day Rain', '2-Day Rain', '3-Day Rain', 'Enterococcus'
df['Total Rain'] = df['1-Day Rain'] + df['2-Day Rain'] + df['3-Day Rain']
### NOTE: not sure if 3-Day Rain is the rain on Day 3 or the total rain over 3 days
# Compute the correlation between 'Total Rain' and 'Enterococcus'
correlation = df['3-Day Rain'].corr(df['Enterococcus'])
print(f"Correlation between Total Rain and Enterococcus: {correlation:.2f}")