import argparse
from helpers import general as General
from helpers import segmenter as Segmenter
import json
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from helpers.bm25 import BM25Retriever
from tqdm import tqdm


def remove_identical_segments(segments):
    unique_segments = []
    remove_indices = set()

    for i, segment in enumerate(segments):
        if i not in remove_indices:
            unique_segments.append(segment)
            for j in range(i + 1, len(segments)):
                if segments[j] == segment:
                    remove_indices.add(j)
    
    return unique_segments


def main(corpus_path, original_test_path, top_docs_path):
    total_num_inital_top_docs = 0
    total_num_of_overlap_found = 0
    total_num_of_removed_segments = 0
    total_num_final_segments = 0
    
    with open(corpus_path, 'r', encoding='utf8') as corpus, open(original_test_path, 'r', encoding='utf8') as test_data, open(top_docs_path, 'w') as output_file:
        # iter_count = 0
        final_data = []
        for corpus_line, test_line in tqdm(zip(corpus, test_data)):
            print("New claim")
            data_to_write = []
            test_data = json.loads(test_line)
            corpus_data = json.loads(corpus_line)
            example_id = corpus_data['example_id']

            all_corpus = [] # Segment data for all questions, which the top docs will be retrieved from
            original_indices_map = {}
            for question, responses in corpus_data['questions'].items():
                # print("New question")
                segment_data = []  # A list of tuples containing a segment and its span
                for response in responses:
                    content = response['content']
                    url = response['url']
                    snippet = response['snippet']
                    title = response['title']
                    segment_dict = Segmenter.segment_answer(content)
                    for segment, span in segment_dict.items():
                        segment_data.append((segment, span, response))  # Include response metadata

                
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

            top_docs_data = []

            print(f"Number of top docs: {len(top_docs_tokenized)}")
            total_num_inital_top_docs += len(top_docs_tokenized)

           
            top_docs_unique, original_indices_map = Segmenter.remove_identical_segments(top_docs_tokenized, original_indices_map)

            print(f"Number of unique segments: {len(top_docs_unique)}")
            total_num_of_removed_segments += len(top_docs_tokenized) - len(top_docs_unique)

            ids_to_merge = Segmenter.find_overlapping_segments(top_docs_unique)
            top_docs_final, original_indices_map = Segmenter.merge_segments(top_docs_unique, ids_to_merge, original_indices_map)

            total_num_of_overlap_found += len(top_docs_unique) - len(top_docs_final)

            
            print(f"Number of final segments: {len(top_docs_final)}")
            total_num_final_segments += len(top_docs_final)


            # print(f"Total number of segments: {len(all_corpus)}")

        ## This part temporariyly commented out trying out something new.
            # Accessing the metadata for the filtered top documents
            for doc in top_docs_final:
                content = ' '.join(doc)
                doc_tuple = tuple(doc)
                if content == "No data":
                    print("Original metadata list is None")
                    top_docs_data.append({
                        'question': "No question",
                        'url': "No URL",
                        'snippet': "No snippet",
                        'title': "No title",
                        'content': "No content",
                    })
                    continue
                
                if doc_tuple in original_indices_map:
                    original_metadata_list = original_indices_map[doc_tuple]
                    top_docs_data.append({
                        'question': original_metadata_list['question'],
                        'url': original_metadata_list['url'],
                        'snippet': original_metadata_list['snippet'],
                        'title': original_metadata_list['title'],
                        'content': content,
                    })
            data_to_write.append({
                'example_id': example_id,
                'top_docs': top_docs_data
            })
            json.dump(data_to_write, output_file)
            output_file.write('\n')  # Ensure each entry is on a new line
            output_file.flush()
        
    print(f"Total number of initial top docs: {total_num_inital_top_docs}")
    print(f"Total number of removed segments: {total_num_of_removed_segments}")
    print(f"Total number of overlap found: {total_num_of_overlap_found}")
    print(f"Total number of final segments: {total_num_final_segments}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_path', default='./Data/3_Answers/answers_mixtral_icl.jsonl', type=str)
    parser.add_argument('--original_test_path', default='./ClaimDecomp/test.jsonl', type=str)
    parser.add_argument('--top_docs_path', default='./Data/4_TopDocs/top_docs_mixtral_icl.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)
