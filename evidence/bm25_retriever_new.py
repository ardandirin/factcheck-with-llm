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
            # print(i, j)
            if Segmenter.are_segments_identical(top_docs_tokenized[i], top_docs_tokenized[j]):
                # print(f"Identical segments found: Document {i} and {j}")
                ids_to_remove.append(j)
            else:
                overlap = Segmenter.sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
                if overlap:
                    # print(f"Overlap found between document {i} and {j}: '{overlap}'")
                    ids_to_merge.append((i, j))
    return ids_to_remove, ids_to_merge


def merge_remove_segments(top_docs_tokenized, ids_to_remove, ids_to_merge, original_indices_map):
    merged_segments = []
    merged_segments_map = {}
    merged_indices = set()
    new_original_indices_map = {}
    index_mapping = {}  # Maps old indices to new indices

    # Handle merging
    new_index = 0
    for i, j in ids_to_merge:
        if i in merged_indices or j in merged_indices:
            continue

        overlap = Segmenter.sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
        if overlap:
            print(f"Overlap found between document {i} and {j}")
            merged_segment = Segmenter.merge_segments_new(top_docs_tokenized[i], top_docs_tokenized[j], overlap)
            merged_segments.append(merged_segment)
            merged_indices.update([i, j])
            merged_segments_map[new_index] = [i, j]

            # Update index mapping
            index_mapping[i] = new_index
            index_mapping[j] = new_index
            new_index += 1
        else:
            print("Error: Overlap not found in segments")

    # Handle unmerged segments
    for index, segment in enumerate(top_docs_tokenized):
        if index not in merged_indices:
            merged_segments.append(segment)
            index_mapping[index] = new_index
            new_index += 1

    # Update ids_to_remove based on index_mapping
    updated_ids_to_remove = set()
    for old_index in ids_to_remove:
        if old_index in index_mapping:
            updated_ids_to_remove.add(index_mapping[old_index])

    # Filter out the segments to remove
    filtered_top_docs_tokenized = [segment for i, segment in enumerate(merged_segments) if i not in updated_ids_to_remove]
    
    # Get the original metadata for the filtered segments in this for loop
    for i, merged_segment in enumerate(merged_segments):
        if i in updated_ids_to_remove:
            continue

        # Check if this segment is a result of a merge
        if i in merged_segments_map:
            original_indices = merged_segments_map[i]
            merged_metadata = []

            for original_index in original_indices:
                original_segment = top_docs_tokenized[original_index]
                original_segment_tuple = tuple(original_segment)
                if original_segment_tuple in original_indices_map:
                    # Aggregate metadata from all original segments
                    merged_metadata.append(original_indices_map[original_segment_tuple])

            # Store the aggregated metadata for the merged segment
            new_original_indices_map[tuple(merged_segment)] = merged_metadata
        else:
            # For segments not resulting from a merge, just copy the original metadata
            original_segment_tuple = tuple(merged_segment)
            if original_segment_tuple in original_indices_map:
                new_original_indices_map[original_segment_tuple] = [original_indices_map[original_segment_tuple]]

    

    return filtered_top_docs_tokenized, new_original_indices_map
    
    # print(f"Filtered top docs: {len(filtered_top_docs_tokenized)}")




def main(corpus_path, original_test_path, top_docs_path):
    
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(original_test_path, 'r', encoding='utf8') as test_data:
        # iter_count = 0
        final_data = []
        for corpus_line, test_line in tqdm(zip(corpus, test_data)):

            data_to_write = []
            test_data = json.loads(test_line)
            corpus_data = json.loads(corpus_line)
            example_id = corpus_data['example_id']

            all_corpus = [] # Segment data for all questions, which the top docs will be retrieved from
            original_indices_map = {}
            for question, responses in corpus_data['questions'].items():
                print("New question")
                segment_data = []  # A list of tuples containing a segment and its span
                for response in responses:
                    content = response['content']
                    url = response['url']
                    snippet = response['snippet']
                    title = response['title']
                    segment_dict = Segmenter.segment_answer(content)
                    for segment, span in segment_dict.items():
                        segment_data.append((segment, span, response))  # Include response metadata

                # Tokenize each segment for the BM25Retriever
                # tokenized_segments = [word_tokenize(segment) for segment, _, _ in segment_data]
                
                # Tokenize each segment for the BM25Retriever and keep track of original indices
                tokenized_segments = []
                
                for original_idx, (segment, _, _) in enumerate(segment_data):
                    tokenized_segment = word_tokenize(segment)
                    tokenized_segments.append(tokenized_segment)

                    original_indices_map[tuple(tokenized_segment)] = {'index': original_idx, 'question': question, 'url': url, 'snippet': snippet, 'title': title}

                # Check if tokenized_segments is empty and add placeholder
                if not tokenized_segments:
                    print("Tokenized segments is empty")
                    tokenized_segments.append(word_tokenize("No data"))

                all_corpus.extend(tokenized_segments)

            bm25_retriever = BM25Retriever(all_corpus)

            claim = General.get_context(test_data) # With person, venue and claim
            query = word_tokenize(claim)
            top_docs_tokenized, scores = bm25_retriever.get_top_n_doc(query, 4)

            # # Iterate through the filtered top documents
            # for doc in top_docs_tokenized:
            #     # Convert the tokenized document back to tuple form
            #     doc_tuple = tuple(doc)

            #     # Retrieve original metadata from the map using the tuple as a key
            #     if doc_tuple in original_indices_map:
            #         original_metadata = original_indices_map[doc_tuple]

            #         # Access the metadata fields
            #         original_index = original_metadata['index']
            #         original_question = original_metadata['question']
            #         original_url = original_metadata['url']
            #         original_snippet = original_metadata['snippet']
            #         original_title = original_metadata['title']
            #     else:
            #         print("!!!!Error: Original metadata not found")

            top_docs_data = []
            ids_to_remove, ids_to_merge = finds_ids(top_docs_tokenized)

            print(f"Ids to remove: {ids_to_remove}")
            print(f"Ids to merge: {ids_to_merge}")

            print(f"Total number of segments: {len(all_corpus)}")

            filtered_top_docs_tokenized, new_original_indices_map = merge_remove_segments(top_docs_tokenized, ids_to_remove, ids_to_merge, original_indices_map)

            # Accessing the metadata for the filtered top documents
            for doc in filtered_top_docs_tokenized:
                content = ' '.join(doc)
                doc_tuple = tuple(doc)
                if doc_tuple in new_original_indices_map:
                    original_metadata_list = new_original_indices_map[doc_tuple]
                   # Use a set to track unique metadata combinations
                    unique_metadata = set()

                    for original_metadata in original_metadata_list:
                        # Create a tuple of metadata values to check for uniqueness
                        metadata_tuple = (
                            original_metadata['question'],
                            original_metadata['url'],
                            original_metadata['snippet'],
                            original_metadata['title']
                        )

                    # Add to top_docs_data only if this combination hasn't been added before
                    if metadata_tuple not in unique_metadata:
                        unique_metadata.add(metadata_tuple)
                        top_docs_data.append({
                            'question': original_metadata['question'],
                            'url': original_metadata['url'],
                            'snippet': original_metadata['snippet'],
                            'title': original_metadata['title'],
                            'content': content,
                        })
            data_to_write.append({
                'example_id': example_id,
                'top_docs': top_docs_data
            })
            final_data.append(data_to_write)

        with open(top_docs_path, 'w') as f:
            for line in final_data:
                json.dump(line, f)
                f.write('\n')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./ClaimDecomp/answers.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--top_docs_path', default='./ClaimDecomp/top_docs.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)
