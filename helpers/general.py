import requests
import certifi
import bs4 as BeautifulSoup
import logging

def get_text(url):
    # Send a GET request to the URL
    try:
        request = requests.get(url, verify= certifi.where(), timeout=10)
        status = request.status_code
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
        print(f"SSL Error encountered for URL {url}: {ssl_error}")
        # Handle the error or log it
        # Optionally, retry with SSL verification disabled (not recommended)
        return None