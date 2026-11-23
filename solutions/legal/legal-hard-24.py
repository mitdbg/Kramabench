import csv
import typing as t
import numpy as np
data_path = "./data/legal/input/"

class TableCsv:
    def __init__(self,
                 columns: t.List[str],
                 values: t.List[t.List[t.Any]]):
        self.columns = columns
        self.values = values


class Table:
    def __init__(self,
                 table_name: str,
                 csv_location: str,
                 attributes: t.Dict[str, t.Any],
                 ):
        self.table_name = table_name
        self.csv_location = csv_location
        self.attributes = attributes

    @staticmethod
    def parse_table(csv_path: str) -> 'Table':
        with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
            raw_contents = list(csv.reader(f))
        table_name = raw_contents[0][0].strip()
        attributes: t.Dict[str, t.Any] = {}
        current_block = []
        first_table = True
        for row in raw_contents[1:]:
            cleaned_row = [cell.strip() for cell in row]
            if not any(cleaned_row):
                # start of the next attribute
                if len(current_block) <= 0:
                    continue
                sub_table_name = [v for v in current_block[0] if v != '']
                if (first_table and len(current_block) >= 2) or (len(sub_table_name) == 1 and len(current_block) >= 3):
                    # treat it as a csv table.
                    if first_table:
                        sub_table_name = table_name
                        start_idx = 0
                    else:
                        sub_table_name = sub_table_name[0]
                        start_idx = 1
                    columns = current_block[start_idx]
                    values = current_block[start_idx+1:]
                    attributes[sub_table_name] = TableCsv(columns, values)
                else:
                    # treat it an unorganized texts
                    for row in current_block:
                        attr_name = row[0]
                        attr_content = '|'.join([v for v in row[1:] if v != ''])
                        attributes[attr_name] = attr_content
                current_block = []
                first_table = False
            else:
                current_block.append(cleaned_row)
        return Table(table_name, csv_path, attributes)


table1 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_State_Rankings_Identity_Theft_Reports.csv")
table2 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_State_Rankings_Fraud_and_Other_Reports.csv")

def solve_state() -> float:
    sub_table1 = table1.attributes['State Rankings: Identity Theft Reports']
    sub_table2 = table2.attributes['State Rankings: Fraud and Other Reports']
    best_total = -1
    best_name = None
    for row in sub_table1.values:
        state_name = row[1]
        for row2 in sub_table2.values:
            if state_name == row2[1]:
                total = int(row[3].replace(',', '')) + int(row2[3].replace(',', ''))
                if total > best_total:
                    best_total = total
                    best_name = state_name
                break
    return best_name
state_name = solve_state()


table3 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/State MSA Identity Theft data/{state_name}.csv")
def solve_legal_hard_24() -> float:
    sub_table3 = table3.attributes['Metropolitan Areas: Identity Theft Reports']
    best_region = None
    best_score = -1
    for row in sub_table3.values:
        if best_score < int(row[1].replace(',', '')):
            best_region = row[0]
            best_score = int(row[1].replace(',', ''))
    return best_region
print(solve_legal_hard_24())

