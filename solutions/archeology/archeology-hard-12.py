#!/usr/bin/env python
# coding: utf-8
import pandas as pd
data_path = "./data/archeology/input"

city_path = f"{data_path}/worldcities.csv"
city_df = pd.read_csv(city_path)
countries = city_df["country"].unique().tolist()
countries = set(countries)

path = f"{data_path}/conflict_brecke.csv"
conflict_data = pd.read_csv(path)
processed_rows = []


def get_matching_word(sentence, checklist):
    words = sentence.lower()
    for item in checklist:
        if item.lower() in words:
            return item
    return None

for index, row in conflict_data.iterrows():
    name = row["Conflict"]
    if "-" in name:
        name = name.split("-")
        actor_a = name[0]
        actor_b = name[1]
    elif "and" in name:
        name = name.split("and")
        actor_a = name[0]
        actor_b = name[1]
    else:
        actor_a = name
        actor_b = name

    start_year = int(row["StartYear"])
    end_year = int(row["EndYear"])
                   
    actor_a = get_matching_word(actor_a, countries)
    actor_b = get_matching_word(actor_b, countries)

    if actor_a is None or actor_b is None:
        continue

    actor_a, actor_b = sorted([actor_a, actor_b])

    processed_rows.append({
        "actor_a": actor_a,
        "actor_b": actor_b,
        "start": start_year,
        "end": end_year,
    })

filtered_data = pd.DataFrame(processed_rows)

dedup_data = pd.DataFrame(columns=["actor_a", "actor_b", "start", "end"])

grouped_conflicts = filtered_data.groupby(["actor_a", "actor_b"])
for group, df in grouped_conflicts:
    df = df.sort_values(by="start", ascending=True)
    merged_rows = []

    if len(df) > 1:
        current = df.iloc[0].copy()     
        for i in range(1, len(df)):
            next_row = df.iloc[i]
            if next_row["start"] <= current["end"]:
                if next_row["end"] > current["end"]:
                    current["end"] = next_row["end"]
            else:
                merged_rows.append(current)
                current = next_row.copy()
        merged_rows.append(current)
        df = pd.DataFrame(merged_rows)

    dedup_data = pd.concat([dedup_data, df], ignore_index=True)

print(len(dedup_data))