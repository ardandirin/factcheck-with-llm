# import helper_functions as helpers
from evaluate import load
import json
from bert_score import score
bertscore = load("bertscore")
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine
import torch
from tqdm import tqdm
import statistics
from transformers import logging
import matplotlib.pyplot as plt
from helpers import json_loader as Jsonloader

# Set the logging level to error to suppress warnings (but still show errors)
logging.set_verbosity_error()



# Load pre-trained model tokenizer (vocabulary)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load pre-trained model (weights)
model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)

generated_questions_path = './ClaimDecomp/subquestions_finetuned.jsonl'
generated_questions_path = './DataProcessed/subquestions_icl_mixtral.jsonl'
annotated_questions_path = './ClaimDecomp/test.jsonl'
recall_threshold = 0.9


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
    # subquestions = data[i]['subquestions'][0].split(', ')
    subquestions = Jsonloader.list_returner_q_mark(data[i])
    reference_questions = question_aggregator(annotated[i])
    examples.append({'subquestions': subquestions, 'reference_questions': reference_questions})


def compute_mean_max(examples, out_file):
    mean_scores = []
    matched_max = {}
    for example in tqdm(examples, desc="Processing Examples"):
        subquestions, reference_questions = example['subquestions'], example['reference_questions']
        max_scores = []
        for ref_q in tqdm(reference_questions, desc="Processing Reference Questions", leave=False):
            max_score = 0
            max_subq = ''
            for sub_q in tqdm(subquestions, desc="Processing Subquestions", leave=False):
            # Compute BERT scores
                _, R, _ = score([ref_q], [sub_q], lang="en", verbose=False)
                embedding = R.item()
                if embedding > max_score:
                    max_score = embedding
                    max_subq = sub_q
            max_scores.append(max_score)
            matched_max[ref_q] = {"max_subq": max_subq, "score": max_score}
        average = statistics.fmean(max_scores)
        mean_scores.append(average)

    output_data = {
        'mean_scores': mean_scores,
        'matched_max': matched_max
    }
        
    with open(output_file_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)
    return mean_scores, matched_max


output_file_path = 'mean_max.json'
mean_scores, matched_max = compute_mean_max(examples, output_file_path)
print(mean_scores)

# Plotting the distribution of mean_scores
plt.figure(figsize=(10, 6))
plt.hist(mean_scores, bins=20, edgecolor='black')  # Adjust bins as needed
plt.title('Distribution of Mean Scores')
plt.xlabel('Scores')
plt.ylabel('Frequency')

# Save the plot
plt.savefig('mean_scores_distribution.png', dpi=300)  # Saves the plot as a PNG file

plt.show()



# def compute_recall_and_save_matches(examples, thresholds, output_file_path):
#     total_matches = {threshold: 0 for threshold in thresholds}
#     matched_pairs = {threshold: [] for threshold in thresholds}
#     total_ref_questions = 0

#     for example in examples:
#         subquestions, reference_questions = example['subquestions'], example['reference_questions']
#         total_ref_questions += len(reference_questions)

#         for ref_q in reference_questions:
#             matches_found = {threshold: False for threshold in thresholds}

#             for sub_q in subquestions:
#                 # Compute BERT scores
#                 _, R, _ = score([ref_q], [sub_q], lang="en", verbose=True)
#                 score_value = R.item()

#                 for threshold in thresholds:
#                     if score_value >= threshold and not matches_found[threshold]:
#                         # Count this match for recall calculation
#                         total_matches[threshold] += 1
#                         matches_found[threshold] = True

#                         # Save the matched pair
#                         match = {
#                             'reference_question': ref_q,
#                             'matched_subquestion': sub_q,
#                             'score': score_value
#                         }
#                         matched_pairs[threshold].append(match)

#     # Write the matched pairs to a file
#     with open(output_file_path, 'w') as outfile:
#         json.dump(matched_pairs, outfile, indent=4)

#     # Calculate average recall for each threshold
#     average_recalls = {threshold: total_matches[threshold] / total_ref_questions for threshold in thresholds}

#     return average_recalls, matched_pairs

# # Define your thresholds and output file path
# thresholds = [0.8, 0.9, 0.925, 0.95]
# output_file_path = 'matched_pairs.json'

# # Assuming examples are defined
# average_recalls, matched_pairs = compute_recall_and_save_matches(examples, thresholds, output_file_path)

# for threshold, avg_recall in average_recalls.items():
#     print(f"Average Recall at threshold {threshold}: {avg_recall}")
# print(f"Matched pairs saved to {output_file_path}")