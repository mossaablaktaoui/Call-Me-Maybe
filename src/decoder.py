class Decoder:
    def __init__(self, file_manager, model):
        self.file_manager = file_manager
        self.model = model

        self.allowed_function_names = self.file_manager.get_function_names()
        self.end_token = "\n"

    def mask_function_name_logits(self, logits: list[float],
                                  current_text: str,) -> list[float]:

        masked_logits = logits.copy()
        current_text = current_text.strip()

        for token_id in range(len(masked_logits)):
            token = self.model.decode([token_id])
            candidate = current_text + token.strip()

            if not self.is_function_name_prefix(candidate):
                masked_logits[token_id] = float("-inf")

        return masked_logits

    def mask_parameter_value_logits(
        self,
        logits: list[float],
        current_text: str,
        param_type: str,
    ) -> list[float]:
        masked_logits = logits.copy()
        param_type = param_type.lower().strip()

        if param_type in {"int", "integer", "float", "number"}:
            return self.keep_number_or_newline(masked_logits)

        if param_type in {"bool", "boolean"}:
            return self.keep_bool_or_newline(masked_logits, current_text)

        return self.keep_string_or_newline(masked_logits)

    def is_function_name_prefix(self, text: str) -> bool:
        text = text.strip()

        if text == "":
            return True

        return any(
            function_name.startswith(text)
            for function_name in self.allowed_function_names
        )

    def is_complete_function_name(self, text: str) -> bool:
        text = text.strip()
        return text in self.allowed_function_names

    def value_is_finished(self, text: str) -> bool:
        return self.end_token in text

    def clean_end_token(self, text: str) -> str:
        return text.split(self.end_token)[0].strip()

    def keep_number_or_newline(self, logits: list[float]) -> list[float]:
        allowed_chars = "0123456789.-"

        for token_id in range(len(logits)):
            token = self.model.decode([token_id])

            if token == "":
                logits[token_id] = float("-inf")
                continue

            if "\n" in token:
                continue

            if not all(char in allowed_chars for char in token):
                logits[token_id] = float("-inf")

        return logits

    def keep_string_or_newline(self, logits: list[float]) -> list[float]:
        for token_id in range(len(logits)):
            token = self.model.decode([token_id])

            if token == "":
                logits[token_id] = float("-inf")

        return logits

    def keep_bool_or_newline(
        self,
        logits: list[float],
        current_text: str,
    ) -> list[float]:
        allowed_values = ["true", "false"]
        current_text = current_text.strip().lower()

        for token_id in range(len(logits)):
            token = self.model.decode([token_id])
            candidate = current_text + token.lower().strip()

            if "\n" in token:
                continue

            if not any(value.startswith(candidate) for value in allowed_values):
                logits[token_id] = float("-inf")

        return logits
