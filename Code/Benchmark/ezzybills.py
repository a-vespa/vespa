__requires__ = "Request module (https://github.com/requests/requests)"

import requests
import json
from time import sleep
import os
import time
from datetime import datetime
url = 'https://app.ezzydoc.com/EzzyService.svc/Rest'
api_key = {'APIKey': ''}
payload = {'user': '', 'pwd': '', 'APIKey': ''}


def get_extraction_details(filepath , file):
    try:
        start_time = time.time()
        r = requests.get(url + '/Login', params=payload,verify=False )
        start_time = time.time()
        with open(os.path.join(filepath,file), 'rb') as img_file:
            print(os.path.join(filepath,file))
            img_name = file
            data = img_file.read()
            b = bytearray(data)
            li = []
            for i in b:
                li.append(i)
            raw_data = {"PictureName": file, "PictureStream": li}
            json_data = json.dumps(raw_data)
            r2 = requests.post(
                "https://app.ezzydoc.com/EzzyService.svc/Rest/uploadInvoiceImage",
                data=json_data, cookies=r.cookies, params=api_key, headers={'Content-Type': 'application/json'},verify=False)
        
            invoiceID = str(r2.json().get("invoice_id"))
            print(r2.json())
        # Wait until invoice has been processed
        while True:
            r4 = requests.get(url + '/workflowStatus?invoiceid=' + invoiceID, cookies=r.cookies, params=api_key ,verify=False)
            completeBool = str(r4.json().get("complete"))
            print(r4.json())
            if completeBool == "True":
                break
            sleep(1)

        # Get invoice total
        r5 = requests.get(url + '/getInvoiceHeaderBlocks?invoiceid=' + invoiceID, cookies=r.cookies, params=api_key,verify=False)
        invoice_data = r5.json()
        invoice_data["filename"] = file
        invoice_data["exreaction_time"] = time.time() - start_time
    

        ezzebill_item ={}
        if invoice_data["invoiceForm"]["invoiceDate"] != None:
            timestamp = invoice_data["invoiceForm"]["invoiceDate"][6:19]
            if timestamp != None:
                dt = datetime.fromtimestamp(int(timestamp)/1000)  # using the local timezone
                ezzebill_item["Invoice Date"] = dt.strftime("%Y-%m-%d")
        else:
            ezzebill_item["Invoice Date"] = "NA"
        if invoice_data["invoiceForm"]["paymentDate"] != None:
            timestamp = invoice_data["invoiceForm"]["paymentDate"][6:19]
            if timestamp != None:
                dt = datetime.fromtimestamp(int(timestamp)/1000)  # using the local timezone
                ezzebill_item["Due date"] = dt.strftime("%Y-%m-%d")
                
        else:
            ezzebill_item["Due date"] = "NA"
        ezzebill_item["Invoice From"] =  invoice_data["invoiceForm"]["supplierName"]
        ezzebill_item["Total Amount"] = invoice_data["invoiceForm"]["invoiceTotal"]
        ezzebill_item["Invoice Number"] =  invoice_data["invoiceForm"]["invoiceNumber"]
        ezzebill_item["document_name"] =  invoice_data["filename"]

        with open('comparison_script/jsons/Ezzybill/result.json', 'r') as outfile:
            ezzybill_extraction = json.load(outfile)
            ezzybill_extraction.append(ezzebill_item)

        with open('comparison_script/jsons/Ezzybill/result.json', 'w') as outfile:
            json.dump(ezzybill_extraction, outfile)
    except:
        pass