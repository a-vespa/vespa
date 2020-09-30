import csv
import json
import logging
import re
import moment 
import pandas as pd
from fuzzywuzzy import fuzz
import datetime
from decimal import Decimal
LOCALE= "US"
logging.basicConfig(filename="extract_validator.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class ExtractValidator():
    """
    The goal is to have a "solid" validator to identify a VESPA extracted answer is a
        Exact Match=EM
        Partial Match=PM
        NA (Cannot Extract)=NA
        Wrong (Extracted wrong values)=WRONG

    What do we mean by "solid" ? We would like to make validator as accurate as possible i.e. with
    minimum False Positives.
    """

    def partial_score(self, gt, answer):
        p_rt = fuzz.partial_ratio(gt, answer)
        p_tsort_rt = fuzz.partial_token_sort_ratio(gt, answer)
        p_tset_rt = fuzz.partial_token_set_ratio(gt, answer)

        return (p_rt + p_tsort_rt + p_tset_rt) / 3

    def len_diff(self, gt, answer):
        return abs(len(gt)-len(answer))

    def max(self, gt, answer):
        return (gt, answer) if len(gt) > len(answer) else (answer, gt)

    def is_substr(self, super_str, sub_str):
        return True if super_str.lower().find(sub_str.lower()) >= 0 else False

    def is_date(self, field):
        return True if field.lower().find('date') >= 0 else False

    def is_amount(self, field):
        return True if field.lower() in ['total amount'] else False

    def is_tax(self, field):
        return True if field.lower() in ['late payment charges', 'gst'] else False

    def cleanup(self, gt, answer, field):
        if self.is_date(field):
            if gt.lower().find('days') == -1:
                if LOCALE =="SG":
                    if re.match("^\d{1,2}\/\d{1,2}\/\d{4}$", gt):
                        format_str = '%d/%m/%Y' # The format
                        datetime_obj = datetime.datetime.strptime(gt, format_str)
                        gt = str(datetime_obj.date())
                    elif  re.match("^\d{1,2} \d{1,2} \d{4}$", gt):
                        format_str = '%d %m %Y' # The format
                        datetime_obj = datetime.datetime.strptime(gt, format_str)
                        gt =  str(datetime_obj.date())
                    elif re.match("^\d{1,2}-\d{1,2}-\d{4}$", gt):
                        format_str = '%d-%m-%Y' # The format
                        datetime_obj = datetime.datetime.strptime(gt, format_str)
                        gt =  str(datetime_obj.date())
                    elif re.match("^\d{1,2}.\d{1,2}.\d{4}$", gt):
                        format_str = '%d.%m.%Y' # The format
                        datetime_obj = datetime.datetime.strptime(gt, format_str)
                        gt =  str(datetime_obj.date())
                    else:
                        try:
                            dategt = moment.date(gt)
                            dategt = str(dategt)
                            gt = dategt[:10]
                        except:
                            pass
                elif LOCALE =="US":
                    try:
                        if re.match("^\d{1,2}\/\d{1,2}\/\d{4}$", gt):
                            format_str = '%m/%d/%Y' # The format
                            datetime_obj = datetime.datetime.strptime(gt, format_str)
                            gt = str(datetime_obj.date())
                        elif  re.match("^\d{1,2} \d{1,2} \d{4}$", gt):
                            format_str = '%m %d %Y' # The format
                            datetime_obj = datetime.datetime.strptime(gt, format_str)
                            gt =  str(datetime_obj.date())
                        elif re.match("^\d{1,2}-\d{1,2}-\d{4}$", gt):
                            format_str = '%m-%d-%Y' # The format
                            datetime_obj = datetime.datetime.strptime(gt, format_str)
                            gt =  str(datetime_obj.date())
                        elif re.match("^\d{1,2}.\d{1,2}.\d{4}$", gt):
                            format_str = '%d.%m.%Y' # The format
                            datetime_obj = datetime.datetime.strptime(gt, format_str)
                            gt =  str(datetime_obj.date())
                        else:
                            try:
                                dategt = moment.date(gt)
                                dategt = str(dategt)
                                gt = dategt[:10]
                            except:
                                pass
                    except:
                            dategt = moment.date(gt)
                            dategt = str(dategt)
                            gt = dategt[:10]
                gt, answer = re.sub(
                    "[\/\-\.]", " ", gt), re.sub("[\/\-\.]", " ", answer)
        elif self.is_amount(field):

            gt, answer = re.sub("[\$\,]", "", gt), re.sub("[\$\,]", "", str(answer))
            gt = float(gt)
            answer = float(answer)
            d1 = Decimal (gt)
            d2 = Decimal (answer)
            gt = round(d1, 2)
            answer = round(d2, 2)
            gt = str(gt)
            answer = str(answer)
            print(gt ,answer )
        return gt.lower().strip(), answer.lower().strip()

    def isEM(self, gt, answer, field):
        if self.is_date(field):
            #if fuzz.token_sort_ratio(gt, answer) == 100 or (answer == "na" and gt == ""):
            if (gt==answer) or (answer == "na" and gt == ""):
                return True
        elif self.is_amount(field):
            if fuzz.token_sort_ratio(gt, answer) == 100 or (answer == "na" and gt == ""):
                return True
        else:
            if fuzz.token_sort_ratio(gt, answer) >= 90 or (answer == "na" and gt == ""):
                return True
        return False

    def isNA(self, gt, answer, field):
        if answer == "na":
            return True
        return False

    def isPM(self, gt, answer, field):
        if self.is_date(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 80:
                super_str, sub_str = self.max(gt, answer)
                if not self.is_substr(super_str, sub_str):
                    return False
                return True

        elif self.is_amount(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 70:
                if len(answer) > len(gt) and gt == "0":
                    return False
                elif len(answer) > len(gt) and self.is_substr(answer, "{:.2f}".format(float(gt))):
                    return True
                elif len(gt) > len(answer) and str(int(float(gt))) == answer:
                    return True
                return False
            else:
                return False

        elif self.is_tax(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 70:
                if len(answer) > len(gt) and self.is_substr(answer, gt):
                    return True
                return False
            else:
                return False

        else:
            if fuzz.token_sort_ratio(gt, answer) < 90 and self.partial_score(gt, answer) > 60:
                return True
        return False

    def isWRONG(self, gt, answer, field):
        if self.is_date(field):
            if self.len_diff(gt, answer) == 0 and fuzz.token_sort_ratio(gt, answer) < 100:
                return True
            elif self.len_diff(gt, answer) > 0 and fuzz.token_sort_ratio(gt, answer) < 50:
                return True
        else:
            if fuzz.token_sort_ratio(gt, answer) < 50 and self.partial_score(gt, answer) < 60:
                return True
        return False

    def debug_lines(self, doc, field, gt, answer):
        len_diff = abs(len(gt)-len(answer))
        p_rt = fuzz.partial_ratio(gt, answer)
        p_tsort_rt = fuzz.partial_token_sort_ratio(gt, answer)
        p_tset_rt = fuzz.partial_token_set_ratio(gt, answer)
        tsort_rt = fuzz.token_sort_ratio(gt, answer)
        tset_rt = fuzz.token_set_ratio(gt, answer)

        return [doc, field, gt, answer, len_diff,  p_rt, p_tsort_rt, p_tset_rt, tsort_rt, tset_rt]

    def get_ocr_quality(self, document_name, master):
        for hit in master['hits']['hits']:
            if hit['_source']['document_name'] == document_name:
                try:
                    ocr_quality = hit['_source']['ocr_quality_matrix']['mean']
                except:
                    logging.error(
                        "Exception fetching OCR Quality, initializing it as 99")
                    ocr_quality = 99
                break
        return ocr_quality

    def secure_file_name(self, doc):
        return doc.replace(" ", "_")

    def gt_doc_name(self, document_name, gt):
        gt_document_name = ""
        score = 0
        for _ in gt.itertuples():
            lhs = self.secure_file_name(_.document_name)
            rhs = self.secure_file_name(document_name)

            if lhs == rhs:
                gt_document_name = _.document_name
                return gt_document_name

        return gt_document_name

    def run(self, locale, knowledge, gt, columns):

        gt.fillna("", inplace=True)
        results = []
        debug_lines = []

        for hit in knowledge:
            document_name = hit['document_name']

            gt_document_name = self.gt_doc_name(document_name, gt)

            if len(gt_document_name) == 0:
                logging.info("="*71)
                logging.error("Document: {} | GT: {}".format(
                    document_name, "Failed to find ground truth"))
                logging.info("="*71)
                continue

            logging.info("="*71)
            logging.info("Document: {} | GT: {}".format(
                document_name, gt_document_name))
            logging.info("="*71)

            em = 0  # Exact match
            na = 0  # NA
            pm = 0  # Partial match
            wrong = 0  # Wrong answer
            ocr_quality = 0


            for k in columns:
                if k !="document_name":
                    lhs = gt[gt['document_name'] ==
                             gt_document_name][k].values[0]
                    lhs_temp = lhs
                    rhs = hit[k]

                    lhs, rhs = self.cleanup(lhs, rhs, k)

                    if self.isEM(lhs, rhs, k):
                        em += 1
                        label = 'EM'
                    elif self.isNA(lhs, rhs, k):
                        na += 1
                        label = 'NA'
                    elif self.isPM(lhs, rhs, k):
                        pm += 1
                        label = 'PM'
                    else:
                        wrong += 1
                        label = 'Wrong'
                    lhs = gt[gt['document_name'] ==
                             gt_document_name][k].values[0]
                    debug_lines.append(self.debug_lines(
                        document_name, k, lhs, rhs))
                    debug_lines[-1].append("Sypht")
                    debug_lines[-1].append(label)

                    logging.debug("Field: {} | gt: {} | answer: {} | label: {}".format(
                        k, lhs, rhs, label))

            logging.info("="*71)
            results.append([document_name, em, pm, na, wrong,ocr_quality])

        return results, debug_lines


def generate_score(x, weights, min_val, max_val):
    """
    This function calculates a weighted score and
    do min max scaling on the score
    """
    score = x['EM'] * weights['EM'] - \
        (x['PM'] * weights['PM'] + x['NA'] *
         weights['NA'] + x['Wrong'] * weights['Wrong'])
    return ((score - min_val) / (max_val - min_val))


def generate_label(score, slabs):
    """
    This function labels data based on the score and the
    respective slab the score falls into
    """
    for slab in slabs:
        if slab["lower"] <= score < slab["upper"]:
            return slab["label"]


def main(locale, knowledge, gt, columns):
    with open('comparison_script/jsons/config.json') as f:
        config = json.load(f)

    slabs = config["slabs"][locale]
    weights = config["weights"]
    min_val = config["min"][locale]
    max_val = config["max"][locale]

    ev = ExtractValidator()
    results, debug_lines = ev.run(locale, knowledge, gt, columns)
    file_mode = 'w'
    with open("comparison_script/jsons/Ezzybill/debug_lines.csv", file_mode) as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        if file_mode == "w":
            writer.writerow(['doc', 'field', 'gt', 'answer', 'len_diff', 'p_rt', 'p_tsort_rt',
                             'p_tset_rt', 'tsort_rt', 'tset_rt', 'origin', 'label'])
        writer.writerows(debug_lines)

    df = pd.DataFrame(results, columns=['filename', 'EM', 'PM', 'NA',
                                        'Wrong' ,'OCR_Quality_Mean'])

    df['score'] = df.apply(lambda x: generate_score(
        x, weights, min_val, max_val), axis=1)
    df['label'] = df.apply(lambda x: generate_label(x['score'], slabs), axis=1)

    return df

def run_comparison():
    gt_file_path = "comparison_script/ground_truth/us_invoice_ground_truth.csv"
    knowledge_file_path = "comparison_script/jsons/Ezzybill/result.json"
    columns = [
        'document_name',
        'Invoice Number',
        'Total Amount',
        'Invoice Date',
        'Due date',
        'Invoice From'
    ]

    gt = pd.read_csv(gt_file_path)[columns]
    knowledge = json.load(open(knowledge_file_path))
    df = main("SG", knowledge, gt, columns)
    df.to_csv("comparison_script/jsons/Ezzybill/training_data.csv", index=None)
