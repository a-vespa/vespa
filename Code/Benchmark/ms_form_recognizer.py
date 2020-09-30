########### Python Form Recognizer Async Analyze #############
import json
import time
from requests import get, post
import os
import time

# Endpoint URL
endpoint = "https://benchmarking-invoice-extraction.cognitiveservices.azure.com/"
model_id = "ccdc72bf-86ef-45f4-a4e5-cf74a489b234"
post_url = endpoint + "/formrecognizer/v2.0/custom/models/ccdc72bf-86ef-45f4-a4e5-cf74a489b234/analyze"
apim_key = "d060ca60439f4b639b29be634ee356a3"

params = {
    "includeTextDetails": True
}

headers = {
    # Request headers
    'Content-Type': 'application/pdf',
    'Ocp-Apim-Subscription-Key': apim_key,
}

def extract_invocie_details(filepath, file):
    with open(os.path.join(filepath,file), "rb") as f:
        data_bytes = f.read()

    try:
        start_time = time.time()
        resp = post(url = post_url, data = data_bytes, headers = headers, params = params)
        if resp.status_code != 202:
            # print("POST analyze failed:\n%s" % json.dumps(resp.json()))
            # quit()
            return
        # print("POST analyze succeeded:\n%s" % resp.headers)
        get_url = resp.headers["operation-location"]

        n_tries = 15
        n_try = 0
        wait_sec = 5
        max_wait_sec = 60
        while n_try < n_tries:
            try:
                resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": apim_key})
                resp_json = resp.json()
                if resp.status_code != 200:
                    print("GET analyze results failed:\n%s" % json.dumps(resp_json))
                    # quit()
                    return
                status = resp_json["status"]
                if status == "succeeded":
                    keyvalue = resp_json["analyzeResult"]["documentResults"]
                    
                    keyvaluepair=[]
                    keyvalueitem={}
                    for key, item in keyvalue[0]["fields"].items():
                        
                        if key =="Due Date":
                            if item != None:
                                keyvalueitem["Due Date"] = item["text"]
                            else:
                                keyvalueitem["Due Date"] = "NA"
                        elif key == "Invocie Number":
                            if item != None:
                                keyvalueitem["Invocie Number"] = item["text"]
                            else:
                                 keyvalueitem["Invocie Number"] ="NA"
                        elif key == "Invoice To":
                            if item != None:
                                keyvalueitem["Invoice To"] = item["text"]
                            else:
                                keyvalueitem["Invoice To"] = "NA"
                        elif key == "Invoice Date":
                            if item != None:
                                keyvalueitem["Invoice Date"] = item["text"]
                            else:
                                keyvalueitem["Invoice Date"] = "NA"
                        elif key == "Invoice From":
                            if item != None:
                                keyvalueitem["Invoice From"] = item["text"]
                            else:
                                keyvalueitem["Invoice From"] = "NA"
                        elif key == "Payment terms":
                            if item != None:
                                keyvalueitem["Payment terms"] = item["text"]
                            else:
                                keyvalueitem["Payment terms"]= "NA"
                        elif key == "Total Amount":
                            if item != None:
                                keyvalueitem["Total Amount"] = item["text"]
                            else:
                                keyvalueitem["Total Amount"]= "NA"
                        keyvalueitem["document name"] = file
                        keyvalueitem["exreaction_time"] = time.time() - start_time
                    with open('fr_result.json', 'r') as outfile:
                        fr_extraction = json.load(outfile)
                        fr_extraction.append(resp_json)

                    with open('fr_result.json', 'w') as outfile:
                        json.dump(fr_extraction, outfile)

                    with open('field_wise_result.json' , 'r') as json_file:
                        field_wise_extraction = json.load(json_file)
                        field_wise_extraction.append(keyvalueitem)

                    with open('field_wise_result.json', 'w') as outfile:
                        json.dump(field_wise_extraction, outfile)

                    print("Analysis succeeded:\n")
                    return
                if status == "failed":
                    print("Analysis failed:\n", file)
                    #quit()
                # Analysis still running. Wait and retry.
                time.sleep(wait_sec)
                n_try += 1
                wait_sec = min(2*wait_sec, max_wait_sec)     
            except Exception as e:
                msg = "GET analyze results failed:\n%s" % str(e)
                print(msg)
                return
        print("Analyze operation did not complete within the allocated time.")

    except Exception as e:
        print("POST analyze failed:\n%s" % str(e))
        # quit() 
        return