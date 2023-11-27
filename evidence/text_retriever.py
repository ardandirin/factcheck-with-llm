import requests
from bs4 import BeautifulSoup
from helpers import json_loader as JsonLoader
import certifi

sample_url = "https://whorulesamerica.ucsc.edu/power/history_of_labor_unions.html"

# Send a GET request to the URL
response = requests.get(sample_url, verify=certifi.where())

# Check if the request was successful
if response.status_code == 200:
    # Parse the content of the request with Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Now you can navigate and extract data from the soup object
    # For example, to get all text from the page:
    page_text = soup.get_text()

    # Or, to find a specific element, like a div with a specific class:
    specific_div = soup.find('div', {'class': 'your-class-name'})

    print(page_text)  # or use specific_div to do something with that specific div
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")