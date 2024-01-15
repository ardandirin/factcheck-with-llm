import openai
import json
import os
from tqdm import tqdm
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chat_completion(prompt, model="gpt-3.5-turbo"):
    
   # Creating a message as required by the API
    messages=[
    {"role": "system", "content": "Assume you are a fact-checker, generate several yes or no questions to help me answer if this claim is true or false. You should ask questions regarding both implicit and explicit facets of the claim. DO ONLY OUTPUT THE QUESTIONS."},
    {"role": "user", "content": prompt}]
  
   # Calling the ChatCompletion API
    response = openai.ChatCompletion.create(
       model=model,
       messages=messages,
       temperature=0.7,
   )

   # Returning the extracted response
    return response.choices[0].message["content"]


model = "ft:gpt-3.5-turbo-0613:personal::8HsRtakR"
results = []

with open('ClaimDecomp/test.jsonl', 'r') as input_file:
    for line in tqdm(input_file, desc="Processing"):
        # Load the JSON data from the line
        data = json.loads(line)
        
        # Extract the relevant fields
        example_id = data['example_id']
        claim = data['claim']
        person = data['person']
        venue = data['venue']
        prompt = person + " " + venue + '\n' + claim

        # Placeholder for subquestions
        subquestions = []
        # subquestions.append("placeholder")
        # subquestions.append(get_chat_completion(prompt, model=model))

        # Append a new dictionary to the results list
        results.append({
            'example_id': example_id,
            'prompt': prompt,
            'subquestions': subquestions
        })


def create_output_file(results):
    with open('ClaimDecomp/subquestions.jsonl', 'w') as output_file:
        for json_obj in results:
            output_file.write(json.dumps(json_obj) + '\n')

create_output_file(results)