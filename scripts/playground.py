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

# websites = '../ClaimDecomp/websites.jsonl'
# out_file = '../ClaimDecomp/websites_subset.jsonl'
# results = JsonLoader.json_loader(websites)

# Load data and annotated questions

# print(type(results))
# print(results[0][2]["url"])

# Open the source file and the destination file
# with open(websites, 'r') as source, open(out_file, 'w') as dest:
#     for line in source:
#         # Write each line to the destination file
#         dest.write(line)

# Extracting and listing the URLs
# urls = [item["url"] for item in results]

# Print the URLs
# print(urls)

# top_docs_path = '../ClaimDecomp/top_docs_old.jsonl'
# top_docs_path_new = '../ClaimDecomp/top_docs_10.jsonl'

answers = '../ClaimDecomp/answers.jsonl'
# answers10 = '../ClaimDecomp/answers_10.jsonl'

# with open(answers, 'r') as file, open(answers10, 'w') as out:
#     count = 0
#     breakcondition = False
#     for line in file:
#         if breakcondition:
#             break
#         out.write(line)
#         count += 1
#         if count == 10:
#             breakcondition = True


line_number = [180, 181, 182]  # the line number you want to access
input_file_path = '../ClaimDecomp/websites.jsonl'
output_file_path = '../DataProcessed/websites_3.jsonl'

with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    for current_line_number, line in enumerate(input_file, start=1):
        if current_line_number in line_number:
            output_file.write(line)
            print(f"Line {current_line_number} has been written to {output_file_path}")
    else:
        print(f"Line {line_number} not found.")
