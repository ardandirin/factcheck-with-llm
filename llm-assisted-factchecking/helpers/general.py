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
            

def get_answer_anyscale(api_base, token, model_name, system_message, user_message):
    s = requests.Session()
    url = f"{api_base}/chat/completions"
    body = {
    "model": model_name,
    "messages": [{"role": "system", "content": system_message}, 
                {"role": "user", "content": user_message}],
    "temperature": 0.7
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
