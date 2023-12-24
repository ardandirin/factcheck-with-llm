# factcheck-with-llm - Thesis


## Prerequisties 

### Create conda environment
```
conda create -n your_environment_name
conda activate your_environment name
```
Download the necessary codes
```
pip install -r requirements.txt
```



### Evidence Retrieval
The script "web_api_retrieval.py" retrieves websites via Google Custom Search API, a web api key, as well as search engine id must be acquired from Google's official API, and placed in a .env file.

Google allows only 100 queries per day, therefore the code was run on a span of multiple days to acquire for 200 lines in the subquestions_finetuned.jsonl file


### Websites Retriever
Does Web queries using Google custom search API:
And creates websites jsonl file as output.
python -m evidence.web_api_retriever \
    --subquestion_path "./ClaimDecomp/subquestions_finetuned.jsonl" \
    --websites_path "./ClaimDecomp/websites.jsonl" \
    --web_api_key "Your web API goes here" \
    --search_engine_id "search engine id goes here" \
    


### Text Retriever

text_retriever.py uses BeautifulSoup to retrieve text from those websites. To run the command the arguments must be given:

```
python -m evidence.text_retriever \
    --websites_path "./ClaimDecomp/websites.jsonl"
    --output_path  "./ClaimDecomp/answers.jsonl"
```




### BM25 Retriever

Also need to download nltk
```
import nltk
nltk.download('punkt')
```

Here we segment each answer to some number of segments (with token length 1500) and retrieve the most relavent parts of the text using BM25 ranker.

python -m evidence.bm25_retriever.py \
    --corpus_path "./ClaimDecomp/deneme.jsonl"
    --original_test_path "./ClaimDecomp/test.jsonl"
    --top_docs_path "./ClaimDecomp/top_docs_simple.jsonl"
