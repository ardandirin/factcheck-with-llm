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

        
