class Decoder:
    def __init__(self, file_manager, model):
        self.file_manager = file_manager
        self.model = model

        self.func_names = self.file_manager.get_function_names()
        self.func_names_token_ids = self.get_function_name_token_ids()
        self.number_token_ids = self.get_number_token_ids()
        self.bool_token_ids = self.get_bool_token_ids()
        self.string_token_ids = self.get_string_token_ids()

    def get_function_name_token_ids(self) -> set[int]:
        allowed_tokens = set()

        for func_name in self.func_names:
            token_ids = self.model.encode(func_name)[0]

            for token_id in token_ids:
                allowed_tokens.add(int(token_id))

        return allowed_tokens

    def get_number_token_ids(self) -> set[int]:
        allowed_tokens = set()

        pieces = "0123456789-.\n"
        for piece in pieces:
            for token_id in self.model.encode(piece)[0]:
                allowed_tokens.add(int(token_id))

        return allowed_tokens

    def get_bool_token_ids(self) -> set[int]:
        allowed_tokens = set()

        pieces = ["true", "false",
                  "yes", "no",
                  "1", "0", "\n"]

        for piece in pieces:
            for token_id in self.model.encode(piece)[0]:
                allowed_tokens.add(token_id)

        return allowed_tokens

    def get_string_token_ids(self) -> set[int]:
        allowed = set()

        for c in "".join(chr(i) for i in range(32, 127)) + "\n":
            for tid in self.model.encode(c)[0]:
                allowed.add(int(tid))
        return allowed

    def get_next_token_id(self, logits: list[float],
                    param_type: str | None = None) -> list[float]:

        allowed_tokens = set()

        if param_type in {"int", "integer", "float", "number"}:
            allowed_tokens = self.number_token_ids

        elif param_type in {"bool", "boolean"}:
            allowed_tokens = self.bool_token_ids

        elif param_type in {"string", "str"}:
            allowed_tokens = self.string_token_ids

        elif param_type is None:
            allowed_tokens = self.func_names_token_ids

        else:
            next_token_id = logits.index(max(logits))
            return next_token_id

        masked_logits = [float("-inf")] * len(logits)

        for token_id in allowed_tokens:
            masked_logits[token_id] = logits[token_id]

        next_token_id = masked_logits.index(max(masked_logits))
        return next_token_id

    def is_complete(self, text, param_type):
        if param_type:
            return "\n" in text
        text = text.strip()
        matches = [f for f in self.func_names if f.startswith(text)]
        return len(matches) == 1 and matches[0] == text
