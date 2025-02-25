#This will convert the NLST numeric system to text based
import argparse
import pandas as pd
from crdclib import crdclib


def main(args):
    configs = crdclib.readYAML(args.configfile)
    datadict = crdclib.readYAML(configs['DictFile'])
    
    finalfiles = {}
    
    for csvfile in configs['datafiles']:
        templist = csvfile.split('\\')
        filename = 'RECODED_'+templist[-1]
        filename = configs['outputDir']+filename
        df = pd.read_csv(csvfile, dtype=str)
        #Convert everything to str
        #df = df.map(str)
        for key, value in datadict.items():
            if key in df.columns:
                if len(value['FormatText'].keys()) != 1:
                    df[key] = df[key].replace(value['FormatText'])
                
        #print(f"Writing to {filename}")
        df.to_csv(filename, sep="\t", index=False)
                                 
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)