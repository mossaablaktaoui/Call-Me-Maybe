from typing import Any
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

    def build_prompt(self, prompt: str) -> dict[str, Any]:
        function_name = self.generate_function_name(prompt)
        parameters = self.generate_function_parameters(prompt, function_name)

        return {"prompt": prompt,
                "name": function_name,
                "parameters": parameters}

    def generate_function_name(self, prompt: str) -> str:

        func_def = self.file_manager.get_functions_definition()
        name_prompt = self.get_name_prompt(func_def, prompt)

        prompt_tokens_ids = list(self.model.encode(name_prompt)[0])

        result = ""

        while self.decoder.is_complete_function_name(result):
            logits = self.model.get_logits_from_input_ids(prompt_tokens_ids)
            masked_logits = self.decoder.mask_function_name_logits(logits,
                                                                   result)

            next_token_id = self.choose_next_token(masked_logits)
            prompt_tokens_ids.append(next_token_id)

            next_token = self.model.decode([next_token_id])
            result += next_token

            self.visualizer.notify_new_token(next_token)

        return result.strip()

    def generate_function_parameters(self, prompt: str,
                                     function_name: str,) -> dict[str, Any]:

        params_def = self.file_manager.get_function_parameters(function_name)

        parameters = {}

        for param_name, param_data in params_def.items():
            param_type = param_data["type"]

            value = self.generate_one_parameter_value(
                prompt=prompt,
                function_name=function_name,
                param_name=param_name,
                param_type=param_type,
            )

            parameters[param_name] = value

        return parameters

    def generate_one_parameter_value(self, prompt: str, function_name: str,
                                     param_name: str, param_type: str,) -> Any:

        param_prompt = self.get_param_prompt(
            function_name=function_name,
            param_name=param_name,
            param_type=param_type,
            prompt=prompt,
        )

        prompt_tokens_ids = list(self.model.encode(param_prompt)[0])
        result = ""

        while True:
            logits = self.model.get_logits_from_input_ids(prompt_tokens_ids)
            masked_logits = self.decoder.mask_parameter_value_logits(
                logits=logits,
                current_text=result,
                param_type=param_type,
            )

            next_token_id = self.choose_next_token(masked_logits)
            prompt_tokens_ids.append(next_token_id)

            next_token = self.model.decode([next_token_id])
            result += next_token

            self.visualizer.notify_new_token(next_token)

            if self.decoder.value_is_finished(result):
                clean_value = self.decoder.clean_end_token(result)
                return self.cast_parameter_value(clean_value, param_type)

    def choose_next_token(self, logits: list[float]) -> int:
        if max(logits) == float("-inf"):
            raise RuntimeError("No valid token available after masking.")

        return logits.index(max(logits))

    def cast_parameter_value(self, value: str, param_type: str) -> Any:

        value = value.strip()

        if param_type in {"int", "integer"}:
            return int(value)

        if param_type in {"float", "number"}:
            return float(value)

        if param_type in {"bool", "boolean"}:
            return value.lower() in {"true", "yes", "1"}

        return value

    def get_name_prompt(self, func_def: str, prompt: str) -> str:

        return f"""Functions:
{func_def}

Choose function.
Output function_name only.

User:
{prompt}

Answer:
"""

    def get_param_prompt(self, function_name: str, param_name: str,
                         param_type: str, prompt: str,) -> str:

        return f"""Function:
{function_name}

Extract:
{param_name}:{param_type}

Output value only. then newline.

User:
{prompt}

Value:
"""
