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

beach_name = 'constitution_beach_datasheet.csv'
df = prepare_beach_datasheet(os.path.join(data_path, beach_name))
df['Year'] = df['Date'].apply(lambda x: x.split(', ')[-1]).astype(int)
df = df[df['Year'] == 2024]

# Group by 'Date' and count the number of exceedances within each group
exceedance_counts = df[df['Enterococcus'] > 104].groupby('Date').size().reset_index(name='Exceedance Count')
exceedance_counts = exceedance_counts[exceedance_counts['Exceedance Count'] < 3]
print(len(exceedance_counts))