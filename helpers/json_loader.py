import json


def json_loader(data_path):
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
        
