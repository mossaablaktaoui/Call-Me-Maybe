import json
from typing import Any

from numpy.strings import startswith


class Validator:
    def __init__(self, funcs_path):
        self.funcs_path = funcs_path
        self.funcs_defs = self.load_functions()

    def load_functions(self):
        try:
            with open(self.funcs_path, "r") as file:
                return json.load(file)

        except FileNotFoundError:
            raise FileNotFoundError("Missing functions file.")

        except json.JSONDecodeError:
            raise ValueError("Functions file is not valid JSON.")

    def validate_model_reply(self, json_string: str) -> tuple[bool, str]:
        try:
            model_reply = json.loads(json_string)

        except json.JSONDecodeError:
            return False, "Invalid JSON."

        if not isinstance(model_reply, dict):
            return False, "Answer must be a JSON object."

        if set(model_reply.keys()) != {"name", "parameters"}:
            return False, 'Answer must contain only "name" and "parameters".'

        func_name = model_reply["name"]
        parameters = model_reply["parameters"]

        if not isinstance(func_name, str):
            return False, '"name" must be a string.'

        if not isinstance(parameters, dict):
            return False, '"parameters" must be an object.'

        funcs_by_name = {func["name"]: func for func in self.funcs_defs}

        if func_name not in funcs_by_name:
            return False, f'Function "{func_name}" is not allowed.'

        expected_params = set(funcs_by_name[func_name]["parameters"].keys())
        given_params = set(parameters.keys())

        if given_params != expected_params:
            return False, (
                f'Wrong parameters for "{func_name}". '
                f"Expected: {sorted(expected_params)}. "
                f"Got: {sorted(given_params)}."
            )

        return True, "OK"

    def json_is_finished(self, text: str) -> bool:
        depth = 0
        in_string = False
        escaped = False

        for c in text:
            if escaped:
                escaped = False
                continue

            if c == "\\":
                escaped = True
                continue

            if c == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth < 0:
                    return False
       
        return depth == 0 and not in_string and text.strip().startswith("{")

    def is_valid_function(result) -> bool:
        functions_names = [func["name"] for func in self.funcs_path]
        funcs_start_with = [func for func in functions_names
                            if func.startswith(result)]
        if len(funcs_start_with) == 0:
			raise RuntimeError("The model is hallucinating")
        if (result in functions_names and len(funcs_start_with) == 1:
            return True
        return False
