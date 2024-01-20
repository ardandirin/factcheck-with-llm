from helpers import general as General
import json
import argparse
import time
import os
from tqdm import tqdm

base_url = os.environ.get('OPENAI_BASE_URL')
api_key = os.environ.get('OPENAI_API_KEY')

print(f"Base url: {base_url}")
print(f"Api key: {api_key}")

def main(corpus_path, test_path, model_name, output_path):
    total_prompt_token = 0
    total_completion_token = 0
    one_shot_prompt = open('./prompts/one-shot-summary-prompt.txt', 'r', encoding='utf-8').read()
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as output_file:
        for line in tqdm(corpus):
            print('New claim')
            claim_entry = json.loads(line)
            id = claim_entry[0]['example_id']
            original_claim = General.get_claim(test_path, id)
            print(original_claim)
            # example_summary = 
            summaries = {'summary': []}
            data_to_write = {'example_id': id, 'claim': original_claim, 'summary_data': []}
            for dt in claim_entry[0]['top_docs']:
                # dt contains the 5 entries from the top_docs
                content = dt['content']
                document = dt['title']
                
                prompt = one_shot_prompt + '\n'
                prompt = f"Document: {document}\n"
                prompt += f"Content: {content}\n"
                prompt += f'Summarize the relevant information from the document in 1-2 sentences. Your response should provide a clear and concise summary of the relevant information contained in the document.'
                # print(f'The final prompt: {prompt}')
                time.sleep(5) # Sleep for 5 seconds to avoid exceeding the quota
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_answer_anyscale(api_base=base_url, token=api_key, model_name=model_name, system_message='You are a helpful assistant', user_message=prompt)
                summaries['summary'].append(answer)
                print(f"Prompt tokens: {prompt_token_num}")
                total_prompt_token += prompt_token_num
                total_completion_token += completion_token_num
                print(f"Completion tokens: {completion_token_num}")
                print(f"Total tokens: {total_token_num}")
                print(f"Answer - Summary: {answer}")
                
                
                
                summary_data = {
                    'document_title': document,
                    'url': dt['url'],
                    'snippet': dt['snippet'],
                    'summary': answer,
                    'content': content,
                    'prompt_token_num': prompt_token_num,
                    'completion_token_num': completion_token_num,
                    'total_token_num': total_token_num
                }
                data_to_write['summary_data'].append(summary_data)

            

            print(f"Total prompt tokens: {total_prompt_token}")
            print(f"Total completion tokens: {total_completion_token}")
            # Write all the subquestion with their summaries and metadata for the current claim to the output file
            output_file.write(json.dumps(data_to_write) + '\n')

              
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./DataProcessed/top_docs_final.jsonl', type=str)
    parser.add_argument('--test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--output_path', default='./DataProcessed/summaries_final.jsonl', type=str)
    parser.add_argument('--model_name', default='meta-llama/Llama-2-70b-chat-hf', type=str)
    
    args = parser.parse_args()
    return args
                    
if __name__ == '__main__':
    args = parse_args()
    main(args.corpus_path, args.test_path, model_name=args.model_name, output_path=args.output_path)
                