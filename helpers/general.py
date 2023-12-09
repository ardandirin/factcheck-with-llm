import requests
import certifi
from bs4 import BeautifulSoup
import logging
import re


def postprocess_text(text):
    '''
    :param text: the text of the website
    :return: the processed text
    Given a text, remove newlines, tabs, and extra spaces
    '''
    cleaned = text.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    # Optional, remove spaces before and after punctuation
    cleaned = re.sub(r'\s+([?.!,:;])', r'\1', cleaned)
    return cleaned

    
    


def count_words(text):
    words = text.split()
    return len(words)