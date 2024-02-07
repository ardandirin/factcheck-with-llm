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

# answers = '../ClaimDecomp/answers.jsonl'
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


# line_number = [180, 181, 182]  # the line number you want to access
# input_file_path = '../ClaimDecomp/websites.jsonl'
# output_file_path = '../DataProcessed/websites_3.jsonl'

# with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
#     for current_line_number, line in enumerate(input_file, start=1):
#         if current_line_number in line_number:
#             output_file.write(line)
#             print(f"Line {current_line_number} has been written to {output_file_path}")
#     else:
#         print(f"Line {line_number} not found.")

# input_file_path = '../Results/labels_mixtral_gpt_web_withnei.jsonl'
# high = 0
# medium = 0
# low = 0
# yes = 0
# no = 0
# nei = 0
# noti = 0
# others = 0

# null_label = 0
# with open(input_file_path, 'r') as data:
#     for line in data:
#         json_obj = json.loads(line.strip())
#         for item in json_obj['subquestion_data']:
#             item['predicted_label'] is null
#             if label == 'null':
#                 null_label += 1

                
# print(null_label)
# print(f'high: {high}, medium: {medium}, low: {low}')


# with open(input_file_path, 'r') as data:
#     for line in data:
#         json_obj = json.loads(line.strip())
#         for item in json_obj['subquestion_data']:
#             conf = item['predicted_label']
#             if conf == 'yes':
#                 yes += 1
#             elif conf == 'no':
#                 no += 1
#             elif conf == 'nei':
#                 nei += 1
#             elif conf == 'not':
#                 noti += 1
#             else:
#                 others += 1

# # print(f'high: {high}, medium: {medium}, low: {low}')
# print(f'yes: {yes}, no: {no}')
# print(f'nei: {nei}, not: {noti}, others: {others}')




# with open(input_file_path, 'r') as data:
#     for line in data:
#         json_obj = json.loads(line.strip())
#         for item in json_obj['subquestion_data']:
#             conf = item['confidence_level']
#             if conf == 'high':
#                 high += 1
#             elif conf == 'medium':
#                 medium += 1
#             elif conf == 'low':
#                 low += 1
#             else:
#                 others += 1

# print(f'high: {high}, medium: {medium}, low: {low}')

# print(f'others: {others}')

import matplotlib.pyplot as plt

def create_histogram(data, bins=10, title="Histogram", xlabel="Value", ylabel="Frequency"):
    plt.hist(data, bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def remove_after_claim(text):
    # Find the index of "Claim:"
    index = text.find("Claim:")
    # If "Claim:" is found, return the substring up to its starting index
    if index != -1:
        return text[:index]
    # If "Claim:" is not found, return the original text
    return text

import re

mixtral_questions = './DataProcessed/subquestions_icl_mixtral_fixed.jsonl'
mixtral_final = './DataProcessed/subquestions_icl_mixtral_finalized.jsonl'


from helpers import json_loader as Jsonloader
num_questions = []
extremes = 0
with open(mixtral_final, 'r') as file:
    for line in file:
        json_obj = json.loads(line.strip())
        qs = []
        questions = Jsonloader.list_returner_q_mark(json_obj)
        # Jsonloader.load_subquestions_with_question_mark(json_obj, id)
        # questions = re.findall(r'.*?\?', json_obj['questions'].strip())
        
        if "Claim:" in json_obj['questions']:
            # cleaned_qs = remove_after_claim(json_obj['questions'])
            # json_obj['questions'] = cleaned_qs

            print(len(questions))
            print(questions)

        if len(questions) == 0:
            print(json_obj['example_id'])
        num_questions.append(len(questions))

        # json_obj_to_write = {'example_id': json_obj['example_id'], 'claim': json_obj['claim'], 'questions': json_obj['questions']}
        # json.dump(json_obj_to_write, out_file)
        # out_file.write('\n')
    

    create_histogram(num_questions, bins=5, title="Sample Histogram")
    
    print(num_questions)
    print(extremes)

