import json

def load_jsonl(file_path):
    """
    Load a JSON Lines file and return a list of dictionaries.

    :param file_path: The path to the .jsonl file to read.
    :return: A list of dictionaries containing the data from the .jsonl file.
    """
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            data.append(json_obj)
    return data


def merge_questions(file_path1, file_path2):
    """
    Merge two JSONL files based on the 'example_id' key.
    Assumes 'questions' in file1 is a list and 'questions' in file2 is nested within 'annotations'.
    
    :param file_path1: The path to the file containing generated subquestions.
    :param file_path2: The path to the file with the annotated subquestions.
    :return: A dictionary with 'example_id' as keys and combined data as values.
    """
    # Load the first and second file into a dictionary
    generated = {item['example_id']: item for item in load_jsonl(file_path1)}
    annotated = {item['example_id']: item for item in load_jsonl(file_path2)}
    
    # Combine the data
    combined_data = {}
    for example_id in generated:
        if example_id in annotated:
            # Extract questions from annotations in the second file
            questions_file2 = [question for annotation in annotated[example_id]['annotations'] for question in annotation['questions']]
            combined_data[example_id] = {
                'questions_generated': generated[example_id].get('questions', []),
                'questions_annotated': questions_file2
            }
        else:
            print(f"Warning: No match for example_id {example_id} found in second file.")
    
    return combined_data
