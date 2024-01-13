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


def remove_identical_segments(top_docs_tokenized, original_indices_map):
    """ Remove identical segments and return a list of unique segments along with updated original_indices_map. """
    unique_segments = []
    remove_indices = set()
    updated_original_indices_map = {}

    for i, segment in enumerate(top_docs_tokenized):
        if i in remove_indices:
            continue  # Skip segments that are marked for removal

        segment_tuple = tuple(segment)
        unique_segments.append(segment)
        updated_original_indices_map[segment_tuple] = original_indices_map.get(segment_tuple, [])

        # Check for identical segments to mark them for removal
        for j in range(i + 1, len(top_docs_tokenized)):
            if are_segments_identical(segment, top_docs_tokenized[j]):
                remove_indices.add(j)

    return unique_segments, updated_original_indices_map


def find_overlapping_segments(top_docs_tokenized):
    """ Find indices of segments that have an overlap. """
    ids_to_merge = []
    for i in range(len(top_docs_tokenized)):
        for j in range(i + 1, len(top_docs_tokenized)):
            overlap = sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
            if overlap:
                ids_to_merge.append((i, j))
    return ids_to_merge


def merge_segments(top_docs_tokenized, ids_to_merge, original_indices_map):
    merged_segments = []
    merged_indices = set()
    new_original_indices_map = {}

    for i, j in ids_to_merge:
        if i in merged_indices or j in merged_indices:
            continue

        overlap = sequence_overlap(top_docs_tokenized[i], top_docs_tokenized[j])
        if overlap:
            print(f"Overlap found between document {i} and {j}")
            merged_segment = merge_segments_new(top_docs_tokenized[i], top_docs_tokenized[j], overlap)
            merged_segments.append(merged_segment)
            merged_indices.update([i, j])

            # Initialize a dictionary to aggregate metadata from both original segments
            merged_metadata = {}

            for original_index in [i, j]:
                original_segment_tuple = tuple(top_docs_tokenized[original_index])
                if original_segment_tuple in original_indices_map:
                    segment_metadata = original_indices_map[original_segment_tuple]
                    if isinstance(segment_metadata, dict):
                        # Merge dictionaries
                        merged_metadata.update(segment_metadata)
                    else:
                        print(f"Warning: Metadata for segment {original_segment_tuple} is not a dictionary. It's a {type(segment_metadata)}.")
                else:
                    print(f"Metadata for segment {original_segment_tuple} not found in original_indices_map.")

            new_original_indices_map[tuple(merged_segment)] = merged_metadata
        else:
            print("Error: Overlap not found in segments")

    # Include unmerged segments and their metadata
    for index, segment in enumerate(top_docs_tokenized):
        if index not in merged_indices:
            merged_segments.append(segment)
            original_segment_tuple = tuple(segment)
            if original_segment_tuple in original_indices_map:
                new_original_indices_map[original_segment_tuple] = original_indices_map[original_segment_tuple]

    return merged_segments, new_original_indices_map