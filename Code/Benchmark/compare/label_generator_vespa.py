import csv
import json
import logging
import re

import pandas as pd
from fuzzywuzzy import fuzz


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

    def cleanup(self, gt, answers, field):
        if self.is_date(field):
            gt = re.sub("[\/\-\.]", " ", gt)
            answers = [re.sub("[\/\-\.]", " ", answer) for answer in answers]
            if field =="Due date":
                due_date_net_expression = r"\bnet\s+\d+"
                due_date_net_proxy = "{} days"
                net_matches = re.findall(due_date_net_expression, gt, flags=re.IGNORECASE)
                if any(net_matches):
                    gt = due_date_net_proxy.format(re.findall(r"\d+", net_matches[0])[0])
        elif self.is_amount(field):
            gt = re.sub("[\$\,]", "", gt)
            answers = [re.sub("[\$\,]", "", answer) for answer in answers]

        gt = gt.replace(']','').replace('[','')
        gt= gt.replace("'," ,"@#@")
        gts = gt.replace("'",'').split("@#@")
        return [gt.lower().strip()  for gt in gts], [answer.lower().strip() for answer in answers]

    def isEM(self, gts, answers, field):
        for gt in gts:
            for answer in answers:
                if self.is_date(field):
                    if fuzz.token_sort_ratio(gt, answer) == 100 or (answer == "na" and gt == ""):
                        return True,gt, answer
                elif self.is_amount(field):
                    if fuzz.token_sort_ratio(gt, answer) == 100 or (answer == "na" and gt == ""):
                        return True,gt, answer
                else:
                    if fuzz.token_sort_ratio(gt, answer) >= 90 or (answer == "na" and gt == ""):
                        return True,gt, answer
        return False,gts, None

    def isNA(self, gts, answers, field):
        for gt in gts:
            for answer in answers:
                if answer == "na" and len(answers) == 1:
                    return True,gt, answer
        return False,gts, None

    def _isPM(self, gt, answer, field):
        if self.is_date(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 80:
                super_str, sub_str = self.max(gt, answer)
                if not self.is_substr(super_str, sub_str):
                    return False, 0
                return True, self.partial_score(gt, answer)

        elif self.is_amount(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 70:
                if len(answer) > len(gt) and gt == "0":
                    return False, 0
                elif len(answer) > len(gt) and self.is_substr(answer, "{:.2f}".format(float(gt))):
                    return True, self.partial_score(gt, answer)
                elif len(gt) > len(answer) and str(int(float(gt))) == answer:
                    return True, self.partial_score(gt, answer)
                return False, 0
            else:
                return False, 0

        elif self.is_tax(field):
            if self.len_diff(gt, answer) > 0 and self.partial_score(gt, answer) >= 70:
                if len(answer) > len(gt) and self.is_substr(answer, gt):
                    return True, self.partial_score(gt, answer)
                return False, 0
            else:
                return False, 0

        else:
            if fuzz.token_sort_ratio(gt, answer) < 90 and self.partial_score(gt, answer) > 60:
                return True, self.partial_score(gt, answer)
        
        return False, 0

    def isPM(self, gts, answers, field):
        p_answer = None
        p_score = 0
        gt_value=None
        for gt in gts:
            for answer in answers:
                status, score = self._isPM(gt, answer, field)
                if status is True and score > p_score:
                    p_answer = answer
                    p_score = score
                    gt_value = gt
        return False if p_answer is None else True,gt_value, p_answer

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

    def run(self, locale, knowledge, master, gt, columns):

        gt.fillna("", inplace=True)
        results = []
        debug_lines = []

        for hit in filter(lambda x: x['_source']['locale'] == locale, knowledge['hits']['hits']):
            document_name = hit['_source']['document_name']

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
            ocr_quality = self.get_ocr_quality(document_name, master)

            for k in hit['_source']['data']:
                if k['field'] in columns:

                    lhs = gt[gt['document_name'] ==
                             gt_document_name][k['field']].values[0]
                    # rhs = k['ranswer']
                    rhs = [c['ranswer'] for c in k['candidates']]
                    
                    lhs, rhs = self.cleanup(lhs, rhs, k['field'])

                    if self.isEM(lhs, rhs, k['field'])[0]:
                        em += 1
                        label = 'EM'
                        _,lhs, rhs = self.isEM(lhs, rhs, k['field'])
                    elif self.isNA(lhs, rhs, k['field'])[0]:
                        na += 1
                        label = 'NA'
                        _,lhs, rhs = self.isNA(lhs, rhs, k['field'])
                    elif self.isPM(lhs, rhs, k['field'])[0]:
                        pm += 1
                        label = 'PM'
                        _,lhs, rhs = self.isPM(lhs, rhs, k['field'])
                    else:
                        wrong += 1
                        label = 'Wrong'
                        rhs = rhs[0]


                    logging.debug("Field: {} | gt: {} | answer: {} | label: {}".format(
                        k['field'], lhs, rhs, label))

                    debug_lines.append(self.debug_lines(
                        document_name, k['field'], lhs, rhs))
                    debug_lines[-1].append(k['updated_by'])
                    debug_lines[-1].append(label)

            logging.info("="*71)
            logging.info("EM: {} | PM: {} | NA: {} | Wrong: {} | OCR: {}".format(
                em, pm, na, wrong, ocr_quality))
            logging.info("="*71)
            results.append([document_name, em, pm, na, wrong, ocr_quality])

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

def main(locale, knowledge, master, gt, columns):
    with open('compare/config.json') as f:
        config = json.load(f)

    slabs = config["slabs"][locale]
    weights = config["weights"]
    min_val = config["min"][locale]
    max_val = config["max"][locale]

    ev = ExtractValidator()
    results, debug_lines = ev.run(locale, knowledge, master, gt, columns)
    file_mode = 'w'
    with open("extraction_result/vespa/debug_lines.csv", file_mode) as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        if file_mode == "w":
            writer.writerow(['doc', 'field', 'gt', 'answer', 'len_diff', 'p_rt', 'p_tsort_rt',
                             'p_tset_rt', 'tsort_rt', 'tset_rt', 'origin', 'label'])
        writer.writerows(debug_lines)

    df = pd.DataFrame(results, columns=['filename', 'EM', 'PM', 'NA',
                                        'Wrong', 'OCR_Quality_Mean'])

    df['score'] = df.apply(lambda x: generate_score(
        x, weights, min_val, max_val), axis=1)
    df['label'] = df.apply(lambda x: generate_label(x['score'], slabs), axis=1)

    return df


def run_comparison():
    gt_file_path = "ground_truth/invoice_ground_truth.csv"
    knowledge_file_path = "extraction_result/vespa/knowledgeidx.json"
    master_file_path = "extraction_result/vespa/masteridx.json"
    
    columns = [
        'document_name',
        'Invoice Number', 
        'Invoice From',
        'Invoice To', 
        'Total Amount',
        'Invoice Date', 
        'Due date'
    ]

    gt = pd.read_csv(gt_file_path)[columns]
    knowledge = json.load(open(knowledge_file_path))
    master = json.load(open(master_file_path))
    df = main("US", knowledge, master, gt, columns)
    df.to_csv("extraction_result/vespa/training_data.csv", index=None)
