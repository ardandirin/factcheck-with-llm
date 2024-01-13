# factcheck-with-llm - Thesis

![Pipeline with Web Retrieval](factcheck.png?raw=true "Pipeline")

## Prerequisties

### Create conda environment

```bash
conda create -n factcheck
conda activate factcheck
```

Download the necessary libraries

 ```bash
pip install -r requirements.txt
 ```

#### Anyscales Endpoints are used in the following parts

So need to set api key and base url. It can be done by registering in their [website](https://www.anyscale.com)

```bash
export OPENAI_BASE_URL="https://api.endpoints.anyscale.com/v1"
export OPENAI_API_KEY="YOUR_ANYSCALE_ENDPOINT_API_KEY"
```

## The Data

The data used in this project is from this GitHub Repository [subquestions-for-fact-checking](https://github.com/jifan-chen/subquestions-for-fact-checking) by Jifan Chen

### Evidence Retrieval

The script "web_api_retrieval.py" retrieves websites via Google Custom Search API, a web api key, as well as search engine id must be acquired from Google's official API, and placed in a .env file.

Google allows only 100 queries per day, therefore the code was run on a span of multiple days to acquire for 200 lines in the subquestions_finetuned.jsonl file

### Websites Retriever

Does Web queries using Google custom search API:
And creates websites jsonl file as output.
Google Custom Search API is used and following websites are excluded from the search, as well as in the code
there is time constraints (the searches are before the claim was made). Moreover, Google Custom Search API allows only 100 free queries per day, therefore the data for the whole test set (200 claims wiht multiple subquestions in each) are created in about a span of a week.

```bash
python3 -m evidence.web_api_retriever \
    --subquestion_path "./ClaimDecomp/subquestions_finetuned.jsonl" \
    --websites_path "./DataProcessed/websites.jsonl" \
    --web_api_key "Your web API goes here" \
    --search_engine_id "search engine id goes here" \
```

### Text Retriever

text_retriever.py uses BeautifulSoup to retrieve text from those websites. To run the command the arguments must be given:

```bash
python3 -m evidence.text_retriever \
    --websites_path "./DataProcessed/websites.jsonl" \
    --output_path  "./DataProcessed/answers.jsonl"
```

### BM25 Retriever

Also need to download nltk

```python
import nltk
nltk.download('punkt')
```

Here we segment each answer to some number of segments (with token length 1500) and retrieve the most relavent parts of the text using BM25 ranker. If segments are the same they are removed and if there is a significant overlap, they are merged, you can see the detail in the log file -> bm25.out at the very end. Initially we have 4 segments for each claim.

```bash
python3 -m evidence.bm25_retriever.py \
    --corpus_path './DataProcessed/answers.jsonl' \
    --original_test_path "./ClaimDecomp/test.jsonl" \
    --top_docs_path "./DataProcessed/top_docs_final.jsonl"
```

### Summarize

Summarazies the relavent parts retrieved from BM25 and stores them in summaries_final.jsonl

```bash
python3 -m evidence.summarize \
    --corpus_path "./DataProcessed/top_docs_final.jsonl" \
    --test_path "./ClaimDecomp/test.jsonl" \
    --output_path "./DataProcessed/summaries_final.jsonl" \
    --model_name "meta-llama/Llama-2-70b-chat-hf"
```

### Verdict

Here the summaries are given to the LLM with the subquestion to answer it with yes or no.

```bash
python3 veracity_classifier.py 
```
