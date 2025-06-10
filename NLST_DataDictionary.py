import pandas as pd
import argparse
from crdclib import crdclib
from docx import Document    

def parseTable(df, table):
    tabledata = [[cell.text for cell in row.cells] for row in table.rows]
    temp_df = pd.DataFrame(tabledata)
    # https://medium.com/@karthikeyan.eaganathan/read-tables-from-docx-file-to-pandas-dataframes-f7e409401370
    # This handles the headers on each table so there aren't a bunch of header rows in the data
    temp_df = temp_df.rename(columns=temp_df.iloc[0]).drop(temp_df.index[0]).reset_index(drop=True)
    new_df = pd.concat([df, temp_df], ignore_index=True)
    return new_df
    

def deQuotify(valuestring):
    #if '"' in valuestring:
    #    valuestring = valuestring.replace('"', "'")
    #if "'" in valuestring:
    #    valuestring = valuestring.replace("'", "")
    if '"' in valuestring:
        valuestring = valuestring.replace('"', "")
    return valuestring

def getPVList(docxstring):
    pvdict = {}
    stringlist = docxstring.split('\n')
    for entry in stringlist:
        # Remove '
        temp = entry.split("=")
        key = temp[0]
        value = temp[-1]
        value = deQuotify(value)
        pvdict[key] = value
    return pvdict
    
    
def main(args):
    df = pd.DataFrame()
    configs = crdclib.readYAML(args.configfile)
    
    for nlstdocx in configs['nlstdocx']:
        nlstdoc = Document(nlstdocx)
        for nlsttable in nlstdoc.tables:
            for i, row in enumerate(nlsttable.rows):
                text = (cell.text for cell in row.cells)
                if i == 0:
                    keys = tuple(text)
                    if 'Variable' in keys:
                        df = parseTable(df, nlsttable)
    #In theory, we now have a dataframe from all the docs
    # PVs, if they exist, are in teh Format Text column
    #print(df)
    
    final_json = {}
    for index, row in df.iterrows():
        if "=" in row['Format Text']:
            pvlist = getPVList(row['Format Text'])
        else:
            #pvlist = [row['Format Text']]
            pvlist = {row['Format Text']: None}
        final_json[row['Variable']] = {'Label': row['Label'], 'Description': row['Description'], 'FormatText': pvlist}
        
    crdclib.writeYAML(configs['DictFile'], final_json)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)