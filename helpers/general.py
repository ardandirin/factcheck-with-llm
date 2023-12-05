import requests
import certifi
from bs4 import BeautifulSoup
import logging

def get_text(url):
    # Send a GET request to the URL
    page_text = None
    try:
        request = requests.get(url, verify= certifi.where(), timeout=10)
        status = request.status_code
        request.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        # Check if the request was successful
        if status == 200:
            # Parse the content of the request with Beautiful Soup
            soup = BeautifulSoup(request.content, 'html.parser')
            page_text = soup.get_text()
            # print(page_text)  # or use specific_div to do something with that specific div
            return(page_text)
        else:
            print(f"Failed to retrieve the webpage. Status code: {status}")
            
    except requests.exceptions.SSLError as ssl_error:
        logging.error(f"SSL Error encountered for URL {url}: {ssl_error}")
    except requests.exceptions.HTTPError as errh:
        logging.error(f'Failed to retrieve the webpage {url}. Status code: {errh}')
    except requests.exceptions.ConnectionError as errc:
        logging.error(f'Connection Error for URL {url}: {errc}')
    except requests.exceptions.Timeout as errt:
        logging.error(f'Timeout Error encountered for URL {url}: {errt}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error encountered for URL {url}: {err}')
        
    return page_text


def count_words(text):
    words = text.split()
    return len(words)