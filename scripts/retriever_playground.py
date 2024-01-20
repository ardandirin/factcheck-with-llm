from googlesearch import search
from helpers import json_loader as JsonLoader
# from helpers import date_helper as DateHelper
pdf_filter = ' -filetype:pdf'
# url = 'https://www.googleapis.com/customsearch/v1'

subquestion_path = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/subquestions_finetuned.jsonl'
websites_file = '/Users/arda/thesis/factcheck-with-llm/ClaimDecomp/deneme.jsonl'
start_date = '20000101'

params = {
    'q': '_',
    'num': 10,
    'sort':'date:r',
    }

def update_params(query, end_date):
    # Update params query and date range
    params['q'] = query + pdf_filter
    print(params['q'])
    params['sort'] = 'date:r:' + start_date + ':' + end_date
    print(params['sort'])
    return params





results = search("Was Trump exiceted for the 2008 crahs?  after:2000-01-01 before:2018-09-10", advanced=True)

# Iterate over the generator to get each result
for result in results:
    print(f"URL: {result.url}")
    print(f"Title: {result.title}")
    print(f"Description: {result.description}")
    print()  # Just for an extra newline for readability


# print(obj[0])