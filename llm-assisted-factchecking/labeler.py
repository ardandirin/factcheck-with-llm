import json
from helpers import general as General
from helpers import json_loader as JsonLoader
import argparse
import os
import time
from tqdm import tqdm

label_prompt = open('prompts/verdict-prompt.txt', 'r', encoding='utf-8').read()
base_url = os.environ.get('OPENAI_BASE_URL')
api_key = os.environ.get('OPENAI_API_KEY')

def main(corpus_path, test_path, subquestions_path, output_path, model_name):
    total_prompt_token = 0
    total_completion_token = 0
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as outfile:
        subq_data = JsonLoader.json_loader(subquestions_path)
        
        for line in tqdm(corpus):
            data = json.loads(line)
            id = data['example_id']
            original_claim = data['claim']
            subqs = JsonLoader.load_subquestions(subq_data, id)
            gold_label = General.get_label(test_path, id)
            all_summaries = " ".join(summary_dt['summary'] for summary_dt in data['summary_data'])
            all_subqs = []
            data_to_write = {'example_id': id, 'claim': original_claim, 'gold_label': gold_label, 'subquestion_data': []}
            for subquestion in subqs:
                
                prompt = label_prompt
                prompt += f"Answer the following question with one of these two options: yes/no. Your first sentence should be either yes or no followed by a dot (.). Afterwards give how confident you are in your answer with one of these options: High, Medium, Low. Finally give justification for your answer.\nDO ONLY use the following information when making the judgment: {all_summaries}\nQuestion: {subquestion}\nAnswer:"
                time.sleep(5) # Sleep for 5 seconds to avoid exceeding the quota
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model_name, system_message='You are a helpful assistant that is helping with fact checking a claim using only the given information', user_message=prompt)
                predicted_label, _, justification = answer.partition('.')
                print(f"Label: {predicted_label.strip().lower()}")
                total_prompt_token += prompt_token_num
                total_completion_token += completion_token_num
                output_data = {
                    "subquestion": subquestion,
                    "answer": answer,
                    "predicted_label": predicted_label.strip().lower(),
                    "justification": justification.strip(),
                    "prompt_tokens": prompt_token_num,
                    "completion_tokens": completion_token_num,
                    "total_tokens": total_token_num,
                }
                all_subqs.append(output_data)

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
    parser.add_argument('--subquestions_path', default='ClaimDecomp/subquestions_finetuned.jsonl', type=str)
    parser.add_argument('--output_path', default='DataProcessed/labels.jsonl', type=str)
    parser.add_argument('--model_name', default='meta-llama/Llama-2-70b-chat-hf', type=str)
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.test_path, args.subquestions_path, args.output_path, args.model_name)
