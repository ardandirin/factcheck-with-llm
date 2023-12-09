import requests
import argparse
from bs4 import BeautifulSoup
from helpers import json_loader as JsonLoader
import certifi
from helpers import general as General
import json
import logging
from logger_config import setup_logging

sample_url = "https://whorulesamerica.ucsc.edu/power/history_of_labor_unions.html"
url = "https://www.hrw.org/report/2018/02/28/freezer/abusive-conditions-women-and-children-us-immigration-holding-cells"
logger = logging.getLogger(__name__)

websites = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/websites.jsonl'
out_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/deneme.jsonl'
results = JsonLoader.json_loader(websites)


no_url = 0
no_info = 0
responses = {
    'success': 0,
    'ssl': 0,
    'http': 0,
    'connection': 0,
    'timeout': 0,
    'request': 0,
    'other': 0
}


# def add_id(subquestions_path, answers_path):
#     ''' Add id to the websites.jsonl file
#     :param subquestions_path: path to the subquestions.jsonl file
#     :param websites_path: path to the websites.jsonl file
#     :return: a list of dictionaries with id, question, url, and prompt
#     '''
#     subquestions = JsonLoader.json_loader(subquestions_path)
#     answers = JsonLoader.json_loader(answers_path)
#     for i in enumerate(subquestions):
#         answers['example_id'] = subquestions[i].get('example_id', None)
        
            
        
def get_text(url):
    # Send a GET request to the URL
    '''
    :param url: url of the website
    :return: the text of the website
    update the responses dictionary with the status of the request
    '''
    page_text = None

    try:
        request = requests.get(url, verify= certifi.where(), timeout=5)
        status = request.status_code
        request.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        # Check if the request was successful
        if status == 200:
            # Parse the content of the request with Beautiful Soup
            soup = BeautifulSoup(request.content, 'html.parser')
            page_text = soup.get_text()
            responses['success'] += 1
        else:
            print(f"Failed to retrieve the webpage. Status code: {status}")
            responses['other'] += 1
            
    except requests.exceptions.SSLError as ssl_error:
        logging.error(f"SSL Error encountered for URL {url}: {ssl_error}")
        responses['ssl'] += 1
    except requests.exceptions.HTTPError as errh:
        logging.error(f'Failed to retrieve the webpage {url}: {errh}')
        responses['http'] += 1
    except requests.exceptions.ConnectionError as errc:
        logging.error(f'Connection Error for URL {url}: {errc}')
        responses['connection'] += 1
    except requests.exceptions.Timeout as errt:
        logging.error(f'Timeout Error encountered for URL {url}: {errt}')
        responses['timeout'] += 1
    except requests.exceptions.RequestException as err:
        logging.error(f'Error encountered for URL {url}: {err}')
        responses['request'] += 1
        
    return page_text
        


def process_jsonl_file(websites_path, output_path, no_url=0):
    
    ''' Process a jsonl file and aggregate the results for each question in each line
    :param jsonl_file_path: path to the jsonl file
    :param output_file_path: path to the output file'''

    with open(websites_path, 'r') as file, open(output_path, 'w', encoding='utf-8') as out:
        for line in file:
            entries = json.loads(line)  # load an entry from the jsonl (websites) file
            aggregated_results = {} # agrregate the results for each question
            answer_list = [] # a list to store the answers
            for entry in entries:
                question = entry['question']
                if question not in aggregated_results:
                    aggregated_results[question] = ""
                # Check if URL exists
                if entry['url'] == "No URL":
                    no_url += 1
                
                # Retrieve the text from the website
                # print(entry)
                web_content = get_text(entry['url'])
                # print(web_content)
                if web_content != None:
                    num_of_words = General.count_words(web_content)
                    # if num_of_words <= 20:
                        # print(web_content)
                    # if num_of_words > 20:
                        # answer_list.append(web_content)
                    print(f"Number of words: {num_of_words}")
                
                # aggregated_results[question] += f"\n\n{(entry['url'])}"
                if web_content != None:
                    # Clean the text and add it to the list
                    cleaned_answer = General.postprocess_text(web_content)
                    # print(f'Cleaned answer: {cleaned_answer}')
                    answer_list.append(cleaned_answer)
                
                # aggregated_results[question] += f"\n\n{(entry['url'])}"
                # aggregated_results[question].append(answer_list)

            line_results = {'question': question, 'aggregated_text': answer_list}
            # line_results = [{'question': question, 'aggregated_text': text} for question, text in aggregated_results.items()]
            json.dump(line_results, out, ensure_ascii=False)
            out.write('\n')
        print(f"Number of entries with no url: {no_url}")
        print(f"Errors: {responses}")



# def process_chunk(websites_path, output_path):
    
    
    


def parse_args():
    parser = argparse.ArgumentParser(description='Process a jsonl file and aggregate the results for each question in each line')
    parser.add_argument('--websites_path', default='./ClaimDecomp/websites.jsonl', type=str)
    parser.add_argument('--output_path', default='./ClaimDecomp/deneme.jsonl', type=str)
    parser.add_argument('--subquestions_path', default='./ClaimDecomp/subquestions_finetuned.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
   
    process_jsonl_file(args.websites_path, args.output_path)
    # add_id(args.subquestions_path, args.websites_path) # Add id

