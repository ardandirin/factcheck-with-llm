
import re
from dateutil.parser import parse


def convert_date_to_ymd(date_string):
    '''Converts a date string to YYYYMMDD format
    Args:
        date_string (str): A date string in the format of "stated on [month] dd, yyyy"
        Returns:
            str: A date string in the format of YYYYMMDD
    Examples:
        >>> convert_date_to_ymd('stated on January 23, 2018')
        '20180123'
    '''
    date_obj = parse(date_string)
    return date_obj.strftime('%Y%m%d')

def extract_date(string):
    '''Extracts a date from a string using regex
    Args:
        string (str): A string that may contain a date
        Returns:
            datetime: A datetime object representing the date in the string
        Examples:
            >>> extract_date('stated on January 23, 2018')
            
    '''
    # Regex pattern for "stated on [month] dd, yyyy"
    pattern = r'stated on (\b\w+\b) (\d{1,2}), (\d{4})'
    
    match = re.search(pattern, string)
    if match:
        date_string = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
        # Parse the date string into a datetime object
        return convert_date_to_ymd(date_string)
    
    else:
        return None
    
def date_extracter(data):
    print("date_extracter called")
    try:
        date_string = extract_date(data["prompt"])
    except:
        date_string = None

    return date_string
