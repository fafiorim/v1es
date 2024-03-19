import requests
import json
import csv

fname = "smartFoldersNameParentPrefix.csv"
csv_header = ['ID', 'name',"type","parentSmartFolderID"]

f = open(fname, "w", encoding='UTF8')
writer = csv.writer(f)
writer.writerow(csv_header)

smartFolderNamePREFIX = "CX-CDC"
FolderID_list = []

def get_data(base_url, headers, payload):
    response = requests.request("GET", base_url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")

def api_calls():
    # The Smart Folder does not have a parent Smart Folder
    region = "us-1"
    api_key = "5BAB243A-4310-4EBE-81C7-E5FDDF6D5292:4B39AB66-A58A-A383-0074-CE5DB6D88D1A:UTF6P7LwyZQUqlX8PJ4/nplbeZ/HUriCr+2dnS5Nlmw="
    payload = {}
    headers = {
    'api-version': 'v1',
    'Accept': 'application/json',
    'api-secret-key': api_key
    }
    #base_url = '<DSM>' #if you are using Deep Security 
    base_url = 'https://workload.'+region+'.cloudone.trendmicro.com/api/smartfolders' #if you are using Cloud One Workload Security

    output = get_data(base_url, headers, payload)
    tprint = json.dumps(output, indent=4, sort_keys=True)
    dprint = json.loads(tprint)
    return dprint

def parsing_smartFolders(output):
    #parsing the smartFolders to get only the smartFolders that have a parentSmartFolderID and the name of the smartFolder starts with the prefix
    for i in output['smartFolders']:
        #print(f"[DEBUG][START] i: {i}")
        #print(f"[DEGUB][ln 41] dprint: {dprint}")
        #what we will need to start the checks and for the output
        parentSmartFolderID = ""
        sFolderID = str(i['ID'])
        sFolderNAME = str(i['name'])
        psftype = str(i['type'])
        if parentSmartFolderID == "":
            if sFolderNAME.startswith(smartFolderNamePREFIX):
                sFolderID = str(i['ID'])
                sFolderNAME = str(i['name'])
                #write the data in a CSV row
                FolderID_list.append([sFolderID])
                writer.writerow([sFolderID,sFolderNAME,psftype,parentSmartFolderID])
            else:
                if 'parentSmartFolderID' in i:
                    parentSmartFolderID= str(i['parentSmartFolderID'])
                    for k in FolderID_list:
                        if parentSmartFolderID in k:
                            sFolderID = str(i['ID'])
                            sFolderNAME = str(i['name'])
                            psftype = str(i['type'])
                            FolderID_list.append([sFolderID])
                            writer.writerow([sFolderID,sFolderNAME,psftype,parentSmartFolderID])
    f.close()

output = api_calls()
parsing_smartFolders(output)

print(f"Number of Smart Folders: {len(FolderID_list)}")
print(f"Check the file: {fname}")

