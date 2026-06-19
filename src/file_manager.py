from src.models import PromptInput, FunctionDefinition
from pydantic import ValidationError
from pathlib import Path
import argparse
import json


class FileManager():
    def __init__(self):
        arguments = self.parse_argument()
        self.functions_definition = arguments[0]
        self.input = arguments[1]
        self.output = arguments[2]
        self.funcs_def = self.load_functions()

    def load_functions(self):
        try:
            with open(self.functions_definition, "r") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Input JSON must be a list.")

            return data

        except FileNotFoundError:
            raise FileNotFoundError("Missing functions file.")

        except json.JSONDecodeError:
            raise ValueError("Functions file is not valid JSON.")

    def parse_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--functions_definition",
                            type=str,
                            default="data/input/functions_definition.json")
        parser.add_argument("--input",
                            type=str,
                            default="data/input/function_calling_tests.json")
        parser.add_argument("--output",
                            type=str,
                            default="data/output/function_calling_results.json")
        args = parser.parse_args()

        func_path = Path(args.functions_definition)
        input_path = Path(args.input)
        output_path = Path(args.output)

        if not func_path.is_file():
            raise ValueError("functions definition path is invalid")

        if not input_path.is_file():
            raise ValueError("input path is invalid")
        
        if output_path.is_dir():
            output_path = output_path / "function_calling_results.json"

        if not output_path.exists():
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.touch()
            except:
                raise ValueError(f"Invalid output path or directory structure: '{output_path}'")

        return (func_path, input_path, output_path)

    def get_prompts(self) -> list[str]:
        try:
            with open(self.input) as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Input JSON must be a list.")

            prompts: list[str] = []

            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {index} must be a dictionary.")

                prompt = item.get("prompt")

                prompt_validator = PromptInput(prompt=prompt)
                prompts.append(prompt) 

            return prompts

        except ValidationError as e:
            raise ValueError(f"Each item must contain a string prompt.")

    def get_functions_definition(self):
        functions = []

        for func in self.funcs_def:
            params = []

            for param_name, param_data in func['parameters'].items():
                params.append(f"{param_name}:{param_data['type']}")
            func_validator = FunctionDefinition(name=func['name'],
                                                description=func['description'],
                                                parameters=func['parameters'],
                                                returns=func['returns'])
            functions.append(f"{func['name']}({', '.join(params)})")

        return "[" + ", \n".join(functions) + "]"

    def get_function_names(self) -> list[str]:
        return [func["name"] for func in self.funcs_def]

    def get_function_parameters(self, function_name: str) -> dict:
        for func in self.funcs_def:
            if func["name"] == function_name:
                return func["parameters"]

        raise ValueError(f'Function "{function_name}" does not exist.')

    def write_output(self, results):
        with open(self.output, "w") as file:
            json.dump(results, file, indent=4)

