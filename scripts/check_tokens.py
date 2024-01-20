import tiktoken

import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
assert enc.decode(enc.encode("hello world")) == "hello world"

# To get the tokeniser corresponding to a specific model in the OpenAI API:
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

print(encoding.encode("tiktoken is great!"))

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    
    for message in messages:
        for key, value in message.items():
            for role in value:
                # print(type(role['content']))
                if isinstance(role['content'], list):
                    print("WARNING")
                if isinstance(role['content'], list):
                    role['content'] = ' '.join(role['content'])
                # print(type(role['content']))
                num_tokens += len(encoding.encode(role['content']))
            if key == "name":
                num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


# let's verify the function above matches the OpenAI API response

import json

with open('../ClaimDecomp/finetune_train.jsonl', 'r') as f:
    messages_train = [json.loads(line) for line in f]
    train_num = num_tokens_from_messages(messages_train)
    print("Number of train tokens:", train_num)

# with open('../ClaimDecomp/finetune_val.jsonl', 'r') as f:
#     messages_dev = [json.loads(line) for line in f]
#     dev_num = num_tokens_from_messages(messages_dev)
    # print("Number of dev tokens:", dev_num)
    
