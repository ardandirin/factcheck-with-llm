import requests
from bs4 import BeautifulSoup
from helpers import json_loader as JsonLoader
import certifi
from helpers import general as General
import json

sample_url = "https://whorulesamerica.ucsc.edu/power/history_of_labor_unions.html"
url = "https://www.hrw.org/report/2018/02/28/freezer/abusive-conditions-women-and-children-us-immigration-holding-cells"

websites = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/websites.jsonl'
out_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/deneme.jsonl'
results = JsonLoader.json_loader(websites)

def process_jsonl_file(jsonl_file_path, output_file_path):
    
    ''' Process a jsonl file and aggregate the results for each question in each line
    :param jsonl_file_path: path to the jsonl file
    :param output_file_path: path to the output file'''

    with open(jsonl_file_path, 'r') as file, open(output_file_path, 'w', encoding='utf-8') as out:
        for line in file:
            entries = json.loads(line)  # load an entry from the jsonl (websites) file
            aggregated_results = {} # agrregate the results for each question
            for entry in entries:
                question = entry['question']
                if question not in aggregated_results:
                    aggregated_results[question] = ""
                aggregated_results[question] += f"\n\n{(entry['url'])}"

            line_results = [{'question': question, 'aggregated_text': text} for question, text in aggregated_results.items()]
            json.dump(line_results, out, ensure_ascii=False)
            out.write('\n')


process_jsonl_file(websites, out_file)



