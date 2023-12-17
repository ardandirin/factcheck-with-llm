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

    
    
def sequence_overlap(segment1, segment2, window_size=100):
    """
    Check if there is a significant overlap between two segments.
    :param segment1: First segment (list of words).
    :param segment2: Second segment (list of words).
    :param window_size: Size of the window to check for overlap.
    :return: Boolean indicating if there is an ordered overlap.
    """
    for i in range(len(segment1) - window_size + 1):
        window = segment1[i:i + window_size]
        window_str = " ".join(window)
        if window_str in " ".join(segment2):
            return window_str
    return None


def count_words(text):
    words = text.split()
    return len(words)