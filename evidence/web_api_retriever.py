import requests
import argparse
from helpers import json_loader as JsonLoader
from helpers import date_helper as DateHelper
from dotenv import load_dotenv
import os
import json

# Load the variables from .env
load_dotenv()

# Access the API key

api_usage_count = 0
api_usage_limit = 10000


# Define the query you want to search for
# placeholder = "Did Trump say he was excited for the 2008 housing crash?"
pdf_filter = ' -filetype:pdf'
url = 'https://www.googleapis.com/customsearch/v1'

class WebRetriever:
    def __init__(self, args):
        self.args = args
        self.subquestion_path = args.subquestion_path
        self.websites_path = args.websites_path
        self.start_date = '20000101'
        self.params = {
            'key': args.web_api_key,
            'cx': args.search_engine_id,
            'q': '_',
            'num': 10,
            'sort':'date:r',
        }



    def update_params(self, query, end_date):
        # Update params query and date range
        self.params['q'] = query + pdf_filter
        print(self.params['q'])
        self.params['sort'] = 'date:r:' + self.start_date + ':' + end_date
        print(self.params['sort'])
        return self.params



    # Function to process a line and make API calls
    def process_line(self, line):
        ''' Process a line from the input file and make API calls
        :param line: a line from the input file
        :return: a list of search results
        '''
        # questions_list = JsonLoader.list_returner(line) # For GPT3.5 finetuned
        questions_list = JsonLoader.list_returner_q_mark(line) # For Mixtral and gpt icl
        print(questions_list)
        # end_date = DateHelper.extract_date(line['prompt'])
        end_date = DateHelper.extract_date(line['claim'])

        search_results = []
        for q in questions_list:
            params = self.update_params(q, end_date)
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


    def count_lines(self):
        with open(self.websites_path, 'r') as f:
            processed_lines = sum(1 for line in f)
        return processed_lines




    def write_to_file(self, num_lines_to_process):
        process_lines = self.count_lines()  # Count the number of lines already processed and continue from the last line
        print(f'processed_lines: {process_lines}')
        # processed_lines = self.count_lines()
        # Process the input file
        with open(self.subquestion_path, 'r') as f_input, open(self.websites_path, 'a') as f_output:
            for i, line in enumerate(f_input):
                if i >= num_lines_to_process:
                    break  # Stop after processing the desired number of lines

                if i < process_lines:  # Skip already processed lines
                    continue

                if api_usage_count >= api_usage_limit - 5:
                    break  # Stop if API limit is reached
                line = json.loads(line.strip())
                # print(line)
                result = self.process_line(line)
                f_output.write(json.dumps(result) + '\n')
                

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subquestion_path', default='./Data/1_Subquestions/subquestions_icl_gpt_all.jsonl', type=str)
    parser.add_argument('--websites_path', default='./Data/2_Websites/websites_gpt_all.jsonl', type=str)
    parser.add_argument('--web_api_key', default=os.getenv('WEB_API_KEY'), type=str)
    parser.add_argument('--search_engine_id', default=os.getenv('SEARCH_ENGINE_ID'), type=str)
    args = parser.parse_args()
    return args   
        


if __name__ == "__main__":
    args = parse_args()
    webRetriever = WebRetriever(args)
    webRetriever.write_to_file(num_lines_to_process=1200)