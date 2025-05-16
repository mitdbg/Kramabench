import csv
import sys
import pandas as pd
csv.field_size_limit(sys.maxsize)

def tsv_to_csv(tsv_file, csv_file, delimiter='\t', encoding='utf-8'):
    with open(tsv_file, 'r', encoding=encoding) as tsv_f, open(csv_file, 'w', newline='') as csv_f:
        tsv_reader = csv.reader(tsv_f, delimiter=delimiter)
        csv_writer = csv.writer(csv_f)
        for row in tsv_reader:
            csv_writer.writerow(row)

def xlsx_to_csv(xlsx_file, csv_file):
    pd.read_excel(xlsx_file).to_csv(csv_file, index=False)

_file_identity_check_data = dict()
def file_identity_check(id, file_path, tag=None):
    global _file_identity_check_data
    with open(file_path, "rb") as f:
        file_content = f.read()
    if id not in _file_identity_check_data:
        _file_identity_check_data[id] = file_content
    else:
        if _file_identity_check_data[id] != file_content:
            with open("diff1.log", "wb") as f: f.write(_file_identity_check_data[id])
            with open("diff2.log", "wb") as f: f.write(file_content)
            raise ValueError(f"File content '{id}' difference: {tag}.")