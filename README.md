## **Zero-shot Task Transfer for Invoice Extraction via Class-aware QA Ensemble**

VESPA is a novel zero-shot system for a layout, locale, and domain agnostic document extraction. It works with form-like documents with unstructured information e.g. invoices, bills and receipts, long-form documents e.g. legal contracts and format-less documents e.g Annual Reports

**Contributions and empirical claims:**

We demonstrate the effectiveness of our system by evaluating on a closed corpus of real-world retail and tax invoices with multiple complex layouts, domains and geographies. The empirical evaluation shows that:

(1) Our system outperforms 4 commercial invoice solutions that use discriminatively trained models with architectures specifically crafted for invoice extraction. We extracted 6 fields with zero upfront human annotation and training with an **Avg. F1 of 87.50.**

(2) Our framework generalizes well on non-form-based documents like legal contracts and format-less documents like annual reports with **Avg. F1 of 81.2 and 86.42 respectively**

(3) Our class-aware QA ensemble (Avg. F1 87.50)  with diverse network architectures outperforms single QA models (Avg. F1 82.67).



## [Benchmarking](Code/Benchmark)


### Instructions

1. Create a **python 3.6** virtual env using `conda` or `virtualenv`

2. Install all the dependencies:

   ```
   pip install -r requirements.txt
   ```

### Requirements

1. Update username, password and api key in [`ezzybills.py`](Code/Benchmark/extractor/ezzybills.py).
   
   Note: [`click here`](https://www.ezzybills.com/api/) for instructions on how to get API key.
   ```
   # Line No - 11, 12
   ...
   api_key = {'APIKey': ''}
   payload = {'user': '', 'pwd': '', 'APIKey': ''}
   ...
   ...
   ```

   
2. Update MSFR endpoint, model id, post url and apim key in [`ms_form_recognizer.py`](Code/Benchmark/extractor/ms_form_recognizer.py).
   
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

4. Update Sypht API Authentication Token in [`sypht.py`](Code/Benchmark/extractor/sypht.py).
   
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
## Ground Truth
   
   Ground truth file should be created at this location ```ground_truth/invoice_ground_truth.csv```
   
   Sample Ground truth csv:
   ```
   document_name,Invoice Number,Invoice From,Invoice To,Invoice Date,Due date,Total Amount
   Invoice1.pdf,10280,"Kris-Heidenreich, Corporation",ABC Inc,8/20/2018,"['9/20/2018','Net 30']",62.86
   Invoice2.pdf,10281,"Lang-Hilpert Inc",Rogahn and Sons LLP,13 August 2015,"['Net 30']",123.69
   ```
   Note: Ground truth file is required to execute benchmark script.

### How to use?

Run the following script to start the benchmark.

```
python run.py

```

## FoI Config

Sample configurations for different document types

### Annual Reports
```
{
        "locale": "US",
        "domain": "finance",
        "document_type": "stakeholder reports",
        "field": "CEO",
        "field_type": "FOI",
        "keywords": ["chief executive officer",
                     "CEO",
                     "group chief executive"],
        "question_prefix": ["who is the"],
        "response_dtype": "ALPHA",
        "page_affinity": [],
        "validation_policy": [{"type": "NER", "entity": "PER"},
                              {"type": "CQ", "prefix": "who is"}],
        "probability_threshold": [0.2, 0.2, 0.2],
        "sort_results_by_confidence": 0,
        "status": 1
}
```

### Invoices
```
{
        "locale": "SG",
        "domain": "finance",
        "document_type": "invoice",
        "field_type": "FOI",
        "field": "Due date",
        "keywords": ["within what term net duration is the amount due",
                     "within what term duration the invoice is due",
                     "when is the charge due on",
                     "when is the amount payable due on",
                     "when is the due date",
                     "when is the invoice due date",
                     "what is the invoice due date"],
        "question_prefix": [""],
        "response_dtype": "DATE",
        "page_affinity": [1, 2],
        "validation_policy": [{"type": "NER", "entity": "DURATION"},
                              {"type": "NER", "entity": "DATE"}],
        "probability_threshold": [0.80, 0.80, 0.70, 0.70, 0.80, 0.80, 0.80],
        "sort_results_by_confidence": 1,
        "status": 1
}
```

### Master Service Agreement (Contract)
```
{
        "locale": "US",
        "domain": "legal",
        "document_type": "master service agreement",
        "field_type": "FOI",
        "field": "Effective MSA Date",
        "field_origin": [1],
        "keywords": ["effective date"],
        "question_prefix": ["what is the"],
        "response_dtype": "DATE",
        "page_affinity": [0, 1],
        "validation_policy": [{"type": "NER", "entity": "DATE"},
                              {"type": "NER", "entity": "CARDINAL"}],
        "probability_threshold": [0.2],
        "sort_results_by_confidence": 1,
        "status": 1
}
```



## [Parameters](Parameters)

### Single QA Finetuning Parameters
Parameters in this directory are used to finetune the respective QA models.

These parameters are sourced from their original sources.

* [`bart-large-qa-finetuned.md`](Parameters/single_qa_finetuning/bart-large-qa-finetuned.md)
* [`bert-base-uncased-qa-finetuned.md`](Parameters/single_qa_finetuning/bert-base-uncased-qa-finetuned.md)
* [`bert-large-uncased-whole-word-masking-qa-finetuned.md`](Parameters/single_qa_finetuning/bert-large-uncased-whole-word-masking-qa-finetuned.md)
* [`electra-large-discriminator-qa-finetuned.md`](Parameters/single_qa_finetuning/electra-large-discriminator-qa-finetuned.md)
* [`spanbert-base-qa-finetuned.md`](Parameters/single_qa_finetuning/spanbert-base-qa-finetuned.md)
