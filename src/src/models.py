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
    def check_types(cls, data: Any) -> Any:
        if not isinstance(data["name"], str):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function name must be a string",
            )

        if not isinstance(data["description"], str):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function description must be a string",
            )

        if not isinstance(data["parameters"], dict):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function's parameters must be a dictionary",
            )

        if not isinstance(data["returns"], dict):
            raise ValueError(
                "Error in functions definition file:\n"
                "Function's returns must be a string",
            )
        return data


class PromptInput(BaseModel):
    """Represents one prompt from function_calling_tests.json."""

    prompt: str

    @model_validator(mode="before")
    @classmethod
    def check_types(cls, data: Any) -> Any:
        if not isinstance(data["prompt"], str):
            raise ValueError(
                "Error in prompts file:\n"
                "prompt must be a string",
            )
        return data
