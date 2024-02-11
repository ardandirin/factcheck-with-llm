import requests
import re
import re
import json
from openai import OpenAI
import os


def postprocess_text(text):
    '''
    :param text: the text of the website
    :return: the processed text
    Given a text, remove newlines, tabs, and extra spaces
    '''
    cleaned = text.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    # Optional, remove spaces before and after punctuation
    cleaned = re.sub(r'\s+([?.!,:;])', r'\1', cleaned)
    return cleaned


def count_words(text):
    words = text.split()
    return len(words)
    
def get_context(data):
    return data['person'] + " " + data['venue'] + " " + data['claim']
            

def get_article(path, example_id):
    '''
    :param path: the path to the test file containing the context
    :param example_id: the id of the context to find
    :return: the full article of the example_id
    '''
    with open(path, 'r') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            if json_obj['example_id'] == example_id:
                return json_obj['full_article']
    print("No article found")
    return None
            
def get_claim(path, example_id):
    '''
    :param path: the path to the test file containing the context
    :param example_id: the id of the context to find
    :return: the original claim of the example_id
    '''
    with open(path, 'r') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            if json_obj['example_id'] == example_id:
                full_claim = json_obj['person'] + " " + json_obj['venue'] + " " + json_obj['claim']
                return full_claim
    print("No claim found")
    return None


def get_label(path, example_id):
    '''
    :param path: the path to the test file containing the context
    :param example_id: the id of the context to find
    :return: the final verdict of the claim (6-way classification)
    '''
    with open(path, 'r') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            if json_obj['example_id'] == example_id:
                return json_obj['label']
    print("No label found")
    return None
            

def get_answer_anyscale(api_base, token, model_name, system_message, user_message, repeat_penalty = 1, temperature = 1):
    s = requests.Session()
    url = f"{api_base}/chat/completions"
    body = {
    "model": model_name,
    "messages": [{"role": "system", "content": system_message}, 
                {"role": "user", "content": user_message}],
    "temperature": temperature,
    # "repeat_penalty": repeat_penalty,
    }


    with s.post(url, headers={"Authorization": f"Bearer {token}"}, json=body) as resp:
        response = resp.json()
       
        answer = response['choices'][0]['message']['content']
        prompt_token_num = response['usage']['prompt_tokens']
        completion_token_num = response['usage']['completion_tokens']
        total_token_num = response['usage']['total_tokens']
        
        print(f"Prompt tokens: {prompt_token_num}")
        print(f"Completion tokens: {completion_token_num}")
        print(f"Total tokens: {total_token_num}")
        
        return answer, prompt_token_num, completion_token_num, total_token_num
    

def get_chat_completion_gpt(prompt, system_message, model, api_key):
    print(f"Model is {model}")
    OpenAI.api_key = os.environ['OPENAI_API_KEY']
    client = OpenAI()
   # Creating a message as required by the API
    messages=[
    {"role": "system", "content": system_message},
    {"role": "user", "content": prompt}]
  
   # Calling the ChatCompletion API
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
   )

   # Returning the extracted response
    answer = completion.choices[0].message["content"]
    prompt_token_num = completion['usage']['prompt_tokens']
    completion_token_num = completion['usage']['completion_tokens']
    total_token_num = completion['usage']['total_tokens']
    
    print(f"Prompt tokens: {prompt_token_num}")
    print(f"Completion tokens: {completion_token_num}")
    print(f"Total tokens: {total_token_num}")
    
    return answer, prompt_token_num, completion_token_num, total_token_num
    

def classify_veracity(answer_list):
    if not answer_list:
        return "No Data"
    categories = {
        "pants-fire": (0, 1/6),
        "false": (1/6, 2/6),
        "barely-true": (2/6, 3/6),
        "half-true": (3/6, 4/6),
        "mostly-true": (4/6, 5/6),
        "true": (5/6, 1)
    }

    veracity_score = sum(1 if answer == 'yes' else 0 for answer in answer_list) / len(answer_list)

    for category, (lower_bound, upper_bound) in categories.items():
        if lower_bound <= veracity_score < upper_bound:
            return category

    # Handle edge case where score is exactly 1
    if veracity_score == 1:
        return "true"

    return "Unknown Category" # Should never happen


def classify_veracity_new_6way(answer_list):
    if not answer_list:
        print("No data found")
        return "Unknown"  # Handle empty list

    # Define categories and their bounds
    categories = [
        "pants-fire", "false", "barely-true",
        "half-true", "mostly-true", "true"
    ]

    # Filter the list to only include 'yes' and 'no' answers
    filtered_answers = [answer for answer in answer_list if answer in ['yes', 'no']]

    # Return "No Data" if there are no 'yes' or 'no' answers
    if not filtered_answers:
        return "Unknown"

    # Calculate veracity score based only on 'yes' and 'no' answers
    veracity_score = sum(1 if answer == 'yes' else 0 for answer in filtered_answers) / len(filtered_answers)

    # Determine the category based on the veracity score
    index = int(veracity_score * len(categories))  # Convert score to index
    if index == len(categories):  # Handle edge case where score is exactly 1
        index -= 1  # Adjust index to last category

    return categories[index]


