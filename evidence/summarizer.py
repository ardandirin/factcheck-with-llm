# from transformers import pipeline
import argparse
from helpers import json_loader as JsonLoader
from helpers import general as General
import json
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from typing import List
from helpers.bm25 import BM25Retriever
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")



def segment_answer(answer: str, segment_size: int = 1000) -> List[str]:
    words = word_tokenize(answer)
    segments = []
    for i in range(0, len(words), segment_size):
        segment = ' '.join(words[i:i + segment_size])
        segments.append(segment)
    return segments

def are_segments_identical(seg1: str, seg2: str) -> bool:
    return seg1 == seg2


def main(corpus_path, original_test_path):    
    # Read and process the JSONL file
    text_units = []
    questions = []
    index = 0 # Index for the claim
    
    test_file = open(original_test_path, 'r')
    # JsonLoader.reconstruct_dataset(corpus_path, original_test_path)
    

    with open(corpus_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            for question, answers in data.items():
                questions.append(question)
                for answer in answers:
                    segments = segment_answer(answer)
                    text_units.extend(segments)

    # Initialize BM25Retriever with the segmented answers
    bm25_retriever = BM25Retriever([word_tokenize(segment) for segment in text_units])

    # Example: Scoring segments for the first question
    query = word_tokenize(questions[0])
    top_docs, scores = bm25_retriever.get_top_n_doc(query, 4)

    # Output the results
    for doc, score in zip(top_docs, scores):
        print("Segment:", ' '.join(doc))
        print("Score:", score)
        print("---")
        
        # Process for identifying and handling overlaps
    for i in range(len(top_docs)):
        for j in range(i + 1, len(top_docs)):
            if are_segments_identical(top_docs[i], top_docs[j]):
                print(f"Identical segments found: Document {i} and {j}")
                # Handle the identical segments (e.g., remove one)
            else:
                overlap = General.sequence_overlap(top_docs[i], top_docs[j]) # This function needs to be defined
                if overlap:
                    print(f"Ordered overlap found between document {i} and {j}: '{overlap}'")
                    # Handle the overlap (e.g., merge segments)

    # # Assuming top_docs is the list of top documents from the BM25 retriever
    # for i in range(len(top_docs)):
    #     for j in range(i + 1, len(top_docs)):
    #         overlap = General.sequence_overlap(top_docs[i], top_docs[j])
    #         if overlap:
    #             print(f"Ordered overlap found between document {i} and {j}: '{overlap}'")

                        
    



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./ClaimDecomp/deneme.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path)