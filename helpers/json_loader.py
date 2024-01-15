import json


def json_loader(data_path):
    '''Given a path to a jsonl file, returns a list of json objects'''
    print("json_loader called")
    data = []
    with open(data_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            data.append(json_obj)
    if data is not None:
        return data
    else:
        return None
    

    
def list_returner(json_obj):
    '''Given a list data, returns a list of subquestions where each object within the list is a subquestion string'''
    subquestions = json_obj['subquestions'][0].split(', ')
    # print(subquestions)
    return subquestions

        
def load_subquestions(subquestions_obj, example_id):
    '''Given python object of subquestions, returns a list of subquestions for the given claim (id)'''
    print("load_subquestions called")
    for entry in subquestions_obj:
        if entry['example_id'] == example_id:
            print("Subquestions found")
            return entry['subquestions'][0].split(', ')
    print("No such id found")
    return None 