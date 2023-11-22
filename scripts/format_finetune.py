import json

# Define a function to convert a line of JSON data to the format we want
def question_aggregator(json_line):

    question_set_1 = json_line["annotations"][0]["questions"]
    question_set_2 = json_line["annotations"][1]["questions"]

   # Combine the two sets of questions
    combined_questions = question_set_1 + question_set_2

    # Ensure each element is a string
    combined_questions = [str(question) for question in combined_questions]

    # Join the list into a string
    questions_string = ', '.join(combined_questions)
    return questions_string

# Open the input and output files
with open('../ClaimDecomp/dev.jsonl', 'r') as input_file, open('../ClaimDecomp/finetune_val.jsonl', 'w') as output_file:
    # Loop through each line in the input file to read necessary data
    # question_aggregator(json.loads(input_file.readline()))
    for line in input_file:
        # Load the JSON data from the line
        data = json.loads(line)
        
        # Extract the relevant fields
        claim = data['claim']
        person = data['person']
        venue = data['venue']
        questions = question_aggregator(data)
        prompt = person + " " + venue + '\n' + claim
        # Create a new dictionary with the relevant fields
        # new_data = {'text': text, 'label': label}
        out_line = {"messages": [{"role": "system", "content": "Assume you are a fact-checker, generate several yes or no questions to help me answer if this claim is true or false. You should ask questions regarding both implicit and explicit facets of the claim. DO ONLY OUTPUT THE QUESTIONS."}, {"role": "user", "content": prompt}, {"role": "assistant", "content": questions}]}
        
        # Write the new data to the output file
        output_file.write(json.dumps(out_line) + '\n')


# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}