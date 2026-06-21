import argparse
import json
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from src.models import FunctionDefinition, PromptInput


class FileManager:
    def __init__(self) -> None:
        arguments = self.parse_argument()
        self.functions_definition = arguments[0]
        self.input = arguments[1]
        self.output = arguments[2]
        self.model_name = arguments[3]
        self.funcs_def = self.load_functions()

    def load_functions(self) -> list[dict[str, Any]]:
        try:
            with open(self.functions_definition, "r") as file:
                data: Any = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Input JSON must be a list.")

            return cast(list[dict[str, Any]], data)

        except FileNotFoundError:
            raise FileNotFoundError("Missing functions file.")

        except json.JSONDecodeError:
            raise ValueError("Functions file is not valid JSON.")

    def parse_argument(self) -> tuple[Path, Path, Path, str]:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--functions_definition",
            type=str,
            default="data/input/functions_definition.json",
        )
        parser.add_argument(
            "--input",
            type=str,
            default="data/input/function_calling_tests.json",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="data/output/function_calling_results.json",
        )
        parser.add_argument(
            "--model",
            type=str,
            default="Qwen/Qwen3-0.6B",
            help="Hugging Face causal language model to use.",
        )
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
            except OSError as error:
                raise ValueError(
                    "Invalid output path or directory structure: "
                    f"'{output_path}'",
                ) from error

        return (func_path, input_path, output_path, args.model)

    def get_prompts(self) -> list[str]:
        try:
            with open(self.input) as file:
                data: Any = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Input JSON must be a list.")

            prompts: list[str] = []

            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {index} must be a dictionary.")

                prompt = item.get("prompt")
                if not isinstance(prompt, str):
                    raise ValueError("prompt must be a string")

                PromptInput(prompt=prompt)
                prompts.append(prompt)

            return prompts

        except ValidationError as error:
            raise ValueError(
                "Each item must contain a string prompt.",
            ) from error

    def get_functions_definition(self) -> str:
        functions = []

        for func in self.funcs_def:
            params = []

            for param_name, param_data in func["parameters"].items():
                params.append(f"{param_name}:{param_data['type']}")
            FunctionDefinition(
                name=func["name"],
                description=func["description"],
                parameters=func["parameters"],
                returns=func["returns"],
            )
            functions.append(f"{func['name']}({', '.join(params)})")

        return "[" + ", \n".join(functions) + "]"

    def get_function_names(self) -> list[str]:
        return [str(func["name"]) for func in self.funcs_def]

    def get_function_parameters(self, function_name: str) -> dict[str, Any]:
        for func in self.funcs_def:
            if func["name"] == function_name:
                return cast(dict[str, Any], func["parameters"])

        raise ValueError(f'Function "{function_name}" does not exist.')

    def write_output(self, results: list[dict[str, Any]]) -> None:
        with open(self.output, "w") as file:
            json.dump(results, file, indent=4)
