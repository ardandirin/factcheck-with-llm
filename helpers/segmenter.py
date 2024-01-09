from nltk.tokenize import word_tokenize
from helpers.general import clean_text, find_close_match

def segment_answer(answer: str, segment_size: int = 1500) -> dict[str: tuple[int, int]]:
    words = word_tokenize(answer)
    segments = {}
    
    stride = segment_size // 2
    for i in range(0, len(words), stride):
        segment = ' '.join(words[i:i + segment_size])
        # Calculate the span as character indices in the original text
        start_index = answer.find(segment)
        end_index = start_index + len(segment) - 1
        segments[segment] = (start_index, end_index)

    return segments

def are_segments_identical(seg1: list, seg2: list) -> bool:
    return seg1 == seg2



def sequence_overlap(segment1, segment2, window_size=100):
    """
    Check if there is a significant overlap between two segments.
    :param segment1: First segment (list of words).
    :param segment2: Second segment (list of words).
    :param window_size: Size of the window to check for overlap.
    :return: Boolean indicating if there is an ordered overlap.
    """
    for i in range(len(segment1) - window_size + 1):
        window = segment1[i:i + window_size]
        window_str = " ".join(window)
        if window_str in " ".join(segment2):
            return window_str
    return None


# def merge_segments(seg1, seg2, original_document):
#     """
#     Merge two overlapping segments with reference to the original document.
#     Each segment is a tuple: (start_index, end_index, text).
#     Original_document is the complete text of the original document. i.e. Answer, should be the same.
#     """
#     # Determine the new start and end points
#     # new_start = min(seg1[0], seg2[0])
#     # new_end = max(seg1[1], seg2[1])

#     # Find the start and end indices of the segments in the original document
#     start_index = original_document.find(seg1[0])
#     end_index = original_document.find(seg2[::])

#     # Extract the merged text from the original document for accuracy
#     new_text = original_document[start_index:end_index]

#     return new_text


def expand_segment(segment, span, original_text, offset):
    start_index, end_index = span
    # Adjust the start and end indices by the offset
    start_index = max(0, start_index - offset)
    end_index = min(len(original_text), end_index + offset)
    # Extract and return the expanded segment
    return original_text[start_index:end_index]
def expand_segment_with_offset(segment: str, original_text: str, offset: int) -> str:
    # Tokenize the original text
    tokenized_original = word_tokenize(original_text)
    tokenized_segment = word_tokenize(segment)

    # Define the range for the first and last tokens to match
    first_tokens_to_match = 10
    last_tokens_to_match = 10

    # Adjust the range if the segment is shorter
    if len(tokenized_segment) < first_tokens_to_match + last_tokens_to_match:
        first_tokens_to_match = last_tokens_to_match = len(tokenized_segment) // 2

    # Find the start and end token index of the segment in the original text
    for i in range(len(tokenized_original)):
        # Check for match with the first and last tokens of the segment
        if (tokenized_original[i:i + first_tokens_to_match] == tokenized_segment[:first_tokens_to_match] and 
            tokenized_original[i + len(tokenized_segment) - last_tokens_to_match:i + len(tokenized_segment)] == tokenized_segment[-last_tokens_to_match:]):
            print("Segment found as tokens")
            start_token_index = i
            break
    else:
        # Segment not found as tokens, return original segment
        print("Segment not found as tokens, returning original segment")
        return segment

    # Calculate the start and end token indices with offset
    start_token_index = max(0, start_token_index - offset)
    end_token_index = min(len(tokenized_original), start_token_index + len(tokenized_segment) + offset)

    # Join the tokens back to a string
    expanded_segment = ' '.join(tokenized_original[start_token_index:end_token_index])

    return expanded_segment





def merge_segments(i, j, top_docs, unit2docid, docid2doc):
    print(f"Document1 length is {len(top_docs[i])}")
    print(f"Document2 length is {len(top_docs[j])}")
    # print(f"Ordered overlap found between document {i} and {j}: '{overlap}'")
    # overlap_count += 1
    # Handle the overlap (e.g., merge segments)
    doc1 = ' '.join(top_docs[i])
    doc2 = ' '.join(top_docs[j])
    id1 = None
    id2 = None
    try:
        id1 = unit2docid[doc1]
    except:
        id1 = find_close_match(doc1, unit2docid)
    # try:
    #     id2 = unit2docid[doc2]
    # except:
    #     id2 = find_close_match(doc2, unit2docid)
        
    # id1 = find_close_match(doc1, unit2docid)
    # id2 = find_close_match(doc2, unit2docid)
    
    answer = docid2doc[id1]
    # print(len(answer))

    merged_segment = doc1 + " " + doc2
    merged_segment_id = id1
    
    return merged_segment, merged_segment_id
    # print(f"Merged segment: {merged_segment}")

    # Update the top_docs list
    # top_docs[i] = merged_segment
    # top_docs.pop(j) # This is the problem
















def find_overlap_start_index(segment, overlap):
        combined_text = ""
        for i, token in enumerate(segment):
            combined_text += token + " "
            combined_trimmed = combined_text.strip()  # Trim any leading/trailing spaces for accurate comparison
            if combined_trimmed == overlap:
                # print(f"Overlap found at index {i}")
                return i + 1  # Return the exclusive end index of the overlap
            elif combined_trimmed.endswith(overlap):
                return i + 1  # Handle cases where overlap is at the end
           
        return None


def merge_segments_new(seg1, seg2, overlap):
    # Find the start index of the overlap in seg1 and seg2
        start_idx_seg1 = find_overlap_start_index(seg1, overlap)
        start_idx_seg2 = find_overlap_start_index(seg2, overlap)

        if start_idx_seg1 is None or start_idx_seg2 is None:
            # print("Error: Overlap not found in segments")
            return seg1  # Fallback

        # Determine the order of the segments
        if start_idx_seg2 > start_idx_seg1:
            # seg1 comes after seg2, so take the beginning of seg2 and append the end of seg1
            merged_segment = seg2[:start_idx_seg2 - len(overlap.split())] + seg1[start_idx_seg1:]
        else:
            # seg1 comes before seg2
            merged_segment = seg1[:start_idx_seg1 - len(overlap.split())] + seg2[start_idx_seg2:]

        return merged_segment

