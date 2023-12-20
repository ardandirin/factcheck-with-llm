import argparse
from helpers import json_loader as JsonLoader
from helpers import general as General
from helpers import segmenter as Segmenter
import json
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
# from typing import List, Dict
from helpers.bm25 import BM25Retriever
from tqdm import tqdm


# unit2doc_index = {} # A dictionary that maps a text unit to its document index
# doc_index2doc = {} # A dictionary that maps a document index to its document

      
def main(corpus_path, original_test_path, top_docs_path):
    
    with open(corpus_path, 'r', encoding='utf8') as file, open(original_test_path, 'r', encoding='utf8') as test_data:
        docid = 0 # Unique identifier for each segment
        final_data = []
        for corpus_line, test_line in tqdm(zip(file, test_data)):
            test_data = json.loads(test_line)
            data = json.loads(corpus_line)
            print("New claim")
            for question, answers in data.items():
                 print("New question")
                 docid2doc = {} # A dictionary that maps a text unit to its document
                 unit2docid = {} # A dictionary that maps a text unit to its document id
                 segment_data = []  # A list of tuples containing a segment and its span
                 original_spans = {}  # Dictionary to store original spans
                 for answer in answers:
                    segment_dict = Segmenter.segment_answer(answer)
                    for segment, span in segment_dict.items():
                        # Store both the segment and its span
                        segment_data.append((segment, span))
                        docid2doc[docid] = answer
                        unit2docid[segment] = docid
                        original_spans[segment] = span
                        docid += 1
                    # Here we have segments for one answer!
                # Tokenize each segment for the BM25Retriever, this contains all the segments for one question, i.e 10 websites
                 tokenized_segments = [word_tokenize(segment) for segment, _ in segment_data]
                 bm25_retriever = BM25Retriever(tokenized_segments)

                 query = word_tokenize(question)
                 top_docs, scores = bm25_retriever.get_top_n_doc(query, 4)
                 
                 for doc, score in zip(top_docs, scores):
                    # print("Segment:", ' '.join(doc))
                    print("Score:", score)
                    print("---")
                    
                 overlap_count = 0
                   # Process for identifying and handling overlaps
                 print(len(top_docs))
                 top_docs_new = []
                 ids_to_remove = []
                 ids_to_merge = []
                 for i in range(len(top_docs)):
                    for j in range(i + 1, len(top_docs)):
                        print(i, j)
                        if Segmenter.are_segments_identical(top_docs[i], top_docs[j]):
                            print(f"Identical segments found: Document {i} and {j}")
                            # Handle the identical segments (e.g., remove one)
                            # top_docs.pop(j) # Remove the duplicate
                            ids_to_remove.append(j)
                        else:
                            overlap = Segmenter.sequence_overlap(top_docs[i], top_docs[j])
                            if overlap:
                                ids_to_merge.append((i, j))
                                
                 print(f"Ids to remove: {ids_to_remove}")
                 print(f"Ids to merge: {ids_to_merge}") 
                 
                 
                 # Step 1: Ensure No Overlap (add your logic here if needed)

                 # Step 2: Remove documents
                 top_docs_new = [doc for i, doc in enumerate(top_docs) if i not in ids_to_remove]

                # Step 3: Merge documents
                # Assuming ids_to_merge is a list of tuples (i, j), where i and j are indices to be merged
                 for i, j in ids_to_merge:
                    # Check if i and j are valid indices after removal
                    if 0 <= i < len(top_docs_new) and 0 <= j < len(top_docs_new):
                        merged_segment, merged_segment_id = Segmenter.merge_segments(i, j, top_docs_new, unit2docid, docid2doc)
                        # Update the list and references
                        top_docs_new[i] = word_tokenize(merged_segment)
                        unit2docid[merged_segment] = merged_segment_id
                        
                        # Update span for the merged segment
                        # span1 = original_spans[top_docs_new[i]]
                        # span2 = original_spans[top_docs_new[j]]
                        # merged_span = (min(span1[0], span2[0]), max(span1[1], span2[1]))
                        # original_spans[merged_segment] = merged_span
                        # Optionally remove the j-th element if it's a separate entity post-merge
                        top_docs_new.pop(j)
                        
                        
                 print(len(top_docs_new))

                 offset = 150  # Your desired offset

                 expanded_top_docs = []
                 for segment in top_docs_new:
                    # span = original_spans[segment]
                    segment = ' '.join(segment) # Turn the list of tokens back to a string
                    try:
                        doc_id = unit2docid[segment] # Here it may not find it
                    except:
                        doc_id = General.find_close_match(segment, unit2docid)
                        
                    original_text = docid2doc[doc_id]
                    # expanded_segment = Segmenter.expand_segment(segment, span, original_text, offset)
                    expanded_segment = Segmenter.expand_segment_with_offset(segment, original_text, offset)
                    expanded_top_docs.append(expanded_segment)
               
               
              
                    result = {
                            'example_id': test_data['example_id'],
                            # 'label': test_data['label'],
                            # 'claim': test_data['claim'],
                            # 'person': test_data['person'],
                            # 'venue': test_data['venue'],
                            # 'full_article': test_data['full_article'],
                            'question': question,
                            'top_docs': expanded_top_docs
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
    parser.add_argument('--top_docs_path', default='./ClaimDecomp/top_docs.jsonl', type=str)
    # parser.add_argument('--output_path', default='./ClaimDecomp/summaries.jsonl', type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.corpus_path, args.original_test_path, args.top_docs_path)