import json
from helpers import general as General

api_base = 'https://api.endpoints.anyscale.com/v1'
token = 'esecret_6ccw4he32qk9jfkabbl8br41ca'
model_name = 'meta-llama/Llama-2-70b-chat-hf'
verdict_prompt = open('prompts/verdict-prompt.txt', 'r', encoding='utf-8').read()


def process_data(input_file_path, output_file_path):
    total_prompt_token = 0
    total_completion_token = 0
    with open(input_file_path, 'r', encoding='utf8') as input, open(output_file_path, 'w', encoding='utf8') as outfile:
        for line in input:
            data = json.loads(line)
            original_claim = data['claim']

            for subquestion_data in data['subquestions']:
                subquestion = subquestion_data['subquestion']
                all_summaries = " ".join([summary['summary'] for summary in subquestion_data['summaries']])
                prompt = verdict_prompt
                prompt += f"Answer the following question with one of these two options: yes/no. Your first sentence should be either yes or no. Afterwards give justification for your answer.\nDO ONLY use the following information when making the judgment: {all_summaries}\nQuestion: {subquestion}\nAnswer:"
                
                answer, prompt_token_num, completion_token_num, total_token_num = General.get_summary(api_base=api_base, token=token, model_name=model_name, system_message='You are a helpful assistant', user_message=prompt)
                
                total_prompt_token += prompt_token_num
                total_completion_token += completion_token_num
                output_data = {
                    "example_id": data['example_id'],
                    "claim": original_claim,
                    "subquestion": subquestion_data['subquestion'],
                    "answer": answer,
                    "prompt_tokens": prompt_token_num,
                    "completion_tokens": completion_token_num,
                    "total_tokens": total_token_num,
                    
                }
                json.dump(output_data, outfile)
                outfile.write('\n')
    print(f"Total prompt tokens: {total_prompt_token}")
    print(f"Total completion tokens: {total_completion_token}")

def main():
    input_file_path = 'ClaimDecomp/summaries_2.jsonl'  # Path to the input file
    output_file_path = 'ClaimDecomp/verdicts_2.jsonl'  # Path to the output file
    process_data(input_file_path, output_file_path)


if __name__ == "__main__":
    main()
