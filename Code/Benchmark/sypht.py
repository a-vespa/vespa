import os
import json
import time

import requests

def get_extraction_details(filepath, file):
    extracted_data ={}
    url = 'https://api.sypht.com/fileupload'
    payload = {'fieldSets' :'["sypht.invoice" ,"sypht.document",  "sypht.bill"]'}
    start_time = time.time()
    status=False
    files = {'fileToUpload' : open(os.path.join(filepath,file),'rb')}
    headers = {
        'Accept' : 'application/json',
        'Authorization' : 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1FVTBOalpGTmpNM1FqTXpOek00TURWR1JFTTJNREk1TXpFeFJUazVNVGxEUkRZMk1rRkJPUSJ9.eyJodHRwczovL2FwaS5zeXBodC5jb20vY29tcGFueUlkIjoiNzdkZGUyMGMtZjk1NS00ODlhLWIwZmMtYTAxNzVlMzZhZjVhIiwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5zeXBodC5jb20vIiwic3ViIjoiZTc1VmJQUHR0cFprQWprVGI5TkRhR3lVS01YWkZxbjBAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vYXBpLnN5cGh0LmNvbSIsImlhdCI6MTU5NTQ4NzkxMiwiZXhwIjoxNTk1NTc0MzEyLCJhenAiOiJlNzVWYlBQdHRwWmtBamtUYjlORGFHeVVLTVhaRnFuMCIsInNjb3BlIjoicmVzdWx0OmFsbCBmaWxldXBsb2FkOmFsbCBhZG1pbmlzdHJhdGlvbjpjb21wYW55IiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.tUEv9kqq_ZH1Yj8v1dtBqLs6TzdiOibsw7gDVnrzJ4j-BrXdq71zQ5ZAH0wUDGMFOOMio6JWUkAOUAjS7ZcAaMZ_4hN_LdxBAAbNn4Oscvk14UZ8ddL0rfzcwxae5WMTrvW5aiaTBSTV2vieX-dqRTrsJBWdtK4pHbyFuOzvP6Foec1xbIZIFEBiBQdVYnJpBIX0FltBYWfVEocdOyoBpFSRlSHaH6Kt1IyXurcfKygG1RNbeBn_E1htloEQox-Z1VF6YaplqFsYxgh2vMbOW0znMZLcqDljBkCS4DhlzJDpchQ24OsHnGj1ArXOvU5qLZUxrEAVuTBxisQqt4wuSQ'
       } 
    response = requests.request('POST' , url, headers=headers,data=payload , files=files, allow_redirects=False)
    json_data = json.loads(response.text)
    json_data["filename"] = file
    try:
        while status==False:            
            geturl = 'https://api.sypht.com/result/final/'+json_data["fileId"]
            response = requests.request('GET', geturl, headers = headers,  allow_redirects=False)
            extracted_data = json.loads(response.text)
            if extracted_data["status"] !="IN PROGRESS":
                extracted_data["exreaction_time"] = time.time() - start_time
                extracted_data["filename"] = file
                status=True
                item={}
                item["document_name"] = file.split('/')[-1]
                item["exreaction_time"] = extracted_data["exreaction_time"]
                for i in extracted_data["results"]["fields"]:
                    if i["name"]=="document.date":
                        item["Invoice Date"] =i["value"]
                    elif i["name"]=="invoice.amountDue":
                        item["Total Amount"] = i["value"]
                    elif i["name"]=="invoice.dueDate":
                        item["Due date"] = i["value"]
                    elif i["name"]=="document.referenceNo":
                        item["Invoice Number"]= i["value"]
                
                with open('comparison_script/jsons/Sypht/result.json', 'r') as readfile:
                    sypht_extraction = json.load(readfile)
                    sypht_extraction.append(item)
                
                with open('comparison_script/jsons/Sypht/result.json', 'w') as outfile:
                    json.dump(sypht_extraction, outfile)

    except:
        pass
    


