import argparse
from helpers import general as General
from helpers import segmenter as Segmenter
import json
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from helpers.bm25 import BM25Retriever
from tqdm import tqdm

def main(corpus_path, original_test_path, top_docs_path):
    with open(corpus_path, 'r', encoding='utf8') as file, open(original_test_path, 'r', encoding='utf8') as test_data:
        final_data = []
        for corpus_line, test_line in tqdm(zip(file, test_data)):
            data_to_write = []
            test_data = json.loads(test_line)
            corpus_data = json.loads(corpus_line)
            example_id = corpus_data['example_id']

            for question, responses in corpus_data['questions'].items():
                print("New question")
                segment_data = []  # A list of tuples containing a segment and its span
                for response in responses:
                    content = response['content']
                    segment_dict = Segmenter.segment_answer(content)
                    for segment, span in segment_dict.items():
                        segment_data.append((segment, span, response))  # Include response metadata

                # Tokenize each segment for the BM25Retriever
                tokenized_segments = [word_tokenize(segment) for segment, _, _ in segment_data]
                bm25_retriever = BM25Retriever(tokenized_segments)

                query = word_tokenize(question)
                top_docs_tokenized, scores = bm25_retriever.get_top_n_doc(query, 4)

                top_docs_data = []
                for top_doc_tokenized, score in zip(top_docs_tokenized, scores):
                    # Match tokenized top docs with original segments
                    match_index = next((i for i, (segment, _, _) in enumerate(segment_data) if word_tokenize(segment) == top_doc_tokenized), None)
                    if match_index is not None:
                        original_segment, _, response_metadata = segment_data[match_index]
                        print("Score:", score)
                        print("---")
                        top_doc = {
                            'url': response_metadata['url'],
                            'snippet': response_metadata['snippet'],
                            'title': response_metadata['title'],
                            'segment': original_segment,
                            'score': score
                        }
                        top_docs_data.append(top_doc)

                distilled_ans = {
                    'question': question,
                    'top_docs': top_docs_data
                }
                data_to_write.append(distilled_ans)

            result = {
                'example_id': example_id,
                'text': data_to_write
            }
            final_data.append(result)

        with open(top_docs_path, 'w') as f:
            for line in final_data:
                json.dump(line, f)
                f.write('\n')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./ClaimDecomp/answers_subset.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--top_docs_path', default='./ClaimDecomp/top_docs_simpl_new.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)
