import json
from helpers import general as General
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper
import argparse
import os
import time
from tqdm import tqdm
import re
# from sklearn.metrics import classification_report, confusion_matrix

label_prompt = open('prompts/verdict-prompt.txt', 'r', encoding='utf-8').read()
label_prompt_with_date = open('prompts/confidence-few_shot_no_labels.txt', 'r', encoding='utf-8').read()
base_url = os.environ.get('OPENAI_BASE_URL')
api_key = os.environ.get('OPENAI_API_KEY')


def pick_model(model_name):
    if model_name == "llama70b":
        model = "meta-llama/Llama-2-70b-chat-hf"
    elif model_name == "mixtral":
        model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    else:
        print("Unknown model")
    return model

# def dissect_answer(answer):

def extract_value(text, keyword):
    # Find the start of the keyword
    start = text.find(keyword)
    if start == -1:
        return None  # Keyword not found

    # Find the end of the line
    end = text.find('\n', start)
    if end == -1:
        end = len(text)

    # Extract the value after the keyword
    return text[start+len(keyword):end].strip()

def extract_value_regex(text, keyword):
    # Regular expression pattern to capture the content after the keyword
    pattern = re.compile(re.escape(keyword) + r'\s*(.*?)(?:\n|$)')
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None  # Return None if no match is found


def main(corpus_path, test_path, subquestions_path, output_path, model_name):
    model = pick_model(model_name)
    total_prompt_token = 0
    total_completion_token = 0
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as outfile:
        subq_data = JsonLoader.json_loader(subquestions_path)
        
        for line in tqdm(corpus):
            data = json.loads(line)
            id = data['example_id']
            original_claim = data['claim']
            date = DateHelper.extract_date_string(original_claim)
            subqs = JsonLoader.load_subquestions(subq_data, id)
            gold_label = General.get_label(test_path, id)
            all_summaries = " ".join(summary_dt['summary'] for summary_dt in data['summary_data'])
            all_subqs = []
            pred_labels_list = [] # List of predicted labels for each subquestion
            data_to_write = {'example_id': id, 'claim': original_claim, 'gold_label': gold_label, 'pred_label': str, 'subquestion_data': []}
            for subquestion in subqs:
                
                prompt = label_prompt_with_date
                # prompt += f"Answer the following question with one of these two options: yes/no. Your first sentence should be either yes or no followed by a dot (.). Afterwards give how confident you are in your answer with one of these options: High, Medium, Low. Finally give justification for your answer.\nDO ONLY use the following information when making the judgment: {all_summaries}\nQuestion: {subquestion}\nAnswer:"
                # prompt += f"Date: {date}\nQuestion: {subquestion}\nAnswer:"
                system_mes = "I will give you a question. Please answer the question with either yes, no, or not enough info. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY USE information prior to the given date.\nAlways seperate each part with a /n"
                prompt += f"Question:{subquestion}\nDate:{date}"
                time.sleep(1) # Sleep for 1 seconds to avoid exceeding the quota and almost concurrent requests.
                # answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model_name, system_message='You are a helpful assistant that is helping with fact checking a claim using only the given information', user_message=prompt)
                # print(f"prompt:'{prompt}")
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model, system_message=system_mes, user_message=prompt)

                # Split the text by newline
                lines = answer.split('\n')




                # predicted_label = extract_value_regex(answer, "Answer: ").strip().lower()

                # confidence = extract_value_regex(answer, "Confidence: ")
                # justification = extract_value_regex(answer, "Justification: ")
                # predicted_label = lines[0].split(": ")[1].strip().lower() if len(lines) > 0 else None
                # confidence = lines[1].split(": ")[1].strip().lower() if len(lines) > 1 else None
                # justification = lines[2].split(": ", 1)[1] if len(lines) > 2 else None

                splited_answer = answer.split('\n')
                predicted_label = splited_answer[0].strip().lower()
                confidence = splited_answer[1].strip().lower()
                justification = splited_answer[2]

                second_system_message = "I will give you a question and provide some information. Please answer the question with either yes, no, or not enough info. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Then give a brief justification for your answer. DO ONLY USE information prior to the given date.\nAlways seperate each part with a /n"
                second_prompt = label_prompt_with_date
                second_prompt += f"Question:{subquestion}\nDate:{date}\nInformation:{all_summaries}"
                if predicted_label == "not enough info":
                    print(f"Querying again with the web evidece since the label was {predicted_label}.")
                    time.sleep(1) # Sleep for 1 seconds to avoid exceeding the quota and almost concurrent requests.
                    second_answer, prompt_token_num_second, completion_token_num_second, total_token_num_second = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model, system_message=second_system_message, user_message=second_prompt)
                    splited_answer_new = second_answer.split('\n')
                    predicted_label_w_evidence = splited_answer[0].strip().lower()
                    confidence_w_evidence = splited_answer[1].strip().lower()
                    justification_w_evidence = splited_answer[2]

                    print(f"Label with evidence: {predicted_label_w_evidence}")
                    print(f"Confidence with evidence: {confidence_w_evidence}")
                    print(f'Justification with evidence {justification_w_evidence}')
                    pred_labels_list.append(predicted_label_w_evidence)
                else: # it is either yes or no
                    pred_labels_list.append(predicted_label)
        
                
                print(f"Label: {predicted_label}")
                print(f"Confidence: {confidence}")
                print(f'Justification {justification}')

                total_prompt_token += prompt_token_num
                total_completion_token += completion_token_num
                output_data = {
                    "subquestion": subquestion,
                    "answer": answer,
                    "predicted_label": predicted_label,
                    "confidence_level": confidence,
                    "confidence_level_w_evidence": confidence_w_evidence if predicted_label == "not enough info" else "N/A",
                    "justification": justification,
                    "justification_w_evidence": justification_w_evidence if predicted_label == "not enough info" else "N/A",
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
    parser.add_argument('--corpus_path', default='DataProcessed/summaries_5.jsonl', type=str)
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--subquestions_path', default='ClaimDecomp/subquestions_finetuned.jsonl', type=str)
    parser.add_argument('--output_path', default='DataProcessed/labels_confidence_5_mixtral.jsonl', type=str)
    parser.add_argument('--model_name', default='mixtral', type=str)
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.test_path, args.subquestions_path, args.output_path, args.model_name)
