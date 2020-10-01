import requests  
import json 
import os 
import time
payload = {}   

def get_extraction_details(filepath ,file):
    try:
        start_time = time.time()
        url = "https://api.elis.rossum.ai/v1/queues/34281/upload"
        token = 'token a94ff2e6994a8d09661cb5dcc555e0911943a56d'
        headers = {
            'Accept' : 'application/json',
            'Authorization' : token}
        files = {'content' : open(os.path.join(filepath,file) ,'rb')}
        response = requests.request('POST' , url, headers=headers,data=payload , files=files, allow_redirects=False ,verify=False)
        json_data = json.loads(response.text)
        is_reviewed=False
        while is_reviewed==False:
            statusurl = json_data["annotation"]
            headers = {
            'Authorization' : token}
            response1 = requests.get(statusurl, headers=headers, allow_redirects=False ,verify=False)
            status_json = json.loads(response1.text)
            if status_json["status"] == "to_review":
                extraction_time = time.time() - start_time
                is_reviewed=True
                extraction_details_url = 'https://api.elis.rossum.ai/v1/queues/34281/export?status=to_review&format=json&id='+ str(status_json["id"])
                extraction_details = requests.get(extraction_details_url, headers=headers, allow_redirects=False ,verify=False)
                rossum_extraction =  json.loads(extraction_details.text)
                rossum_extraction["result"] = rossum_extraction["results"][0]
                rossum_extraction["extraction_time"] = extraction_time
                rossum_extraction["document_name"] = file
                item = {}
                item["GST"] = "NA"
                item["document_name"] = rossum_extraction["document_name"]
                item["extraction-time"] = rossum_extraction["extraction_time"]
                for i in rossum_extraction["result"]["content"]:
                    if i["schema_id"] == "invoice_details_section":
                        for j in i["children"]:
                            if j["schema_id"] == "date_issue":
                                item["Invoice Date"] = j["value"]
                            elif j["schema_id"] == "date_due":
                                item["Due date"] = j["value"]
                            elif j["schema_id"] == "invoice_id":
                                item["Invoice Number"] = j["value"]
                    elif i["schema_id"] == "totals_section":
                        for j in i["children"]:
                            if j["schema_id"] == "amount_due":
                                item["Total Amount"] = j["value"]
                            elif j["schema_id"] == "tax_details":
                                for k in j["children"]:
                                    if k["schema_id"] == "tax_detail":
                                        if len(k["children"]) >0:
                                            item["GST"] = k["children"][0]["value"]
                                        else:
                                            item["GST"] = "NA"
                    elif i["schema_id"] == "payment_info_section":
                        for j in i["children"]:
                            if j["schema_id"] == "terms":
                                item["net_terms"] = j["value"]               
                    elif i["schema_id"] == "vendor_section":
                        for j in i["children"]:
                            if j["schema_id"] == "sender_name":
                                item["Invoice From"] = j["value"]
                            elif j["schema_id"] == "recipient_name":
                                item["Invoice To"] = j["value"]       

                with open('extraction_result/rossum/result.json', 'r') as outfile:
                        rossum_extraction = json.load(outfile)
                        rossum_extraction.append(item)
                with open('extraction_result/rossum/result.json' , 'w') as json_file:
                    json.dump(rossum_extraction , json_file) 

    except:
        pass  
    