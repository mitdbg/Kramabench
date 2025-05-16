import re
import typing as t
import numpy as np

class TableCsv:
    def __init__(self,
                 columns: t.List[str],
                 values: t.List[t.List[t.Any]]):
        self.columns = columns
        self.values = values


def remove_commas_in_quotes(line):
    return re.sub(r'"[^"]*"', lambda m: m.group(0).replace(',', ''), line)

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
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            raw_contents = f.readlines()
        table_name = raw_contents[0].replace(',', '').strip()
        attributes: t.Dict[str, t.Any] = {}
        current_block = []
        first_table = True
        for line in raw_contents[1:]:
            cleaned_line = remove_commas_in_quotes(line)
            cleaned_line = cleaned_line.replace('"', '').strip()
            if cleaned_line.replace(',', '').strip() == '':
                # start of the next attribute
                if len(current_block) <= 0:
                    continue
                sub_table_name = [v.strip() for v in current_block[0].split(',') if v.strip() != '']
                if (first_table or len(sub_table_name) == 1) and len(current_block) >= 3:
                    # treat it as a csv table.
                    if first_table:
                        sub_table_name = table_name
                    else:
                        sub_table_name = sub_table_name[0]
                    columns = [col.strip() for col in current_block[1].split(',')]
                    values = []
                    for l in current_block[2:]:
                        value = [val.strip() for val in l.split(',')]
                        values.append(value)
                    attributes[sub_table_name] = TableCsv(columns, values)
                else:
                    # treat it an unorganized texts
                    for l in current_block:
                        attr_name = l.split(',')[0]
                        attr_content = '|'.join([v.strip() for v in l.split(',')[1:] if v.strip() != ''])
                        attributes[attr_name] = attr_content
                current_block = []
                first_table = False
            else:
                current_block.append(cleaned_line)
        return Table(table_name, csv_path, attributes)


data_path = "./data/legal/input/"
table1 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Report_Type.csv")
table2 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_Identity_Theft_Reports_by_Type.csv")


def solve_legal_easy_21() -> float:
    sub_table1 = table1.attributes['Report Type']
    sub_table2 = table2.attributes['Identity Theft Reports by Type']
    total = int(sub_table1.values[0][1])
    correct = int(sub_table2.values[1][2])
    return correct/total
print(solve_legal_easy_21())

