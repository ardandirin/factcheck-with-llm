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

#### Anyscales Endpoints are used in the following parts.
So need to set api key and base url. It can be done by registering in their [website](https://www.anyscale.com)
```bash
export OPENAI_BASE_URL="https://api.endpoints.anyscale.com/v1"
export OPENAI_API_KEY="YOUR_ANYSCALE_ENDPOINT_API_KEY"
```


### Evidence Retrieval

The script "web_api_retrieval.py" retrieves websites via Google Custom Search API, a web api key, as well as search engine id must be acquired from Google's official API, and placed in a .env file.

Google allows only 100 queries per day, therefore the code was run on a span of multiple days to acquire for 200 lines in the subquestions_finetuned.jsonl file

### Websites Retriever

Does Web queries using Google custom search API:
And creates websites jsonl file as output.
```bash
python3 -m evidence.web_api_retriever \
    --subquestion_path "./ClaimDecomp/subquestions_finetuned.jsonl" \
    --websites_path "./ClaimDecomp/websites.jsonl" \
    --web_api_key "Your web API goes here" \
    --search_engine_id "search engine id goes here" \
```

### Text Retriever

text_retriever.py uses BeautifulSoup to retrieve text from those websites. To run the command the arguments must be given:

```bash
python3 -m evidence.text_retriever \
    --websites_path "./ClaimDecomp/websites.jsonl" \
    --output_path  "./ClaimDecomp/answers.jsonl"
```

### BM25 Retriever

Also need to download nltk

```python
import nltk
nltk.download('punkt')
```

Here we segment each answer to some number of segments (with token length 1500) and retrieve the most relavent parts of the text using BM25 ranker.

```bash
python3 -m evidence.bm25_retriever_new.py \
    --corpus_path './ClaimDecomp/answers.jsonl' \
    --original_test_path "./ClaimDecomp/test.jsonl" \
    --top_docs_path "./ClaimDecomp/top_docs_final.jsonl"
```


### Summarize

Summarazies the relavent parts retrieved from BM25 and stores them in summaries.jsonl
```bash
python3 -m evidence.summarize_new \
    --corpus_path "./DataProcessed/top_docs_final.jsonl" \
    --test_path "./ClaimDecomp/test.jsonl" \
    --output_path "./DataProcessed/summaries_final.jsonl" \
    --model_name "meta-llama/Llama-2-70b-chat-hf"
```

### Veracity Classifier

The final step of the pipeline. Here the summaries are given to the LLM along with the claim for context as well as the subquestion to answer it with yes/no

```bash
python3 veracity_classifier.py 
```