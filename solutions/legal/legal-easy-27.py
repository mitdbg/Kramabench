import pandas as pd

data_path = "./data/legal/input/"
df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_State_Top_Ten_Report_Categories.csv")

# extract data
df = df.iloc[1:-4]
column_names = list(df.iloc[0].to_dict().values())
df.columns = [col.strip() for col in column_names]
df = df.iloc[1:]

# group by state, check if "Prizes, Sweepstakes and Lotteries" is in categories
prizes_states = []
for state, state_df in df.groupby('State'):
    if "Prizes, Sweepstakes and Lotteries" in state_df['Category'].tolist():
        prizes_states.append(state)
print(len(prizes_states))