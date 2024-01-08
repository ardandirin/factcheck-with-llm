import json
# from helpers import json_loader as JsonLoader
# data = []
# generated_questions_path = '../ClaimDecomp/subquestions_finetuned.jsonl'


# import re


# examples = []

# with open(generated_questions_path, 'r') as file:
#     for line in file:
#         json_obj = json.loads(line.strip())
#         data.append(json_obj)

# for i in range(len(data)):
#     subquestions = data[i]['subquestions'][0].split(', ')
#     examples.append(subquestions)
    
# print(examples[7][3])

websites = '../ClaimDecomp/websites.jsonl'
out_file = '../ClaimDecomp/websites_subset.jsonl'
# results = JsonLoader.json_loader(websites)

# Load data and annotated questions

# print(type(results))
# print(results[0][2]["url"])

# Open the source file and the destination file
with open(websites, 'r') as source, open(out_file, 'w') as dest:
    for line in source:
        # Write each line to the destination file
        dest.write(line)

# Extracting and listing the URLs
# urls = [item["url"] for item in results]

# Print the URLs
# print(urls)