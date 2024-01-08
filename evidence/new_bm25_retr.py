import argparse
from helpers import general as General
from helpers import segmenter as Segmenter
import json
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from helpers.bm25 import BM25Retriever
from tqdm import tqdm

import nltk
nltk.download('punkt')


def finds_ids(top_docs_tokenized):
    ''' Finds the ids of the segments that are identical or have an overlap. '''
    ids_to_remove = []
    ids_to_merge = []
    for i in range(len(top_docs_tokenized)):
        for j in range(i + 1, len(top_docs_tokenized)):
            print(i, j)
            if Segmenter.are_segments_identical(top_docs_tokenized[i], top_docs_tokenized[j]):
                print(f"Identical segments found: Document {i} and {j}")
                ids_to_remove.append(j)
            else:
                overlap = Segmenter.sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
                if overlap:
                    print(f"Overlap found between document {i} and {j}: '{overlap}'")
                    ids_to_merge.append((i, j))
    return ids_to_remove, ids_to_merge



def main(corpus_path, original_test_path, top_docs_path):
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(original_test_path, 'r', encoding='utf8') as test_data:
        final_data = []
        for corpus_line, test_line in tqdm(zip(corpus, test_data)):
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
                # tokenized_segments = [word_tokenize(segment) for segment, _, _ in segment_data]
                
                # Tokenize each segment for the BM25Retriever and keep track of original indices
                tokenized_segments = []
                original_indices_map = {}
                for original_idx, (segment, _, _) in enumerate(segment_data):
                    tokenized_segment = word_tokenize(segment)
                    tokenized_segments.append(tokenized_segment)
                    original_indices_map[tuple(tokenized_segment)] = original_idx
                bm25_retriever = BM25Retriever(tokenized_segments)

                query = word_tokenize(question)
                top_docs_tokenized, scores = bm25_retriever.get_top_n_doc(query, 4)
                
                top_docs_data = []
                ids_to_remove, ids_to_merge = finds_ids(top_docs_tokenized)
                                
                print(f"Ids to remove: {ids_to_remove}")
                print(f"Ids to merge: {ids_to_merge}") 
                

                # Merging and removing segments
                merged_segments = []
                merged_segments_map = {}
                merged_indices = set()
                for i, j in ids_to_merge:
                    if i in merged_indices or j in merged_indices:
                        continue

                    overlap = Segmenter.sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
                    if overlap:
                        print(f"Overlap found between document {i} and {j}")
                        merged_segment = Segmenter.merge_segments_new(top_docs_tokenized[i], top_docs_tokenized[j], overlap)
                        # print(f"Merged segment: {merged_segment}")
                        merged_segments.append(merged_segment)
                        merged_indices.update([i, j])
                        merged_segments_map[len(merged_segments) - 1] = [i, j]
                    else:
                        print("Error: Overlap not found in segments")

                for index, segment in enumerate(top_docs_tokenized):
                    if index not in merged_indices:
                        merged_segments.append(segment)

                filtered_top_docs_tokenized = [segment for i, segment in enumerate(merged_segments) if i not in ids_to_remove]
                
                print(f"Filtered top docs: {len(filtered_top_docs_tokenized)}")

                # Processing segments with their metadata
                for idx, (filtered_top_doc_token, score) in enumerate(zip(filtered_top_docs_tokenized, scores)):
                    merged_metadata = None
                    if idx in merged_segments_map:
                        original_indices = merged_segments_map[idx]
                        metadata_list = []
                        
                        for original_idx in original_indices:
                            corresponding_index = next((i for i, (segment, _, _) in enumerate(segment_data) if word_tokenize(segment) in filtered_top_doc_token), None)
                            if corresponding_index is not None:
                                _, _, original_metadata = segment_data[corresponding_index]
                                metadata_list.append(original_metadata)
                            # Process or store this metadata as needed
                            
                        else:
                            # Handle the case where metadata differs
                            # This could be storing both, logging a warning, etc.
                            print("Warning: Metadata differs for merged segments")
                            merged_metadata = {"multiple_sources": metadata_list}
                    
                    for segment, span, response_metadata in segment_data:
                        if set(word_tokenize(segment)).issubset(filtered_top_doc_token):
                            print("Found segment: inside")
                            top_doc = {
                                'url': response_metadata['url'],
                                'snippet': response_metadata['snippet'],
                                'title': response_metadata['title'],
                                'segment': segment,
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
                'data': data_to_write
            }
            final_data.append(result)

        with open(top_docs_path, 'w') as f:
            for line in final_data:
                json.dump(line, f)
                f.write('\n')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./ClaimDecomp/answers2.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--top_docs_path', default='./ClaimDecomp/top_docs_simpl2.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)
