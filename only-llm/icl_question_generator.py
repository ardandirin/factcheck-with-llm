'''
IN-CONTEXT-LEARNING QUESTION GENERATOR
Given the ClaimDecomp Test set's questions and the prompt to provide few-shot-learning
Returns the generated subquestions about the claim. 
'''


'''Claim: Viral image stated on June 8, 2020 in post on Facebook: Cops in Norway: require 3 years of training, 4 people killed since 2002. Cops in Finland: require 2 years of training, 7 people killed since 2000. Cops in Iceland: require 2 years of training, 1 person killed since ever. Cops in the U.S.: require 21 weeks of training, 8,000+ people killed since 2001.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Quesons:
Does Norway require 3 years of training for cops?
Have Norwegian cops killed 4 people since the early 2000's?
Does Finland require only 2 years of training for police?
Have Finnish police killed 7 people since 2000?
Does Iceland only require 2 years of training for cops?
Have Iceland cops only killed 1 person ever?
Does the U.S. require only 21 weeks of training for cops?
Have U.S. cops killed more than 8,000 people since 2001?
Do experts associate only training me with police-related shoong fatalies?

Claim: Barry DuVal stated on September 25, 2015 in an interview: We're the only major oil-producing naon in the world with a self-imposed ban on exporng our crude oil to other naons.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:
Is the U.S. the only major oil-producing naon to ban exports of crude oil?
Is the self-imposed ban on crude oil export of U.S a complete ban?

Claim: William Barr stated on September 2, 2020 in a CNN interview: We indicted someone in Texas, 1,700 ballots collected from people who could vote, he made them out and voted for the person he wanted to.

Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:
Were 1700 mail-in ballots invesgated for fraud in Texas during the 2020 elecon?
Did the Justice Department indict someone in Texas for voter fraud?
Did widespread mail-in order fraud happen in Texas during the 2020 elecon?
Did voter disenfranchisement happen in Texas during the 2020 elecon?

Claim: {}
Suppose you are a fact-checker, generate several yes or no quesons to help me answer if this claim is true or false.

Questions:'''



def main():
    input_claim = ""
    prompt = f"Claim: {input_claim}\nSuppose you are a fact-checker, generate several yes or no questions to help me answer if this claim is true or false.\nQuestions:"