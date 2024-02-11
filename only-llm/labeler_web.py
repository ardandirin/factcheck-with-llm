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

# label_prompt = open('prompts/verdict-prompt-nei-with-summaries.txt', 'r', encoding='utf-8').read()
# label_prompt_with_date = open('prompts/verdict-prompt-with-date.txt', 'r', encoding='utf-8').read()
base_url = os.environ.get('OPENAI_BASE_URL')
api_key = os.environ.get('OPENAI_API_KEY')

def extract_keyword(text, keyword):
    # Regex pattern to match the keyword, followed by a word, and capture that word
    pattern = re.compile(re.escape(keyword) + r"\s*(\w+)")
    match = pattern.search(text)
    if match:
        # The first captured group contains the word we want (e.g., 'Yes')
        return match.group(1).strip().lower()
    else:
        print("Returned None from extract_keyword!")
        return None
    
import re

def extract_justification(text, keyword="Justification:"):
    pattern = re.compile(re.escape(keyword) + r"\s*(.*?)(?:\n|$)", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    else:
        return None

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
    model = General.pick_model(model_name)
    total_prompt_token = 0
    total_completion_token = 0

    total_prompt_token_num_second = 0
    total_completion_token_num_second = 0
    not_confident = 0 # How many times the confidence was not high
    answer_changed = 0 # How many times the answer was changed with the LLM's internal knowledge
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as outfile:
        subq_data = JsonLoader.json_loader(subquestions_path)
        
        for line in tqdm(corpus):
            data = json.loads(line)
            id = data['example_id']
            original_claim = data['claim']
            date = DateHelper.extract_date_string(original_claim)
            # subqs = JsonLoader.load_subquestions_with_question_mark_gpt(subq_data, id) 
            # subqs = JsonLoader.load_subquestions(subq_data, id) # For GPT generated subquestions
            # subqs = JsonLoader.load_subquestions_with_newline(subq_data, id) # For mixtral generated subquestions
            subqs = JsonLoader.load_subquestions_with_question_mark(subq_data, id) # For mixtral generated subquestions
            
            gold_label = General.get_label(test_path, id)
            all_summaries = " ".join(summary_dt['summary'] for summary_dt in data['summary_data'])
            all_subqs = []
            pred_labels_list = [] # List of predicted labels for each subquestion
            data_to_write = {'example_id': id, 'claim': original_claim, 'gold_label': gold_label, 'pred_label': str, 'subquestion_data': []}
            for subquestion in subqs:
                
                prompt = label_prompt
                prompt += f"DO ONLY use the following information when making the judgment: {all_summaries}\nQuestion: {subquestion}\n"
                # prompt += f"\nQuestion: {subquestion}\nInformation:{all_summaries}\n"

                system_mes = "You should answer the question with either yes or no. Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. Always seperate each part of the answer with a new line"
                system_mes_with_no_info = "You should answer the question with either yes, no or nei(for not enough information). Then provide your confidence level to indicate your level of confidence in your predicted answer, choose one from High/Medium/Low. High indicates that you are very confident in your generated answer, Medium indicates average confidence, and Low indicates lack of confidence in your generated answer. Finally give a brief justification for your answer. DO ONLY use the information provided. Always seperate each part of the answer with a new line. In your answers always follow this format:Label:\nConfidence:\nJustification:"

                time.sleep(1) # Sleep for 1 seconds to avoid exceeding the quota and almost concurrent requests.
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model, system_message=system_mes_with_no_info, user_message=prompt)

                

                predicted_label = extract_keyword(answer, "Label:")
                confidence = extract_keyword(answer, "Confidence:")
                justification = extract_justification(answer, "Justification:")
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
                    "justification": justification,
                    "prompt_tokens": prompt_token_num,
                    "completion_tokens": completion_token_num,
                    "total_tokens": total_token_num,
                }
                all_subqs.append(output_data)

            print(f"len(pred_labels_list): {len(pred_labels_list)}")
            veracity = General.classify_veracity_new_6way(pred_labels_list)
            data_to_write['pred_label'] = veracity
            data_to_write['subquestion_data'] = all_subqs
            json.dump(data_to_write, outfile)
            outfile.write('\n')
    print(f"Total prompt tokens: {total_prompt_token}")
    print(f"Total completion tokens: {total_completion_token}")
    print(f"Total tokens: {total_prompt_token + total_completion_token}")

    print(f"Total prompt tokens second: {total_prompt_token_num_second}")
    print(f"Total completion tokens second: {total_completion_token_num_second}")
    print(f"Total tokens second: {total_prompt_token_num_second + total_completion_token_num_second}")

            
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='DataProcessed/summaries_final.jsonl', type=str)
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--subquestions_path', default='DataProcessed/subquestions_icl_mixtral.jsonl', type=str)
    parser.add_argument('--output_path', default='Results/labels_mixtral_web_updated_questions.jsonl', type=str)
    parser.add_argument('--model_name', default='mixtral', type=str)
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.test_path, args.subquestions_path, args.output_path, args.model_name)
