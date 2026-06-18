class Decoder:
    def __init__(self, file_manager, model):
        self.file_manager = file_manager
        self.model = model

        self.allowed_function_names = self.file_manager.get_function_names()

    def mask_function_name_logits(self, logits: list[float],
                                  current_text: str,) -> list[float]:

        for token_id in range(len(logits)):
            token = self.model.decode([token_id])
            result = current_text + token.strip()

            if not any(function_name.startswith(text)
                       for function_name in self.allowed_function_names):
                logits[token_id] = float("-inf")

        return logits

    def mask_parameter_value_logits(self, logits: list[float],
                                    current_text: str,
                                    param_type: str,) -> list[float]:

        param_type = param_type.lower().strip()

        if param_type in {"int", "integer", "float", "number"}:
            return self.keep_number(logits)

        if param_type in {"bool", "boolean"}:
            return self.keep_bool(logits, current_text)

        return logits

    def is_complete_function_name(self, text: str) -> bool:
        text = text.strip()
        return text in self.allowed_function_names

    def value_is_finished(self, text: str) -> bool:
        return "\n" in text

    def keep_number(self, logits: list[float]) -> list[float]:
        allowed_chars = "0123456789.-"

        for token_id in range(len(logits)):
            token = self.model.decode([token_id])

            if "\n" in token:
                continue

            if not all(char in allowed_chars for char in token):
                logits[token_id] = float("-inf")

        return logits

    def keep_bool(self, logits: list[float],
                  current_text: str,) -> list[float]:

        allowed_values = ["true", "false", "1", "0", "yes", "no"]
        current_text = current_text.strip().lower()

        for token_id in range(len(logits)):
            token = self.model.decode([token_id])
            result = current_text + token.lower().strip()

            if "\n" in token:
                continue

            if not any(value.startswith(result) for value in allowed_values):
                logits[token_id] = float("-inf")

        return logits
