import json

with open('../ClaimDecomp/test.jsonl', 'r') as input_file, open('../ClaimDecomp/test_final.jsonl', 'w') as output_file:
    # Loop through each line in the input file to read necessary data
    # question_aggregator(json.loads(input_file.readline()))
    for line in input_file:
        # Load the JSON data from the line
        data = json.loads(line)
        
        # Extract the relevant fields
        claim = data['claim']
        person = data['person']
        venue = data['venue']