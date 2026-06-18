from typing import Any
from pydantic import BaseModel, model_validator


class FunctionDefinition(BaseModel):
    """Represents one available function from functions_definition.json."""

    name: str
    description: str | None = None
    parameters: dict[str, Any]
    returns: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def check_types(cls, data) -> 'FunctionDefinition':
        if not isinstance(data["name"], str):
            raise ValueError("Error in functions definition file:\n"
                             "Function name must be a string")

        if not isinstance(data["description"], str):
            raise ValueError("Error in functions definition file:\n"
                             "Function description must be a string")

        if not isinstance(data["parameters"], dict):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function's parameters must be a dictionary")

        if not isinstance(data["returns"], dict):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function's returns must be a string")
        return data


class PromptInput(BaseModel):
    """Represents one prompt from function_calling_tests.json."""

    prompt: str

    @model_validator(mode="before")
    @classmethod
    def check_types(cls, data) -> 'PromptInput':
        if not isinstance(data['prompt'], str):
            raise ValueError("Error in prompts file:\n"
                             "prompt must be a string")
        return data


"""
result_validator = FunctionCallResult(prompt=result_obj['prompt'],
                                      name=result_obj['name'],
                                      parameters=result_obj['parameters'])




class FunctionCallResult(BaseModel):
    "Represents one final output item."

    prompt: str
    name: str
    parameters: dict[str, Any] = Field(default_factory=dict)


    @model_validator(mode="before")
    def check_types(self) -> 'FunctionDefinition':
        if not isinstance(self.name, str):
            raise ValueError("Error in function call result file:\n"
                             "Function name must be a string")

        if not isinstance(self.prompt, str):
            raise ValueError("Error in function call result file:\n"
                             "Function prompt must be a string")

        if not isinstance(self.parameters, str):
            raise ValueError("Error in function call result file:\n"
                             "Function parameters must be a dictionary")

"""
