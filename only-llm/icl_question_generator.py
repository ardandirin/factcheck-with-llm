'''
IN-CONTEXT-LEARNING QUESTION GENERATOR
Given the ClaimDecomp Test set's questions and the prompt to provide few-shot-learning
Returns the generated subquestions about the claim. 
'''

from helpers import general as General
import argparse
import os
import json
import time
from tqdm import tqdm

# prompt = "Assume you are a fact-checker, generate unique yes or no questions to help me answer if this claim is true or false. You should ask questions regarding both implicit and explicit facets of the claim. Each question should be unique. Make the questions explicit. DO ONLY OUTPUT THE QUESTIONS."


def format_prompt_with_txt(text_data, claim):
    prompt = ""
    with open(text_data, 'r', encoding='utf8') as f:
        text = f.read()
        prompt += text

    prompt += "Claim: {}\nQuestions:\n".format(claim)
    # prompt += "Suppose you are a fact-checker, generate a few yes or no questions to help me answer if this claim is true or false."


    return prompt




def main(test_path, output_path, model_name):
    model = General.pick_model(model_name)
    base_url = os.environ.get('OPENAI_BASE_URL')
    api_key = os.environ.get('OPENAI_API_KEY')
    total_prompt_token = 0
    total_completion_token = 0

    

    system_message = "Assume you are a fact-checker, generate a few, unique yes or no questions to help me answer if this claim is true or false. You should ask questions regarding both implicit and explicit facets of the claim. ONLY OUTPUT THE QUESTIONS. Seperate each question with a new line."

    # system_message = "You are a helpful assistant."
    with open(test_path, 'r', encoding='utf8') as test_file, open(output_path, 'w', encoding='utf8') as outfile:
        for line in tqdm(test_file):
            data = json.loads(line)
            id = data['example_id']
            claim = General.get_claim(test_path, id)
            # prompt = format_prompt(claim)
            prompt = format_prompt_with_txt('prompts/icl_qg.txt', claim)
            answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(base_url, api_key, model, system_message=system_message, user_message=prompt, repeat_penalty=1, temperature=0.7)
            total_prompt_token += prompt_token_num
            total_completion_token += completion_token_num
            print(f"Total prompt tokens: {total_prompt_token}")
            print(f"Total completion tokens: {total_completion_token}")
            print(f"Total tokens: {total_token_num}")
            print(f"Answer: {answer}")
            outfile.write(json.dumps({'example_id': id, 'claim': claim, 'questions': answer}) + '\n')
            outfile.flush()
            time.sleep(2)
    print(f"Total prompt tokens: {total_prompt_token}")
    print(f"Total completion tokens: {total_completion_token}")
    print(f"Total tokens: {total_prompt_token + total_completion_token}")
    

            
def parse_args():
    parser = argparse.ArgumentParser()
  
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--output_path', default='DataProcessed/subquestions_icl_mixtral.jsonl', type=str)
    parser.add_argument('--model_name', default='mixtral', type=str)
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.test_path, args.output_path, args.model_name)

