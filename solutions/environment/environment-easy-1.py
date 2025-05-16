import pandas as pd
import os
data_path = "./data/environment/input"
# q1

# What percentage of water samples collected from Massachusetts beaches during the 2013 bathing season exceeded bacterial standards, leading to temporary closures?

filename_2013 = "water-body-testing-2013.csv"
df_2013 = pd.read_csv(os.path.join(data_path, filename_2013))
violation_df = df_2013[df_2013['Violation'].str.lower() == 'yes']
print(len(violation_df) / len(df_2013) * 100.0)
