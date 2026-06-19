from typing import Any, Dict
import json

from src.file_manager import FileManager
from src.visualizer import Visualizer
from src.decoder import Decoder
from llm_sdk import Small_LLM_Model


class Builder:
    def __init__(self):
        self.file_manager = FileManager()
        self.model = Small_LLM_Model()
        self.visualizer = Visualizer()
        self.decoder = Decoder(
                        file_manager=self.file_manager,
                        model=self.model)

        self.visualizer.run(self.build)

    def build(self):
        results = []
        prompts = self.file_manager.get_prompts()

        for i, prompt in enumerate(prompts):
            self.visualizer.notify_new_prompt(prompt, i + 1, len(prompts))

            result = self.build_prompt(prompt)
            results.append(result)

            self.visualizer.notify_result(json.dumps(result, indent=4))

        self.file_manager.write_output(results)
        self.visualizer.notify_complete()

    def build_prompt(self, prompt: str) -> Dict[str, Any]:
        func_def = self.file_manager.get_functions_definition()
        name_prompt = self.get_name_prompt(func_def, prompt)
        function_name = self.generate_text(name_prompt)

        params_def = self.file_manager.get_function_parameters(function_name)
        parameters = {}

        for param_name, param_data in params_def.items():
            param_type = param_data["type"]

            param_prompt = self.get_param_prompt(function_name, param_name,
                                                 param_type, prompt, parameters)
            print(param_prompt)

            value = self.generate_text(param_prompt, param_type)
            parameters[param_name] = value


        return {"prompt": prompt,
                "name": function_name,
                "parameters": parameters}

    def generate_text(self, prompt: str, param_type: str | None = None) -> str:

        prompt_tokens_ids = list(self.model.encode(prompt)[0])
        result = ""

        while True:
            logits = self.model.get_logits_from_input_ids(prompt_tokens_ids)
            next_token_id = self.decoder.get_next_token_id(logits, param_type)

            prompt_tokens_ids.append(next_token_id)

            next_token = self.model.decode([next_token_id])
            result += next_token

            self.visualizer.notify_new_token(next_token)

            if self.decoder.is_complete(result, param_type):
                if param_type is None:
                    self.visualizer.notify_new_token("\n")
                break

        result = self.cast_parameter_value(result, param_type)
        return result

    def cast_parameter_value(self, value: str, param_type: str) -> Any:

        value = value.strip()
        if param_type in {"int", "integer"}:
            return int(value)

        elif param_type in {"float", "number"}:
            return float(value)

        elif param_type in {"bool", "boolean"}:
            return value.lower() in {"true", "yes", "1"}
        return value

    def get_name_prompt(self, func_def: str, prompt: str) -> str:

        return f"""Functions:
{func_def}

User:
{prompt}

Answer:
"""

    def get_param_prompt(self, function_name: str, param_name: str,
                         param_type: str, prompt: str,
                         parameters: dict[str, Any],) -> str:
        
        # Build context of already extracted parameters WITHOUT quotes.
        # If we use quotes here, the model will output quotes for the next param.
        params_context = ""
        if parameters:
            for k, v in parameters.items():
                params_context += f"{k}={v}, "
        
        # A hard, direct constraint placed immediately before the completion
        constraint = f"Output ONLY the raw {param_type} for {param_name}. No quotes, no commas, no parentheses. Stop immediately."
        
        return f"""User Request: {prompt}
{constraint}

{function_name}({params_context}{param_name}="""

