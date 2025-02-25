#Use NLST data to see what VM Match does
import argparse
from crdclib import crdclib
import requests
import json
import pprint
import pandas as pd

def vmMatchReq(reqobj):
    vmatchprodurl = "https://cadsrapi.cancer.gov/rad/vmMatch/v1/vmMatch"
    headers = { 'Content-Type': 'application/json',
            'matchType': 'Restricted',
            'function': 'Concepts Only'}
    
    try:
        matchres = requests.post(vmatchprodurl, data=json.dumps(reqobj), headers=headers)
    except requests.exceptions.HTTPError as e:
        pprint.pprint(e)
    return json.loads(matchres.content.decode())

def parseValues(jsonobj):
    templist = []
    for value in jsonobj['FormatText'].values():
        templist.append(value)
    return templist

def main(args):
    configs = crdclib.readYAML(args.configfile)
    datadict = crdclib.readYAML(configs['DictFile'])
    
    #Test case
    pvlist = parseValues(datadict['cancyr'])
    print(pvlist)
    query = []
    for pv in pvlist:
        query.append({'name': pv, 'userTip': pv})
    
    matchres = vmMatchReq(query)
    finalres = {}
    #final_df = pd.DataFrame(columns=['pv', 'cdeid', 'cdever'])
    for stanza in matchres['matchResults']:
        queryterm = stanza['name']
        temp = []
        for match in stanza['matches']:
            temp.append({'cdeid': match['itemId'], 'cdever': match['version']})
            #final_df.loc[len(final_df)] = {'pv': queryterm, 'cdeid': match['itemId'], 'cdever': match['version']}
        finalres[queryterm] = temp
        
    #pprint.pprint(finalres)
    #pprint.pprint(final_df['cdeid'].value_counts())
            
    # So let's build a dataframe of CDEs associated wtih each of the terms.
    columns = ['pv', 'publicId', 'longName', 'context', 'syn_name', 'syn_context']
    cde_df = pd.DataFrame(columns=columns)
    for pv, cdeidlist in finalres.items():
        for entry in cdeidlist:
            cdejson = crdclib.getCDERecord(entry['cdeid'], entry['cdever'])
            publicId = cdejson['DataElement']['publicId']
            longName = cdejson['DataElement']['longName']
            context = cdejson['DataElement']['context']
            altlist = cdejson['DataElement']['AlternateNames']
            alt_name = None
            alt_context = None
            for alternate in altlist:
                if alternate['type'] == 'Synonym':
                    alt_name = alternate['name']
                    alt_context = alternate['context']
                cde_df.loc[len(cde_df)] = {'pv': pv, 'publicId':publicId, 'longName':longName, 
                                           'context': context, 'syn_name': alt_name, 'syn_context': alt_context}
    print(cde_df.head())
                    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)