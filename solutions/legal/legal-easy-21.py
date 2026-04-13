import re
import typing as t
from attr import attributes
import numpy as np
import csv
data_path = "./data/legal/input/"

class TableCsv:
    def __init__(self,
                 columns: t.List[str],
                 values: t.List[t.List[t.Any]]):
        self.columns = columns
        self.values = values


def remove_commas_in_quotes(line):
    return re.sub(r'"[^"]*"', lambda m: m.group(0).replace(',', ''), line)

def is_name_line(line):
    row = [val for val in csv.reader([line])][0]
    return row[1:] == [''] * (len(row) - 1)

def is_empty(line):
    return line.replace(',', '').replace('"', '').strip() == ''

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
        attributes: t.Dict[str, t.Any] = {}
        current_block = []
        first_table = True
        for line in raw_contents:
            if is_empty(line):
                continue

            if is_name_line(line):
                if first_table:
                    table_name = line.split(',')[0].strip()
                    first_table_name = table_name
                    first_table = False
                else:
                    # flush the current block as a csv table if it has more than 2 lines, otherwise treat it as unorganized text.
                    if len(current_block) >= 3:
                        columns = [col.strip() for col in current_block[0].split(',')]
                        values = csv.reader(current_block)
                        attributes[table_name] = TableCsv(columns, list(values))
                    else:
                       for l in current_block:
                            attr_name = l.split(',')[0]
                            attr_content = '|'.join([v.strip() for v in l.split(',')[1:] if v.strip() != ''])
                            attributes[attr_name] = attr_content

                    table_name = line.split(',')[0].strip()
                    current_block = []
                    first_table = False
            else:
                current_block.append(line)

        if len(current_block):
            if len(current_block) >= 3:
                columns = [col.strip() for col in current_block[0].split(',')]
                values = csv.reader(current_block)
                attributes[table_name] = TableCsv(columns, list(values))
            else:
                for l in current_block:
                    attr_name = l.split(',')[0]
                    attr_content = '|'.join([v.strip() for v in l.split(',')[1:] if v.strip() != ''])
                    attributes[attr_name] = attr_content

        return Table(first_table_name, csv_path, attributes)


table1 = Table.parse_table(f"{data_path}/csn-data-book-2024-csv/CSVs/2024_CSN_State_Identity_Theft_Reports.csv")


sub_table1 = table1.attributes['State: Identity Theft Reports']
total_alabama = 0
for row in sub_table1.values:
    if row[0] == 'Alabama':
        total_alabama += int(row[2].replace(',', ''))
print(total_alabama)

