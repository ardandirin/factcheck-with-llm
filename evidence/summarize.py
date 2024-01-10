from helpers import general as General
import json
import argparse
import time

def main(corpus_path, test_path, api_base, token, model_name, output_path):
    total_prompt_token = 0
    total_completion_token = 0
    few_shot_prompt = open('./few-shot-prompt.txt', 'r', encoding='utf-8').read()
    one_shot_prompt = open('./one-shot-summary-prompt.txt', 'r', encoding='utf-8').read()
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(output_path, 'w', encoding='utf8') as output_file:
        for line in corpus:
            print('New claim')
            claim_entry = json.loads(line)
            id = claim_entry['example_id']
            data = claim_entry['data']
            original_claim = General.get_claim(test_path, id)
            print(original_claim)
            example_summary = {'example_id': id, 'claim': original_claim, 'subquestions': []}
            
            for dt in data:
                # qs contains the question and the top docs
                subquestion_summary = {'subquestion': dt['question'], 'summaries': []}
                subquestion = (dt['question'])
                summaries = {'summary': []}
                for docs in dt['top_docs']:
                    
                    document = docs['title']
                    segment = docs['segment']
                    
                    prompt = one_shot_prompt + '\n'
                    prompt = f"Document: {document}\n"
                    prompt += f"Content: {segment} \n\n"
                    prompt += f'\n Summarize the relevant information from the document in 1-2 sentences. Your response should provide a clear and concise summary of the relevant information contained in the document. Do not include a judgment about the claim and do not repeat any information from the claim that is not supported by the document.'
                    # print(f'The final prompt: {prompt}')
                    time.sleep(10) # Sleep for 10 seconds to avoid exceeding the quota
                    answer, prompt_token_num, completion_token_num, total_token_num = General.get_summary(api_base=api_base, token=token, model_name=model_name, system_message='You are a helpful assistant', user_message=prompt)
                    summaries['summary'].append(answer)
                    print(f"Prompt tokens: {prompt_token_num}")
                    total_prompt_token += prompt_token_num
                    total_completion_token += completion_token_num
                    print(f"Completion tokens: {completion_token_num}")
                    print(f"Total tokens: {total_token_num}")
                    print(f"Answer - Summary: {answer}")
                    
                    
                    
                    summary_data = {
                        'document_title': docs['title'],
                        'url': docs['url'],
                        'snippet': docs['segment'],
                        'summary': answer,
                        'prompt_token_num': prompt_token_num,
                        'completion_token_num': completion_token_num,
                        'total_token_num': total_token_num
                    }
                    subquestion_summary['summaries'].append(summary_data)
                
                example_summary['subquestions'].append(subquestion_summary)
                

            print(f"Total prompt tokens: {total_prompt_token}")
            print(f"Total completion tokens: {total_completion_token}")
            # Write all the subquestion with their summaries and metadata for the current claim to the output file
            output_file.write(json.dumps(example_summary) + '\n')

                    
                
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_base', default='https://api.endpoints.anyscale.com/v1', type=str)
    parser.add_argument('--token', default='esecret_6ccw4he32qk9jfkabbl8br41ca', type=str)
    parser.add_argument('--corpus_path', default='./ClaimDecomp/top_docs_10.jsonl', type=str)
    parser.add_argument('--test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--output_path', default='./ClaimDecomp/summaries_10.jsonl', type=str)
    
    args = parser.parse_args()
    return args
                    
if __name__ == '__main__':
    args = parse_args()
    model_name = 'meta-llama/Llama-2-70b-chat-hf'
    main(args.corpus_path, args.test_path, args.api_base, args.token, model_name=model_name, output_path=args.output_path)
                