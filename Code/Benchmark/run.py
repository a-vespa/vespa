import json
import os
import time

import compare.label_generator_ezzybills as ezzybills_comparator
import compare.label_generator_msfr as msfr_comparator
import compare.label_generator_rossum as rossum_comparator
import compare.label_generator_sypht as sypht_comparator
import compare.label_generator_vespa as vespa_comparator
import compare.precision as accuracy
import extractor.ezzybills as ezzybills_extractor
import extractor.ms_form_recognizer as ms_form_recognizer_extractor
import extractor.rossum as rossum_extractor
import extractor.sypht as sypht_extractor
import requests


if __name__ == "__main__":
    path = "../../Datasets/Invoices/"
    for r, d, f in os.walk(path):
        for file in f:
            ezzybills_extractor.get_extraction_details(r, file)
            rossum_extractor.get_extraction_details(r, file)
            sypht_extractor.get_extraction_details(r, file)
            ms_form_recognizer_extractor.extract_invocie_details(r, file)
    rossum_comparator.run_comparison()
    ezzybills_comparator.run_comparison()
    sypht_comparator.run_comparison()
    msfr_comparator.run_comparison()
    accuracy.get_f1score()
