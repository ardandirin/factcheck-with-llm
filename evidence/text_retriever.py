import requests
import argparse
from bs4 import BeautifulSoup
from helpers import json_loader as JsonLoader
import certifi
from helpers import general as General
import json
import logging
from logger_config import setup_logging  # This will configure the logging

sample_url = "https://whorulesamerica.ucsc.edu/power/history_of_labor_unions.html"
url = "https://www.hrw.org/report/2018/02/28/freezer/abusive-conditions-women-and-children-us-immigration-holding-cells"
logger = logging.getLogger(__name__)

websites = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/websites.jsonl'
out_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/deneme.jsonl'
results = JsonLoader.json_loader(websites)


class Retriever:
    def __init__(self, args):
        self.args = args
        self.websites_path = args.websites_path
        self.output_path = args.output_path
         


    def process_jsonl_file(self, no_info=0):
        
        ''' Process a jsonl file and aggregate the results for each question in each line
        :param jsonl_file_path: path to the jsonl file
        :param output_file_path: path to the output file'''

        with open(self.websites_path, 'r') as file, open(self.output_path, 'w', encoding='utf-8') as out:
            for line in file:
                entries = json.loads(line)  # load an entry from the jsonl (websites) file
                aggregated_results = {} # agrregate the results for each question
                for entry in entries:
                    question = entry['question']
                    if question not in aggregated_results:
                        aggregated_results[question] = ""
                    # Check if there is info
                    if entry['url'] == "No URL":
                        no_info += 1
                    
                    # Retrieve the text from the website
                    web_content = General.get_text(entry['url'])
                    # print(web_content)
                    if web_content != None:
                        num_of_words = General.count_words(web_content)
                        if num_of_words <= 20:
                            print(web_content)
                    
                    aggregated_results[question] += f"\n\n{(entry['url'])}"

                line_results = [{'question': question, 'aggregated_text': text} for question, text in aggregated_results.items()]
                json.dump(line_results, out, ensure_ascii=False)
                out.write('\n')
            print(f"Number of entries with no info: {no_info}")
            return no_info


def parse_args():
    parser = argparse.ArgumentParser(description='Process a jsonl file and aggregate the results for each question in each line')

    parser.add_argument('--websites_path', default='./ClaimDecomp/websites.jsonl', type=str)
    parser.add_argument('--output_path', default='./ClaimDecomp/deneme.jsonl', type=str)
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    retriever = Retriever(args)
    retriever.process_jsonl_file()


