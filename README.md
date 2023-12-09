# factcheck-with-llm
## Thesis


# Prerequisties 
Download the necessary codes
```
pip install -r requirements.txt
```



# Evidence Retrieval
The script "web_api_retrieval" retrieves websites via Google Custom Search API, a web api key, as well as search engine id must be acquired from Google's official API, and placed in a .env file.

Google allows only 100 queries per day, therefore the code was run on a span of multiple days to acquire for 200 lines in the subquestions_finetuned.jsonl file


text_retriever.py uses BeautifulSoup to retrieve text from those websites in order to run the command the arguments must be given:

```
python -m evidence.text_retriever \
    --websites_path "./ClaimDecomp/websites.jsonl"
    --output_path  "./ClaimDecomp/answers.jsonl"
```
