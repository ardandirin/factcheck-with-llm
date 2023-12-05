import requests
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper
from dotenv import load_dotenv
import os
import json

# Load the variables from .env
load_dotenv()

# Access the API key
web_api_key = os.getenv('WEB_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')

api_usage_count = 0
api_usage_limit = 100


# Define the query you want to search for
# placeholder = "Did Trump say he was excited for the 2008 housing crash?"
pdf_filter = ' -filetype:pdf'
url = 'https://www.googleapis.com/customsearch/v1'

subquestion_path = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/subquestions_finetuned.jsonl'
websites_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/websites.jsonl'
start_date = '20000101'

params = {
    'key': web_api_key,
    'cx': search_engine_id,
    'q': '_',
    'num': 10,
    'sort':'date:r',
    }


def update_params(query, end_date):
    # Update params query and date range
    params['q'] = query + pdf_filter
    print(params['q'])
    params['sort'] = 'date:r:' + start_date + ':' + end_date
    print(params['sort'])
    return params



# Function to process a line and make API calls
def process_line(line):
    ''' Process a line from the input file and make API calls
    :param line: a line from the input file
    :return: a list of search results
    '''
    questions_list = JsonLoader.list_returner(line)
    date = DateHelper.extract_date(line['prompt'])
    search_results = []
    for q in questions_list:
        params = update_params(q, date)
        response = requests.get(url, params=params).json()
        global api_usage_count
        api_usage_count += 1
        print(response)
        if 'items' in response:
            for item in response['items']:
                result = {
                    'question': q,
                    'url': item.get('link', 'No URL'),
                    'title': item.get('title', 'No Title'),
                    'snippet': item.get('snippet', 'No Snippet')
                }
                search_results.append(result)
        else:
            print(f"No items found for query: {q}")
            result = {
                'question': q,
                'url': 'No URL',
                'title': 'No Title',
                'snippet': 'No Snippet'
            }
            search_results.append(result)

    return search_results


def count_lines(websites_file):
    with open(websites_file, 'r') as f:
        processed_lines = sum(1 for line in f)
    return processed_lines


process_lines = 0
print(f'processed_lines: {process_lines}')

def write_to_file(subquestion_path, websites_file, num_lines_to_process):
    processed_lines = count_lines(websites_file)
    # Process the input file
    with open(subquestion_path, 'r') as f_input, open(websites_file, 'a') as f_output:
        for i, line in enumerate(f_input):
            if i >= num_lines_to_process:
                break  # Stop after processing the desired number of lines

            if i < processed_lines:  # Skip already processed lines
                continue

            if api_usage_count >= api_usage_limit - 5:
                break  # Stop if API limit is reached
            line = json.loads(line.strip())
            # print(line)
            result = process_line(line)
            f_output.write(json.dumps(result) + '\n')

        
        
def main():
    write_to_file(subquestion_path, websites_file, num_lines_to_process=170)
    
    
if __name__ == "__main__":
    main()