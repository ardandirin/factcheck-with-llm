import json

data = []
generated_questions_path = '../ClaimDecomp/subquestions_finetuned.jsonl'


import re


examples = []

with open(generated_questions_path, 'r') as file:
    for line in file:
        json_obj = json.loads(line.strip())
        data.append(json_obj)

for i in range(len(data)):
    subquestions = data[i]['subquestions'][0].split(', ')
    examples.append(subquestions)
    
print(examples[7][3])