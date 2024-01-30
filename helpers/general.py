import requests
import re
import re
import json



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
            

def get_answer_anyscale(api_base, token, model_name, system_message, user_message, repeat_penalty = 1, temperature = 0.7):
    s = requests.Session()
    url = f"{api_base}/chat/completions"
    body = {
    "model": model_name,
    "messages": [{"role": "system", "content": system_message}, 
                {"role": "user", "content": user_message}],
    "temperature": temperature,
    "repeat_penalty": repeat_penalty,
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


def classify_veracity_three_way(answer_list):
    categories = {
        "false": (0, 1/3),
        "half-true": (1/3, 2/3),
        "true": (2/3, 1)
    }

    if not answer_list:
        return "Unknown Category"  # Handle empty list

    veracity_score = sum(1 if answer == 'yes' else 0 for answer in answer_list) / len(answer_list)

    for category, (lower_bound, upper_bound) in categories.items():
        if lower_bound <= veracity_score < upper_bound:
            return category

    # Handle edge case where score is exactly 1
    if veracity_score == 1:
        return "true"

    return "Unknown Category"  # Should never happen but added as a safeguard



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

    if yes_count > no_count:
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
