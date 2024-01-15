# pure-llm-factcheking

In this approach we are relying solely on LLMs to do factchecking. Question Decomposition approach is still used as in the other approach however here the evidence is LLM's internal knowledge.

In order to avoid data leakage the prompt includes the date which the claim is made and requests the LLM to 