import argparse
import json
import os
import time
from tqdm import tqdm
from helpers import general as General
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper



def main(corpus_path, test_path, subquestions_path, output_path, model_name):
    model = General.pick_model(model_name)
    total_prompt_token = 0
    total_completion_token = 0

    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as outfile:
        subq_data = JsonLoader.json_loader(subquestions_path)
     
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='DataProcessed/summaries_5.jsonl', type=str)
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--subquestions_path', default='ClaimDecomp/subquestions_icl_mixtral.jsonl', type=str)
    parser.add_argument('--output_path', default='DataProcessed/labels_mixtral_llm_and_web.jsonl', type=str)
    parser.add_argument('--model_name', default='mixtral', type=str)
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.test_path, args.subquestions_path, args.output_path, args.model_name)
