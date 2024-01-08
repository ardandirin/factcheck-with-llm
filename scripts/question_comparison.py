import helper_functions as helpers
from evaluate import load
import json
from bert_score import score
bertscore = load("bertscore")
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine
import torch
from tqdm import tqdm

# Load pre-trained model tokenizer (vocabulary)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load pre-trained model (weights)
model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)

generated_questions_path = '../ClaimDecomp/subquestions_finetuned.jsonl'
annotated_questions_path = '../ClaimDecomp/test.jsonl'

# merged_questions = helpers.merge_questions(generated_questions_path, annotated_questions_path)
# print(merged_questions[0])

# Load the first and second file into a dictionary
generated = {item['example_id']: item for item in helpers.load_jsonl(generated_questions_path)}
annotated = {item['example_id']: item for item in helpers.load_jsonl(annotated_questions_path)}


def question_aggregator(json_line):

    question_set_1 = json_line["annotations"][0]["questions"]
    question_set_2 = json_line["annotations"][1]["questions"]
   # Combine the two sets of questions
    combined_questions = question_set_1 + question_set_2
    # Ensure each element is a string
    combined_questions = [str(question) for question in combined_questions]
    return combined_questions

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


reference_question_ex = question_aggregator(annotated[0])

# print(reference_question_ex)
# Assuming you have two lists of questions:
subquestions = data[0]['subquestions']  # Your list of subquestions

sqs = subquestions[0].split(', ')
print(len(sqs))

reference_questions = reference_question_ex # Your list of reference questions

# Choose a threshold for recall. You can adjust this as needed.
recall_threshold = 0.9
# Function to compute BERT scores, determine recall, and calculate average score
def compute_recall_and_average(subquestions, reference_questions, threshold):
    matching_results = []
    all_scores = []  # List to store all scores

    total_iterations = len(subquestions) * len(reference_questions)
    with tqdm(total=total_iterations, desc="Computing BERT Scores") as pbar:
        for ref_q in reference_questions:
            matched_subquestions = []
            for sub_q in subquestions:
                # Compute BERT scores between the reference question and each subquestion
                P, R, F1 = score([ref_q], [sub_q], lang="en", verbose=True)
                score_value = R.item()
                all_scores.append(score_value)  # Save score

                # Check if the subquestion's recall score meets the threshold
                if score_value >= threshold:
                    matched_subquestions.append((sub_q, score_value))
                pbar.update(1)

            if matched_subquestions:
                # Store the reference question and its matched subquestions
                matching_results.append({'reference_question': ref_q, 'matches': matched_subquestions})

    # Calculate the average score
    average_score = sum(all_scores) / len(all_scores) if all_scores else 0

    return matching_results, average_score


# Call the function and get results and average score
results, avg_score = compute_recall_and_average(sqs, reference_questions, recall_threshold)

# Process the results and print out
for result in results:
    print(f"Reference Question: {result['reference_question']}")
    for match in result['matches']:
        print(f"  Matched Subquestion: {match[0]} (Score: {match[1]})")
    print()  # Newline for readability

# Print the average score
print(f"Average BERT Score: {avg_score}")

# Count the total number of reference questions that were recalled
recalled_count = len(results)
print(f"Total number of reference questions recalled: {recalled_count} out of {len(reference_questions)}")


#/////////////////////////////////////////
# Function to compute BERT scores for each subquestion against each reference question
# def compute_scores(subquestions, reference_questions):
#     all_scores = []
#     for ref_q in reference_questions:
#         scores_for_ref = []
#         for sub_q in subquestions:
#             # Compute BERT scores between the reference question and each subquestion
#             P, R, F1 = score([ref_q], [sub_q], lang="en", verbose=True)
#             # Store the subquestion and its scores
#             scores_for_ref.append({'subquestion': sub_q, 'precision': P.item(), 'recall': R.item(), 'f1': F1.item()})
#         all_scores.append({'reference_question': ref_q, 'scores': scores_for_ref})
#     return all_scores

# # Call the function and get results
# results = compute_scores(sqs, reference_questions)

# # Process the results and print out each individual score
# for result in results:
#     print(f"Reference Question: {result['reference_question']}")
#     for score_info in result['scores']:
#         print(f"  Subquestion: {score_info['subquestion']}")
#         print(f"    Precision: {score_info['precision']}, Recall: {score_info['recall']}, F1: {score_info['f1']}")
#     print()  # Newline for readability





# def calculate_cosine_similarity(text1, text2):
#     # Encode text
#     input_ids_1 = tokenizer.encode(text1, return_tensors='pt')
#     input_ids_2 = tokenizer.encode(text2, return_tensors='pt')

#     # Compute BERT embeddings
#     with torch.no_grad():
#         outputs_1 = model(input_ids_1)
#         outputs_2 = model(input_ids_2)

#     # Use mean of last layer hidden states as sentence representation
#     embeddings_1 = outputs_1.hidden_states[-1].mean(dim=1).squeeze()
#     embeddings_2 = outputs_2.hidden_states[-1].mean(dim=1).squeeze()

#     # Compute cosine similarity
#     cosine_sim = 1 - cosine(embeddings_1, embeddings_2)
#     return cosine_sim

# # Compute similarity for each pair
# similarity_results = {}
# for ref_q in reference_questions:
#     similarity_results[ref_q] = []
#     for sub_q in sqs:
#         sim = calculate_cosine_similarity(ref_q, sub_q)
#         similarity_results[ref_q].append((sub_q, sim))

# # Display the results
# for ref_q, matches in similarity_results.items():
#     print(f"Reference Question: {ref_q}")
#     for sub_q, sim in matches:
#         print(f"  Subquestion: {sub_q}")
#         print(f"    Similarity: {sim}")
#     print()  # Newline for readability