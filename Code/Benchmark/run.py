import os
import json
import time
import requests
import ezzybills as ezzybillsextraction
import rossum as rossumextraction
import sypht as syphtextraction
import ms_form_recognizer as ms_form_recognizer
import extraction_comparison.label_generator_ezzybills as ezzybills
import extraction_comparison.label_generator_rossum as rossum
import extraction_comparison.label_generator_sypht as sypht
import extraction_comparison.label_generator_vespa as vespa
import extraction_comparison.label_generator_msfr as msfr
if __name__ == "__main__":
    path= "/mnt/d/R&D/Project/Vespa Benchmark/Invoice/ALL/"
    for r ,d ,f in os.walk(path):
        for file in f:
            ezzybillsextraction.get_extraction_details(r, file)
            rossumextraction.get_extraction_details(r, file)
            syphtextraction.get_extraction_details(r, file)
            ms_form_recognizer.extract_invocie_details(r, file)
    rossum.run_comparison()
    ezzybills.run_comparison()
    sypht.run_comparison()
    vespa.run_comparison()
    msfr.run_comparison()