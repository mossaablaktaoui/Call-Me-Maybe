import json
from typing import Any, Dict

from src.decoder import Decoder
from src.file_manager import FileManager
from src.LLM_model import LLM_Model
from src.visualterm import Visualizer


class Builder:
    def __init__(self) -> None:
        self.file_manager = FileManager()
        self.model = LLM_Model(self.file_manager.model_name)
        self.visualizer = Visualizer()
        self.decoder = Decoder(
            file_manager=self.file_manager,
            model=self.model,
        )

        self.visualizer.run()
        self.build()

    def build(self) -> None:
        results: list[dict[str, Any]] = []
        prompts = self.file_manager.get_prompts()

        for index, prompt in enumerate(prompts):
            self.visualizer.notify_new_prompt(prompt, index + 1, len(prompts))

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
        parameters: dict[str, Any] = {}

        for param_name, param_data in params_def.items():
            param_type = param_data["type"]

            param_prompt = self.get_param_prompt(
                func_def,
                function_name,
                param_name,
                param_type,
                prompt,
                parameters,
            )

            value = self.generate_text(param_prompt, param_type)
            parameters[param_name] = value

        return {
            "prompt": prompt,
            "name": function_name,
            "parameters": parameters,
        }

    def generate_text(self, prompt: str, param_type: str | None = None) -> Any:
        prompt_tokens_ids = self.model.encode(prompt)
        result = ""

        loop = 0
        while True:
            logits = self.model.get_logits_from_input_ids(prompt_tokens_ids)
            next_token_id = self.decoder.get_next_token_id(
                logits,
                param_type,
                loop,
            )

            loop += 1

            prompt_tokens_ids.append(next_token_id)
            next_token = self.model.decode([next_token_id])
            result += next_token

            self.visualizer.notify_new_token(next_token)

            if self.decoder.is_complete(result, param_type):
                if param_type is None:
                    self.visualizer.notify_new_token("\n")
                break

        return self.cast_parameter_value(result, param_type)

    def cast_parameter_value(self, value: str,
                             param_type: str | None,) -> Any:
        value = value.strip()

        if param_type in {"int", "integer"}:
            return int(float(value))

        if param_type in {"float", "number"}:
            return float(value)

        if param_type in {"bool", "boolean"}:
            return value.lower() in {"true", "yes", "1"}

        if param_type in {"string", "str"}:
            return self.decoder.get_string_value(value)

        return value

    def get_name_prompt(self, func_def: str, prompt: str) -> str:
        return f"""Functions:
{func_def}

User:
{prompt}

Answer:
"""

    def get_param_prompt(self, func_def: str,
                         function_name: str, param_name: str,
                         param_type: str, prompt: str,
                         parameters: dict[str, Any],) -> str:
        params_context = ""
        if parameters:
            for key, value in parameters.items():
                params_context += (
                    f"\"{key}\": {json.dumps(value)},\n            "
                )

        if param_type in {"int", "integer", "float", "number"}:
            value_prefix = ""
        elif param_type in {"bool", "boolean"}:
            value_prefix = ""
        else:
            value_prefix = '"'

        return f"""Available functions:
{func_def}

User prompt: {prompt}

Extract the '{param_name}' parameter for the function \
'{function_name}' and complete the JSON:
{{
        \"prompt\": {json.dumps(prompt)},
        \"name\": \"{function_name}\",
        \"parameters\": {{
            {params_context}\"{param_name}\": {value_prefix}"""
