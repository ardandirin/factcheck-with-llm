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
            data = json.loads(corpus_line)
            print("New claim")
            for question, answers in data.items():
                 print("New question")
                 segment_data = []  # A list of tuples containing a segment and its span
                 for answer in answers:
                    segment_dict = Segmenter.segment_answer(answer)
                    for segment, span in segment_dict.items():
                        segment_data.append((segment, span))
                        
                # Tokenize each segment for the BM25Retriever, this contains all the segments for one question, i.e 10 websites
                 tokenized_segments = [word_tokenize(segment) for segment, _ in segment_data]
                 bm25_retriever = BM25Retriever(tokenized_segments)

                 query = word_tokenize(question)
                 top_docs, scores = bm25_retriever.get_top_n_doc(query, 4)
                 
                 for doc, score in zip(top_docs, scores):
                    # print("Segment:", ' '.join(doc))
                    print("Score:", score)
                    print("---")
                
                 distilled_ans = {
                    'question': question,
                    'top_docs': [" ".join(tokens) for tokens in top_docs]
                 }
                 data_to_write.append(distilled_ans)
              
            result = {
                'example_id': test_data['example_id'],
                'text': data_to_write
                }
            final_data.append(result)
                     
        with open(top_docs_path, 'w') as f:
            for line in final_data:
                json.dump(line, f)
                f.write('\n')
            

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./ClaimDecomp/deneme.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--top_docs_path', default='./ClaimDecomp/top_docs_simple.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)