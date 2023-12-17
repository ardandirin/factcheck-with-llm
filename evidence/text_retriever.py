import requests
import argparse
from bs4 import BeautifulSoup
from helpers import json_loader as JsonLoader
import certifi
from helpers import general as General
import json
import logging
from logger_config import setup_logging
import matplotlib.pyplot as plt
from tqdm import tqdm

logger = logging.getLogger(__name__)

# websites = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/websites.jsonl'
# out_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/deneme.jsonl'
# results = JsonLoader.json_loader(websites)


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
            # print(f"Failed to retrieve the webpage. Status code: {status}")
            responses['other'] += 1
            
    except requests.exceptions.SSLError as ssl_error:
        # logging.error(f"SSL Error encountered for URL {url}: {ssl_error}")
        responses['ssl'] += 1
    except requests.exceptions.HTTPError as errh:
        # logging.error(f'Failed to retrieve the webpage {url}: {errh}')
        responses['http'] += 1
    except requests.exceptions.ConnectionError as errc:
        # logging.error(f'Connection Error for URL {url}: {errc}')
        responses['connection'] += 1
    except requests.exceptions.Timeout as errt:
        # logging.error(f'Timeout Error encountered for URL {url}: {errt}')
        responses['timeout'] += 1
    except requests.exceptions.RequestException as err:
        # logging.error(f'Error encountered f
        # or URL {url}: {err}')
        responses['request'] += 1
        
    return page_text
        

def process_jsonl_file(websites_path, output_path):
    '''Process a jsonl file and aggregate the results for each question in each line'''
    no_url = 0
    no_web_content = 0
    word_counts = []

    with open(websites_path, 'r') as file, open(output_path, 'w', encoding='utf-8') as out:
        for line in tqdm(file):
            entries = json.loads(line)
            aggregated_results = {}

            for entry in entries:
                question = entry['question']
                if question not in aggregated_results:
                    aggregated_results[question] = []

                if entry['url'] == "No URL":
                    no_url += 1
                    continue

                web_content = get_text(entry['url'])
                if web_content is None:
                    no_web_content += 1
                    continue

                num_of_words = General.count_words(web_content)
                cleaned_answer = General.postprocess_text(web_content)
                aggregated_results[question].append(cleaned_answer)
                word_counts.append(num_of_words)

            json.dump(aggregated_results, out, ensure_ascii=False)
            out.write('\n')

        
        print(f"Number of entries with no url: {no_url}")
        print(f"Number of entries with no retrieved web content: {no_web_content}")
        print(f"Total number of queries: {sum(responses.values())}")
        print(f"Results: {responses}")

    return word_counts




# def process_chunk(websites_path, output_path):

def save_word_counts(word_counts, output_path):
    with open(output_path, 'w') as f:
        json.dump(word_counts, f)
    print(f"Word counts saved to {output_path}")
    


def plot_word_counts(word_counts):
    # Plotting the distribution of mean_scores
    plt.figure(figsize=(10, 6))
    plt.hist(word_counts, bins=50, edgecolor='black')  # Adjust bins as needed
    plt.title('Distribution of word counts of websites')
    plt.xlabel('Word Count')
    plt.ylabel('Frequency')
    # Save the plot
    plt.savefig('word_counts.png', dpi=300)  # Saves the plot as a PNG file
    plt.show()
    
    
    
    


def parse_args():
    parser = argparse.ArgumentParser(description='Process a jsonl file and aggregate the results for each question in each line')
    parser.add_argument('--websites_path', default='./ClaimDecomp/websites.jsonl', type=str)
    parser.add_argument('--output_path', default='./ClaimDecomp/deneme.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
   
    word_counts = process_jsonl_file(args.websites_path, args.output_path)
    save_word_counts(word_counts, './ClaimDecomp/word_counts.json')
    plot_word_counts(word_counts)

