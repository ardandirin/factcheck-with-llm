import requests
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper
from dotenv import load_dotenv
import os

# Load the variables from .env
load_dotenv()

# Access the API key
web_api_key = os.getenv('WEB_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')

print(web_api_key)  # Prints your API key


# Define the query you want to search for
query = "Did Trump say he was excited for the 2008 housing crash?"
pdf_filter = ' -filetype:pdf'
url = 'https://www.googleapis.com/customsearch/v1'

subquestion_path = '/Users/arda/thesis/factCheck/ClaimDecomp/subquestions_finetuned.jsonl'

data = JsonLoader.json_loader(subquestion_path)

converted_date = DateHelper.extract_date('stated on April 30, 2018')

print(converted_date)

params = {
    'key': web_api_key,
    'cx': search_engine_id,
    'q': query + pdf_filter,
    'num': 10,
    # 'sort':'date:r:20000101:' + converted_date,
    }


# response = requests.get(url, params=params).json()

# print(response)

# for item in response['items']:
#     print(item['link'])
#     print(item['snippet'])
#     print() 