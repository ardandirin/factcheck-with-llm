import json
import os
import evaluate
import matplotlib.pyplot as plt


generated_questions_path = '../ClaimDecomp/subquestions_finetuned.jsonl'
annotated_questions_path = '../ClaimDecomp/test.jsonl'



# Function to aggregate questions from the JSON line
def question_aggregator(json_line):
    question_set_1 = json_line["annotations"][0]["questions"]
    question_set_2 = json_line["annotations"][1]["questions"]
    combined_questions = question_set_1 + question_set_2
    combined_questions = [str(question) for question in combined_questions]
    return combined_questions

# Load data and annotated questions
data = []
annotated = []
with open(generated_questions_path, 'r') as file:
    for line in file:
        json_obj = json.loads(line.strip())
        data.append(json_obj)

with open(annotated_questions_path, 'r') as file:
    for line in file:
        json_obj = json.loads(line.strip())
        annotated.append(json_obj)

# Preprocessing step, prepare examples for processing

examples = []
for i in range(len(data)):
    subquestions = data[i]['subquestions'][0].split(', ')
    reference_questions = question_aggregator(annotated[i])
    examples.append({'subquestions': subquestions, 'reference_questions': reference_questions})


bleu = evaluate.load("bleu")

print(examples[1]['subquestions'])


def compute_bleu_scores(examples):
    scores = []
    for ex in examples:
        preds = ex['subquestions']
        list_of_refs = [ex['reference_questions'] for _ in range(len(preds))]
        score = bleu.compute(predictions=preds, references=list_of_refs)
        # print(score)
        scores.append(score)
    return scores


def calc_average_bleu_score(scores):
    sum_scores = 0
    for i in scores:
        sum_scores += i['bleu']
    return sum_scores / len(scores)

# Assuming examples are defined
bleu_scores = compute_bleu_scores(examples)
output_file_path = 'bleu_scores.json'

# print(len(bleu_scores))
average_bleu = calc_average_bleu_score(bleu_scores)
# print(average_bleu)

output_data = {
        'bleu': bleu_scores,
        'average': average_bleu
    }

# with open(output_file_path, 'w') as outfile:
#         json.dump(output_data, outfile, indent=4)
# print(len(bleu_scores))


scores_list = [ score['bleu'] for score in bleu_scores ]
# print(scores_list)

# Plotting the distribution of mean_scores
plt.figure(figsize=(10, 6))
plt.hist(scores_list, bins=15, edgecolor='black')  # Adjust bins as needed
plt.title('Distribution of BLEU Scores')
plt.xlabel('BLEU Score')
plt.ylabel('Frequency')

# Save the plot
# plt.savefig('dne.png', dpi=300)  # Saves the plot as a PNG file

# plt.show()
