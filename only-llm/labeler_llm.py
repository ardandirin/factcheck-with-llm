import json
from helpers import general as General
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper
import argparse
import os
import time
from tqdm import tqdm
import re
from openai import OpenAI
from dotenv import load_dotenv
base_url = os.environ.get('OPENAI_BASE_URL')
api_key = os.environ.get('OPENAI_API_KEY')

load_dotenv()


def main(corpus_path, test_path, subquestions_path, output_path, model_name, knowledge_base, llm_type):
    label_prompt = open('prompts/verdict-prompt-with-date.txt', 'r', encoding='utf-8').read()
    model = General.pick_model(model_name)
    total_prompt_token = 0
    total_completion_token = 0

    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as outfile:
        subq_data = JsonLoader.json_loader(subquestions_path)
        
        for line in tqdm(corpus):
            data = json.loads(line)
            id = data['example_id']
            original_claim = data['claim']
            date = DateHelper.extract_date_string(original_claim)
            # subqs = JsonLoader.load_subquestions(subq_data, id) # for gpt generated questions
            subqs = JsonLoader.load_subquestions_with_question_mark_gpt(subq_data, id) # also for gpt but with question marks?
            # subqs = JsonLoader.load_subquestions_with_question_mark(subq_data, id) # for icl generated questions
            gold_label = General.get_label(test_path, id)
            all_subqs = []
            all_summaries = " ".join(summary_dt['summary'] for summary_dt in data['summary_data'])
            pred_labels_list = [] # List of predicted labels for each subquestion
            data_to_write = {'example_id': id, 'claim': original_claim, 'gold_label': gold_label, 'pred_label': str, 'subquestion_data': []}
            for subquestion in subqs:
                prompt = ""
                # if knowledge_base == "llm-web":
                #     prompt += f"I will give you a question. Please answer the question with either yes or no. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY USE information prior to the given date and you can refer to supplemantary information here: {all_summaries}.\nAlways seperate each part with a /n"
                # else:
                #     prompt = "I will give you a question. Please answer the question with either yes or no. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY USE information prior to the given date.\nAlways seperate each part with a /n"
                prompt += label_prompt
                prompt += f"Question: {subquestion}\nDate: {date}\n"
                # system_message_simple = "You are a helpful assistant answering questions."
                # system_message_no_info = "You MUST answer the question with either yes, no or nei(for not enough information). Follow the given format. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY USE information prior to the given date. Always seperate each part of the answer with a new line"
                system_message_lmm_web = f"You should label(answer) the question with either yes, no or nei(for not enough information). Follow the given format. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. You can also use the supplemantary information here: {all_summaries}.\nAlways seperate each part with a /n. The context for the question is: {original_claim} this should just give you the context, it is the original claim which the question is derived from (IT IS NOT NECESSARILY TRUE!)."
                # system_mes = "I will give you a question. Please answer the question with either yes or no. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY USE information prior to the given date.\nAlways seperate each part with a /n"
                time.sleep(1) # Sleep for 1 seconds to avoid exceeding the quota and also concurrent requests.
                if llm_type == 'anyscale':
                    answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model, system_message=system_message_lmm_web, user_message=prompt)
                elif llm_type == 'gpt':
                    print("GPT type selected")
                    openai_api_key = os.getenv('OPENAI_API_KEY')
                    client = OpenAI(api_key=openai_api_key)
                    answer, prompt_token_num, completion_token_num, total_token_num = General.get_chat_completion_gpt(prompt=prompt, system_message=system_message_lmm_web, model=model_name, client=client)
                else:
                    print('Please select a valid LLM')
                predicted_label = General.extract_keyword(answer, "Label:")
                confidence = General.extract_keyword(answer, "Confidence:")
                justification = General.extract_justification(answer, "Justification:")
                pred_labels_list.append(predicted_label)
                
                print(f"Label: {predicted_label}")
                print(f"Confidence: {confidence}")
                print(f'Justification: {justification}')

                total_prompt_token += prompt_token_num
                total_completion_token += completion_token_num
                output_data = {
                    "subquestion": subquestion,
                    "answer": answer,
                    "predicted_label": predicted_label,
                    "confidence_level": confidence,
                    "justification": justification,
                    "prompt_tokens": prompt_token_num,
                    "completion_tokens": completion_token_num,
                    "total_tokens": total_token_num,
                }
                all_subqs.append(output_data)

            veracity = General.classify_veracity(pred_labels_list)
            data_to_write['pred_label'] = veracity
            data_to_write['subquestion_data'] = all_subqs
            json.dump(data_to_write, outfile)
            outfile.write('\n')
    print(f"Total prompt tokens: {total_prompt_token}")
    print(f"Total completion tokens: {total_completion_token}")
    print(f"Total tokens: {total_prompt_token + total_completion_token}")

            
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='DataProcessed/summaries_final.jsonl', type=str)
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--subquestions_path', default='DataProcessed/subquestions_icl_mixtral.jsonl', type=str)
    parser.add_argument('--output_path', default='Results/labels_mixtral_icl_llmweb_withnei.jsonl', type=str)
    parser.add_argument('--model_name', default='mixtral', type=str)
    parser.add_argument('--knowledge_base', default='llm', type=str) # can give llm or llm-web then summaries will be used as well.
    parser.add_argument('--llm_type', default='ansycale') # gpt or anyscale
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.test_path, args.subquestions_path, args.output_path, args.model_name, args.knowledge_base, args.llm_type)
