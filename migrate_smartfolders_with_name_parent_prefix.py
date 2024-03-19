import requests
import json
import csv

#CSV Files
#file to read as input
fname = "smartFoldersNameParentPrefix.csv"
f = open(fname, "r", encoding='UTF8')
#file to write as output with the migration objects and errors
mfname = "MigratedSmartFolders.csv"

#CSV Headers with the results 
mcsv_header = ['ID', 'name', 'parentSmartFolderID', 'migration status','oldID','error code', 'error message']
mf = open(mfname, "w", encoding='UTF8')
writer = csv.writer(mf)
writer.writerow(mcsv_header)
mf.close()

#API information
#Deep Security Smart Folder (from where you will migrate the SmartFolders)
dsm_region = "us-1" # Only used from migrate from SaaS/Cloud to SaaS/Cloud.
dsm_method = "GET"
dsm_api_key = "<Your DSM API key>" #DSM API Key. Only ready permissions are required.
dsm_payload = {}
dsm_headers = {
'api-version': 'v1',
'Accept': 'application/json',
'api-secret-key': dsm_api_key
}
dsm_base_url_dsm = 'https://workload.'+dsm_region+'.cloudone.trendmicro.com/api/smartfolders/'

#Cloud One Workload Security (to where you will migrate the SmartFolders)
c1ws_region = "us-1" #check the Cloud One region for your tenant
c1ws_method = "POST"
c1ws_api_key = "<Your Cloud One or Vision One Endpoint Security Server & Workload API key>" #This API key needs write permission since it will create smartFolders
c1ws_headers = {
'api-version': 'v1',
'Content-Type': 'application/json',
'Accept': 'application/json',
'api-secret-key': c1ws_api_key
}
c1ws_base_url = 'https://workload.'+c1ws_region+'.cloudone.trendmicro.com/api/smartfolders'


def get_data(http_method, base_url, headers, payload):
    
    response = requests.request(http_method, base_url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        error_code = str(response.status_code)
        error_text = str(response.text)
        error_text = error_text.strip('{"message":"')
        error_text = error_text.strip('""}')
        error_dict = {'code': error_code, 'message': error_text}
        return error_dict

def api_call_DSM(sfids):
    payload = {}

    for i in sfids:
        url_api_request = dsm_base_url_dsm + i
        output = get_data(dsm_method,url_api_request, dsm_headers, payload)
        src_parentSmartFolderID = ""
        if 'parentSmartFolderID' in output:
            src_parentSmartFolderID= str(output['parentSmartFolderID'])
            dstParentFolderName = str(output['name'])
            src_search = search_src_smartfoldersNAMEs(src_parentSmartFolderID)
            dst_search = search_dst_parent_smartfoldersID(src_search)
            ddd = output
            ddd.update({'parentSmartFolderID': dst_search})
            migrate = api_call_C1WS(output)
        else:            
            print("\nMigrating SmartFolder ID "+i+" to Cloud One Workload Security:")
            
            migrate = api_call_C1WS(output)
            print ("migrate: "+str(migrate))
    f.close()
    mf.close()


def api_call_C1WS(payload):
    payload = json.dumps(payload) #convert dict to json
    dict_payload = json.loads(payload) #convert json to dict

    output = get_data(c1ws_method,c1ws_base_url,c1ws_headers, payload)
    gd_out_validation = str(list(output.keys())[0])
    print("\napi_call_C1WS output: "+str(output)+"\n")
    ocode = ""
    omessage = ""
    foparentSmartFolderID = ""

    if gd_out_validation == 'code':
        migration_status = 'failed'
        oID=""
        oldfoparentSmartFolderID = ""
        ocode =str(list(output.values())[0])
        omessage = str(list(output.values())[1])
        oldname = str(dict_payload['name'])
        oldtype = str(dict_payload['type'])
        oldID = str(dict_payload['ID'])
        amf = open(mfname, "a", encoding='UTF8')
        writer = csv.writer(amf)
        writer.writerow([oID, oldname, oldfoparentSmartFolderID, migration_status,oldID, ocode, omessage])
        mf.close()
    else:
        migration_status = 'success'
        if (list(output.keys())[0]) == 'name':
            oname =str(list(output.values())[0])
            otype = str(list(output.values())[1])
            oID = str(list(output.values())[-1])
        
        oID = str(list(output.values())[-1])
        oldID = str(dict_payload['ID'])
        #print("payload['ID']: "+oldID)
        amf = open(mfname, "a", encoding='UTF8')
        writer = csv.writer(amf)
        writer.writerow([oID, oname, foparentSmartFolderID, migration_status, oldID, ocode, omessage])
        mf.close()
    return output

def list_smartfoldersIDs():
    reader = csv.reader(f)
    aggregated_data = []
    for row in reader:
        if row[0] == 'ID':
            continue
        sfid = str(row[0])
        aggregated_data.append(sfid)
    f.close()
    return aggregated_data

def search_src_smartfoldersNAMEs(srcParentFolderID):
    f = open(fname, "r", encoding='UTF8')
    srcParentFolderName = ""
    srcParentFolderID = str(srcParentFolderID)
    nmreader = csv.reader(f)
    for row in nmreader:
        if row[0] == srcParentFolderID:
            srcFolderName = str(row[1])
            break
    f.close()
    return srcFolderName

def search_dst_parent_smartfoldersID(dstParentFolderNAME):
    dstParentFolderID = ""
    dstParentFolderNAME = str(dstParentFolderNAME)

    payload = json.dumps({
    "maxItems": "100",
    "searchCriteria": [
        {
        "fieldName": "name",
        "stringTest": "equal",
        "stringValue": dstParentFolderNAME
        }
    ]
    })

    dst_PFID_output = get_data("POST", c1ws_base_url+"/search", c1ws_headers, payload)

    dst_PFID_output = str(dst_PFID_output)
    dst_PFID_output = dst_PFID_output.split(",")
    dst_PFID_output = str(dst_PFID_output)
    dst_PFID_output = dst_PFID_output.split(":")
    dst_PFID_output = str(dst_PFID_output[-1])
    dst_PFID_output = dst_PFID_output.strip('}]}"')
    dstParentFolderID = dst_PFID_output
    return dstParentFolderID

print("PHASE 1 ")
print('Listing Smartfolders IDs presented in the file '+fname+': ')
smartFolderID_list =  list_smartfoldersIDs()
print(smartFolderID_list)  # print the response
print('\n')

print("PHASE 2 ")
print('Describing & Migrating Smartfolders IDs presented in the file '+fname+': ')
dsmartfolders = api_call_DSM(smartFolderID_list)
print(dsmartfolders)  # print the response
print('\n')