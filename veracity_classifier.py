import json
from helpers import general as General

api_base = 'https://api.endpoints.anyscale.com/v1'
token = 'esecret_6ccw4he32qk9jfkabbl8br41ca'
model_name = 'meta-llama/Llama-2-70b-chat-hf'

def process_data(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf8') as file, open(output_file_path, 'w', encoding='utf8') as outfile:
        for line in file:
            data = json.loads(line)
            # original_claim = data['original_claim']

            for subquestion_data in data['subquestions']:
                subquestion = subquestion_data['subquestion']
                all_summaries = " ".join([summary['summary'] for summary in subquestion_data['summaries']])
                prompt = f"Answer the following question out of these three options: yes/no/not-enough-information. \n Subquestion: {subquestion}\n DO ONLY use the following information when making the judgment: {all_summaries}\n, Give justification for your answer."
                
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_summary(api_base=api_base, token=token, model_name=model_name, system_message='You are a helpful assistant', user_message=prompt)
                
                output_data = {
                    "example_id": data['example_id'],
                    "claim": data['claim'],
                    "subquestion": subquestion_data['subquestion'],
                    "answer": answer,
                    "prompt_tokens": prompt_token_num,
                    "completion_tokens": completion_token_num,
                    "total_tokens": total_token_num,
                    
                }
                json.dump(output_data, outfile)
                outfile.write('\n')

def main():
    input_file_path = 'ClaimDecomp/summaries_new.jsonl'  # Path to the input file
    output_file_path = 'ClaimDecomp/verdicts.jsonl'  # Path to the output file
    process_data(input_file_path, output_file_path)


if __name__ == "__main__":
    main()