def classify_veracity_new_6way_with_conf(answer_list, confidence_list):
    if not answer_list or len(answer_list) != len(confidence_list):
        print("Invalid or mismatched input data")
        return "Unknown"

    categories = [
        "pants-fire", "false", "barely-true",
        "half-true", "mostly-true", "true"
    ]

    # Mapping confidence levels to weights
    confidence_weights = {"high": 1, "medium": 0.5, "low": 0}

    weighted_yes_count = 0
    total_weight = 0

    for answer, confidence in zip(answer_list, confidence_list):
        weight = confidence_weights.get(confidence, 0)  # Default to 0 if confidence level is not recognized
        if answer in ['yes', 'no']:
            total_weight += weight
            if answer == 'yes':
                weighted_yes_count += weight

    if total_weight == 0:  # Avoid division by zero and handle cases with no applicable responses
        print("No applicable 'yes' or 'no' answers with sufficient confidence found")
        return "Unknown"

    veracity_score = weighted_yes_count / total_weight

    # Determine the category based on the veracity score
    index = int(veracity_score * len(categories))
    if index == len(categories):  # Handle edge case where score is exactly 1
        index -= 1  # Adjust index to the last category

    return categories[index]



def classify_veracity_three_way(answer_list):
    categories = {
        "false": (0, 1/3),
        "half-true": (1/3, 2/3),
        "true": (2/3, 1)
    }

    if not answer_list:
        print("No data found")
        return "Unknown"  # Handle empty list
    
    # Filter the list to only include 'yes' and 'no' answers
    filtered_answers = [answer for answer in answer_list if answer in ['yes', 'no']]

    # Check if the filtered list is not empty to avoid division by zero
    if not filtered_answers:
        print("No 'yes' or 'no' answers found")
        return "Unknown"  # Handle case with no 'yes' or 'no' answers


    veracity_score = sum(1 if answer == 'yes' else 0 for answer in filtered_answers) / len(filtered_answers)

    for category, (lower_bound, upper_bound) in categories.items():
        if lower_bound <= veracity_score < upper_bound:
            return category

    # Handle edge case where score is exactly 1
    if veracity_score == 1:
        return "true"

    return "Unknown"  # Should never happen but added as a safeguard


def classify_veracity_three_way_with_conf(answer_list, confidence_list):
    if not answer_list or len(answer_list) != len(confidence_list):
        print("Invalid or mismatched input data")
        return "Unknown"

    categories = {
        "false": (0, 1/3),
        "half-true": (1/3, 2/3),
        "true": (2/3, 1)
    }

    # Mapping confidence levels to weights
    confidence_weights = {"high": 1, "medium": 0.5, "low": 0}

    # Initialize variables for calculating the weighted score
    weighted_yes_no_counts = 0
    total_weight = 0

    for answer, confidence in zip(answer_list, confidence_list):
        if confidence in confidence_weights and answer in ['yes', 'no']:
            weight = confidence_weights[confidence]
            answer_value = 1 if answer == 'yes' else 0
            weighted_yes_no_counts += weight * answer_value
            total_weight += weight

    if total_weight == 0:  # Avoid division by zero if all answers are of low confidence or 'nei'
        print("No 'yes' or 'no' answers with sufficient confidence found")
        return "Unknown"

    veracity_score = weighted_yes_no_counts / total_weight

    for category, (lower_bound, upper_bound) in categories.items():
        if lower_bound <= veracity_score < upper_bound:
            return category

    # Handle edge case where score is exactly 1
    if veracity_score == 1:
        return "true"

    return "Unknown"




def map_six_to_three_categories(six_category_label):
    mapping = {
        "pants-fire": "false",
        "false": "false",
        "barely-true": "half-true",
        "half-true": "half-true",
        "mostly-true": "true",
        "true": "true"
    }

    return mapping.get(six_category_label, "Unknown Category")


def classify_binary_veracity(answer_list):
    yes_count = answer_list.count('yes')
    no_count = answer_list.count('no')


    if yes_count == 0 and no_count == 0:
        print(answer_list)
        print("No answer data found")
        return "Unknown"

    if yes_count >= no_count:
        return 'yes'
    else: 
        return 'no'
    
def classify_binary_veracity_with_conf(answer_list, confidence_list):
# Verify that the lists are of equal length
    if not answer_list or len(answer_list) != len(confidence_list):
        print("Invalid or mismatched input data")
        return "Unknown"

    # Mapping confidence levels to weights
    confidence_weights = {"high": 1, "medium": 0.5, "low": 0}

    # Initialize weighted counts
    weighted_yes_count = 0
    weighted_no_count = 0

    # Apply weights based on confidence levels
    for answer, confidence in zip(answer_list, confidence_list):
        weight = confidence_weights.get(confidence, 0)  # Default to 0 if confidence level is unknown
        if answer == 'yes':
            weighted_yes_count += weight
        elif answer == 'no':
            weighted_no_count += weight

    # Decide based on weighted counts
    if weighted_yes_count >= weighted_no_count:
        return 'yes'
    else:
        return 'no'





# def classify_threeway_veracity(answer_list):
#     yes_count = answer_list.count('yes')
#     no_count = answer_list.count('no')

#     if yes_count > no_count:
#         return 'yes'
#     else: 
#         return 'no'
    
def pick_model(model_name):
    if model_name == "llama70b":
        model = "meta-llama/Llama-2-70b-chat-hf"
    elif model_name == "mixtral":
        model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    else:
        print("Unknown model, loading given full model name")
        model = model_name
    return model


def extract_justification(text, keyword="Justification:"):
    pattern = re.compile(re.escape(keyword) + r"\s*(.*?)(?:\n|$)", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    else:
        return None


def extract_keyword(text, keyword):
    # Regex pattern to match the keyword, followed by a word, and capture that word
    pattern = re.compile(re.escape(keyword) + r"\s*(\w+)")
    match = pattern.search(text)
    if match:
        # The first captured group contains the word we want (e.g., 'Yes')
        return match.group(1).strip().lower()
    else:
        print("Returned None from extract_keyword!")
        return None
