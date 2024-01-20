'''
IN-CONTEXT-LEARNING QUESTION GENERATOR
Given the ClaimDecomp Test set's questions and the prompt to provide few-shot-learning
Returns the generated subquestions about the claim. 
'''






def main():
    input_claim = ""
    prompt = f"Claim: {input_claim}\nSuppose you are a fact-checker, generate several yes or no questions to help me answer if this claim is true or false.\nQuestions:"