import requests
import certifi
from bs4 import BeautifulSoup
import logging
import re
# from transformers import pipeline
from nltk import word_tokenize
import difflib
import re
import json
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


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



def clean_text(text):
    # Replace left and right curly quotes with straight quotes
    text = re.sub(r'“', '"', text)
    text = re.sub(r'”', '"', text)
    text = re.sub(r'‘', "'", text)
    text = re.sub(r'’', "'", text)
    text = re.sub(r'`', "'", text)
    text = re.sub(r"''", '"', text)
    # Add more replacements as needed
    return text


def find_close_match(key_to_find, unit2docid):
    '''
    Due to encoding in the bm25, the key to find is not exactly the same as the key in the dictionary
    :param key_to_find: the key to find in the dictionary, string
    :param unit2docid: the dictionary to search in, dictionary
    :return: the value (id) of the closest match'''
    # Find the closest match in the dictionary keys
    closest_match = difflib.get_close_matches(key_to_find, unit2docid.keys(), n=1, cutoff=0.6)
    value = None
    if closest_match:
        # print(f"Closest match found: {closest_match[0]}")
        value = unit2docid[closest_match[0]]
        # print(f"Value: {unit2docid[closest_match[0]]}")
    else:
        print("No close match found")
    return value
    
    
    cleaned_key = General.clean_text(key_to_find)
    cleaned_match = General.clean_text(closest_match[0])
    
    clean_key = General.clean_text(top_doc_key_j)
    cleaned_key = unit2docid[clean_key]
    
    
    if cleaned_key.__eq__(cleaned_match):
        print("True")
    orig = unit2docid[closest_match[0]] # This has "" around it must remove it. I believe.
    
    
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
            


def get_summary(api_base, token, model_name, system_message, user_message):

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
    
