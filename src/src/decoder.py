from typing import Any


class Decoder:
    def __init__(self, file_manager: Any, model: Any) -> None:
        self.file_manager = file_manager
        self.model = model

        self.func_names = self.file_manager.get_function_names()
        self.number_token_ids = self.get_number_token_ids()
        self.bool_token_ids = self.get_bool_token_ids()

    def get_function_name_token_ids(self, loop: int) -> set[int]:
        allowed_tokens = set()
        allow_stop = False

        for func_name in self.func_names:
            token_ids = self.model.encode(func_name)

            if loop < len(token_ids):
                allowed_tokens.add(int(token_ids[loop]))
            elif loop == len(token_ids):
                allow_stop = True

        if allow_stop:
            for token_id in self.model.encode("\n"):
                allowed_tokens.add(int(token_id))

        return allowed_tokens

    def get_number_token_ids(self) -> set[int]:
        allowed_tokens = set()
        pieces = "0123456789-.\n"
        for piece in pieces:
            for token_id in self.model.encode(piece):
                allowed_tokens.add(int(token_id))
        return allowed_tokens

    def get_bool_token_ids(self) -> set[int]:
        allowed_tokens = set()
        pieces = ["true", "false", "yes", "no", "1", "0", "\n"]
        for piece in pieces:
            for token_id in self.model.encode(piece):
                allowed_tokens.add(int(token_id))
        return allowed_tokens

    def get_next_token_id(
        self,
        logits: list[float],
        param_type: str | None = None,
        loop: int = 0,
    ) -> int:
        allowed_tokens = set()

        if param_type in {"int", "integer", "float", "number"}:
            allowed_tokens = self.number_token_ids
        elif param_type in {"bool", "boolean"}:
            allowed_tokens = self.bool_token_ids
        elif param_type is None:
            allowed_tokens = self.get_function_name_token_ids(loop)
        else:
            next_token_id = logits.index(max(logits))
            return next_token_id

        masked_logits = [float("-inf")] * len(logits)

        for token_id in allowed_tokens:
            masked_logits[token_id] = logits[token_id]

        next_token_id = masked_logits.index(max(masked_logits))
        return next_token_id

    def get_string_value(self, text: str) -> str:
        result = []
        index = 0
        while index < len(text):
            char = text[index]
            if char == '"':
                prev_char = text[index - 1] if index > 0 else ""
                if prev_char == "\\":
                    result.append(char)
                else:
                    break
            else:
                result.append(char)
            index += 1

        return "".join(result)

    def is_complete(self, text: str, param_type: str | None) -> bool:
        if param_type is None:
            text = text.strip()
            matches = [
                func for func in self.func_names if func.startswith(text)
            ]
            return len(matches) == 1 and matches[0] == text

        if param_type in {"string", "str"}:
            for index, char in enumerate(text):
                if char == '"':
                    prev_char = text[index - 1] if index > 0 else ""
                    if prev_char != "\\":
                        return True
            return False

        return "\n" in text
