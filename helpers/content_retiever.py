import requests
import certifi
import bs4 as BeautifulSoup

def get_text(url):
    # Send a GET request to the URL
    try:
        response = requests.get(url, verify= certifi.where())

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content of the request with Beautiful Soup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Now you can navigate and extract data from the soup object
            # For example, to get all text from the page:
            page_text = soup.get_text()

            # # Or, to find a specific element, like a div with a specific class:
            # specific_div = soup.find('div', {'class': 'your-class-name'})

            # print(page_text)  # or use specific_div to do something with that specific div
            return(page_text)
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error encountered for URL {url}: {ssl_error}")
        # Handle the error or log it
        # Optionally, retry with SSL verification disabled (not recommended)
        return None