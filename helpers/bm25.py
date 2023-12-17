from rank_bm25 import BM25Okapi
from typing import List
import numpy as np

class BM25Retriever:
    def __init__(self, corpus: List[List[str]]):
        self.corpus = corpus
        self.retriever = BM25Okapi(corpus)
    
    def get_top_n_doc(self, query: List[str], num: int):
        scores = self.retriever.get_scores(query)
        top_n = np.argsort(scores)[::-1][:num]
        docs = [self.corpus[i] for i in top_n]
        scores = [scores[i] for i in top_n]
        return docs, scores
