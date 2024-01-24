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

prompt = '''Claim: Alexandria Ocasio-Cortez stated on July 13, 2018 in an interview on PBS' "Firing Line": Unemployment is low because everyone has two jobs. Unemployment is low because people are working 60, 70, 80 hours a week and can barely feed their family.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:
Can low unemployment rates be attributed to everyone having 2 jobs?
Is unemployment even currently low because of factors stated by Ocasio Cortez?
Can low unemployment be attributed to long work hours?

Claim: Barry DuVal stated on September 25, 2015 in an interview: We're the only major oil-producing nation in the world with a self-imposed ban on exporting our crude oil to other nations.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:
Is the U.S. the only major oil-producing nation to ban exports of crude oil?
Is the self-imposed ban on crude oil export of U.S a complete ban?

Claim: William Barr stated on September 2, 2020 in a CNN interview: We indicted someone in Texas, 1,700 ballots collected from people who could vote, he made them out and voted for the person he wanted to.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:
Were 1700 mail-in ballots invesgated for fraud in Texas during the 2020 election?
Did the Justice Department indict someone in Texas for voter fraud?
Did widespread mail-in order fraud happen in Texas during the 2020 election?
Did voter disenfranchisement happen in Texas during the 2020 election?

Claim: {}
Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:'''


total_prompt_token = 0
total_completion_token = 0



def main(test_path, output_path, model_name):
    model = General.pick_model(model_name)
    base_url = os.environ.get('OPENAI_BASE_URL')
    api_key = os.environ.get('OPENAI_API_KEY')

    with open(test_path, 'r', encoding='utf8') as test_file, open(output_path, 'w', encoding='utf8') as outfile:
        for line in test_file:
            data = json.loads(line)
            id = data['example_id']
            claim = General.get_claim(test_path, id)
            prompt = prompt.format(claim)
            answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(base_url, api_key, model, system_message='You are a helpful assistant.', user_message=prompt)
            total_prompt_token += prompt_token_num
            total_completion_token += completion_token_num
            print(f"Total prompt tokens: {total_prompt_token}")
            print(f"Total completion tokens: {total_completion_token}")
            print(f"Total tokens: {total_token_num}")
            print(f"Answer: {answer}")
            outfile.write(json.dumps({'example_id': id, 'claim': claim, 'questions': answer}) + '\n')
            outfile.flush()
            time.sleep(2)
            # break
    

            
def parse_args():
    parser = argparse.ArgumentParser()
  
    parser.add_argument('--test_path', default='ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--output_path', default='DataProcessed/subquestions_icl_llama.jsonl', type=str)
    parser.add_argument('--model_name', default='llama70b', type=str)
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.test_path, args.output_path, args.model_name)

