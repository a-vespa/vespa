import csv
import pandas as pd
import json


def get_f1score():
    origins = ["msfr", "ezzybill", "sypht", "rossum"]
    final_result = []
    for origin in origins:
        path = 'extraction_result/'+origin+'/debug_lines.csv'
        df = pd.read_csv(path)
        columns = [
            'document_name',
            'Invoice Number',
            'Total Amount',
            'Invoice Date',
            'Due Date',
            'Invoice To',
            'Invoice From'
        ]
        extraction_result = []
        for col in columns:
            if col != 'document_name':
                item = {}
                field_df = df.loc[df['field'] == col]
                EM = len(field_df.loc[field_df['label'] == 'EM'])
                Wrong = len(field_df.loc[field_df['label'] == 'Wrong'])
                PM = len(field_df.loc[field_df['label'] == 'PM'])
                NA = len(field_df.loc[field_df['label'] == 'NA'])
                if(len(field_df) > 0):
                    precition = (EM + PM) / len(field_df) * 100
                    item["f1"] = precition
                else:
                    item["f1"] = "NA"
                item["field"] = col
                extraction_result.append(item)
        result = {}
        result["extraction_engin"] = origin
        result["accuracy"] = extraction_result
        final_result.append(result)

    with open('results.json', 'a') as json_file:
        json.dump(final_result, json_file)
