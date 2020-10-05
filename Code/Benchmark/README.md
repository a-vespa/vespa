# Benchmark

## Instructions

1. Create a **python 3.6** virtual env using `conda` or `virtualenv`

2. Install all the dependencies:

   ```
   pip install -r requirements.txt
   ```

## Requirements

1. Update username, password and api key in [`ezzybills.py`](extractor/ezzybills.py).
   
   Note: [`click here`](https://www.ezzybills.com/api/) for instructions on how to get API key.
   ```
   # Line No - 11, 12
   ...
   api_key = {'APIKey': ''}
   payload = {'user': '', 'pwd': '', 'APIKey': ''}
   ...
   ...
   ```

   
2. Update MSFR endpoint, model id, post url and apim key in [`ms_form_recognizer.py`](extractor/ms_form_recognizer.py).
   
   Note: Create a form-recognizer endpoint using Azure account and train a custom model with labels. [`click here`](https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/label-tool?tabs=v2-0) for the training instructions. For the prediction use same model id in [`ms_form_recognizer.py`](extractor/ms_form_recognizer.py).
   ```
   # Line No - 9, 10, 11, 12
   ...
   endpoint = "https://benchmarking-invoice-extraction.cognitiveservices.azure.com/"
   model_id = "ccdc72bf-86ef-45f4-a4e5-cf74a489b234"
   post_url = endpoint + "/formrecognizer/v2.0/custom/models/ccdc72bf-86ef-45f4-a4e5-cf74a489b234/analyze"
   apim_key = "d060ca60439f4b639b29be634ee356a3"
   ...
   ...
   ```

3. Update Rossum endpoint and API Authentication Token in [`rossum.py`](Code/Benchmark/extractor/rossum.py).

   Note: Create a rossum account and using these credentials, Run the following command to get the API Token.
   ```
   curl -s -H 'Content-Type: application/json' -d '{"username": "east-west-trading-co@elis.rossum.ai", "password":"aCo2ohghBo8Oghai"}' 'https://api.elis.rossum.ai/v1/auth/login'

   # Output 
   # {"key": "db313f24f5738c8e04635e036ec8a45cdd6d6b03"}
   ```

   ```
   # Line No - 11 - rossum.py
   ...
   url = "https://api.elis.rossum.ai/v1/queues/34281/upload"
   token = 'token a94ff2e6994a8d09661cb5dcc555e0911943a56d'
   ...
   ...
   ```

4. Update Sypht API Authentication Token in [`sypht`](extractor/sypht.py).
   
   Note: [`click here`](https://docs.sypht.com/#section/Authentication) for instructions on how to get Authentication Token.
   ```
   # Line No - 16
   ...
       headers = {
       'Accept' : 'application/json',
       'Authorization' : 'Bearer eyJhbGciOiJSUzI1NiIsInR5c
      }
   ...
   ...
   ```
### Ground Truth
   
   Ground truth file should be created at this location ```ground_truth/invoice_ground_truth.csv```
   
   Sample Ground truth csv:
   ```
   document_name,Invoice Number,Invoice From,Invoice To,Invoice Date,Due date,Total Amount
   Invoice1.pdf,10280,"Kris-Heidenreich, Corporation",ABC Inc,8/20/2018,"['9/20/2018','Net 30']",62.86
   Invoice2.pdf,10281,"Lang-Hilpert Inc",Rogahn and Sons LLP,13 August 2015,"['Net 30']",123.69
   ```
   Note: Ground truth file is required to execute benchmark script.

## How to use?

Run the following script to start the benchmark.

```
python run.py

```
