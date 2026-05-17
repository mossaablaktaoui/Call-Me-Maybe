from llm_sdk import Small_LLM_Model
import json
from typing import Dict, List


# Extract prompts from function_calling_tests.json
def get_prompts() -> List:
    with open("data/input/function_calling_tests.json", "r") as file:
        data = json.load(file)

    prompts = []

    for prompt in data:
        prompts.append(prompt.get("prompt"))

    return prompts
# Get all possible tokens of output file
def get_possible_tokens(model):
    tokens_ids = []
    encode_str = 'name parameters prompt {} " : , '

    with open("data/input/functions_definition.json", "r") as file:
        functions = json.load(file)

    for func in functions:   
        encode_str += func['name']
        for param in func['parameters'].keys():
            encode_str += param

    with open("data/input/function_calling_tests.json", "r") as file:
        prompts = file.read()

    encode_str += prompts

    tokens_ids += list(set(model.encode(encode_str)[0]))

    return tokens_ids
        

    
# Extract all available functions from functions_definition.json then reformat them
def compress_funcs_def():
    with open("data/input/functions_definition.json", "r") as file:
        functions = json.load(file)

    compressed = []

    for func in functions:
        params = []

        for param_name, param_data in func['parameters'].items():
            params.append(f"{param_name}:{param_data['type']}")

        compressed.append(
                f"{func['name']}({', '.join(params)})"
                )
    return "[" + ", \n".join(compressed) + "]"

def main():
model = Small_LLM_Model()
    func_def = compress_funcs_def()

    base_prompt = f"""
        FUNCTIONS:
            {func_def}

        JSON OUTPUT:
            {{"prompt":"","name":"","parameters":{{}}}}

        USER:
                """
    user_prompt = "What is the sum of 2 + 3?"

    base_prompt_tokens_ids = list(model.encode(base_prompt)[0])
    user_prompt_tokens_ids = list(model.encode(user_prompt)[0])

    prompt_tokens_ids = base_prompt_tokens_ids + user_prompt_tokens_ids

    res = "{\n"
    stack = ["{"]
    possible_tokens = set(get_possible_tokens(model))

    while True:
        logits = model.get_logits_from_input_ids(prompt_tokens_ids)
        for token_id in range(len(logits)):
            if token_id not in possible_tokens:
                logits[token_id] = float('-inf')
        next_token_id = logits.index(max(logits))
        prompt_tokens_ids.append(next_token_id)
        next_token = model.decode([next_token_id])
        
        if "{" in next_token:
            stack.append("{")
        if "}" in  next_token:
            if stack:
                stack.pop()

        res += next_token
        print("--------------------------------\n", res)
        if len(stack) == 0 and res.strip().startswith("{"):
            break


if __name__ == "__main__":
    """
    model = Small_LLM_Model()
    user_prompt = "What is the sum of 2 + 3?"
    user_prompt_tokens_ids = list(model.encode(user_prompt)[0])

    logits = model.get_logits_from_input_ids(user_prompt_tokens_ids)
    print(type(logits[0]))
    get_possible_tokens(model)
    """
    main()
