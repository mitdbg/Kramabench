import pandas as pd
data_path = "./data/legal/input/"

military_consumer_reports_df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Reports_by_Military_Consumers.csv")
report_categories_df = pd.read_csv(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Categories.csv", encoding="ISO-8859-1")

# extract military table
top_military_categories_df = military_consumer_reports_df.iloc[12:23]
column_names = list(top_military_categories_df.iloc[0].to_dict().values())
top_military_categories_df.columns = [col.strip() for col in column_names]
top_military_categories_df = top_military_categories_df.iloc[1:]

# extract report table
column_names = list(report_categories_df.iloc[1].to_dict().values())
report_categories_df.columns = [col.strip() for col in column_names]
report_categories_df = report_categories_df.iloc[2:-4]

# get pct of imposter scams in military
top_military_categories_df['# of Reports'] = top_military_categories_df['# of Reports'].apply(lambda elt: int(elt.replace(",","")))
total_military_reports = top_military_categories_df['# of Reports'].sum()
military_imposter_scams = top_military_categories_df.loc[top_military_categories_df.Category == 'Imposter Scams']['# of Reports'].iloc[0]
pct_military_imposter_scams = military_imposter_scams/total_military_reports

# get pct of imposter scams in general population
pct_general_imposter_scams = report_categories_df.loc[report_categories_df.Category == "Imposter Scams"]['Percentage'].iloc[0]
pct_general_imposter_scams = float(pct_general_imposter_scams.replace("%",""))/100.0

if pct_military_imposter_scams > pct_general_imposter_scams:
    print("Yes")
else:
    print("No")