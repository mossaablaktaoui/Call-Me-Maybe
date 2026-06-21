import json
from typing import Any, List, Optional, Tuple, cast

from llm_sdk import Small_LLM_Model


class LLM_Model(Small_LLM_Model):
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        super().__init__(model_name=model_name)
        self.merges = self.set_merges()
        self.vocab = self.set_vocab()
        self.inverse_vocab = {value: key for key, value in self.vocab.items()}

    def set_vocab(self) -> dict[str, int]:
        with open(self.get_path_to_vocab_file(), "r") as file:
            data: Any = json.load(file)

        return cast(dict[str, int], data)

    def set_merges(self) -> dict[tuple[str, str], int]:
        merges: dict[tuple[str, str], int] = {}
        with open(self.get_path_to_merges_file(), "r") as file:
            data = file.readlines()

        for index, line in enumerate(data):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) == 2:
                merges[(parts[0], parts[1])] = index

        return merges

    def tokenize(self, text: str) -> List[str]:
        text = text.replace(" ", "Ġ").replace("\n", "Ċ").replace("\t", "ĉ")
        tokens = [char for char in text]

        while True:
            pair_to_merge = self.get_pair_to_merge(tokens)

            if pair_to_merge is None:
                break

            new_tokens = []
            index = 0
            while index < len(tokens):
                if index < len(tokens) - 1:
                    token_1 = tokens[index]
                    token_2 = tokens[index + 1]
                    if (token_1, token_2) == pair_to_merge:
                        new_tokens.append(token_1 + token_2)
                        index += 2
                        continue

                new_tokens.append(tokens[index])
                index += 1

            tokens = new_tokens

        return tokens

    def get_pair_to_merge(
        self,
        tokens: List[str],
    ) -> Optional[Tuple[str, str]]:
        pairs = []

        for index in range(len(tokens) - 1):
            pairs.append((tokens[index], tokens[index + 1]))

        if not pairs:
            return None

        best_pair = min(
            pairs,
            key=lambda pair: self.merges.get(pair, float("inf")),
        )

        if best_pair not in self.merges:
            return None

        return best_pair

    def encode(self, text: str) -> List[int]:
        tokens = self.tokenize(text)
        token_ids = []

        for token in tokens:
            token_ids.append(self.vocab[token])

        return token_ids

    def decode(self, tokens_ids: List[int]) -> str:
        tokens = []

        for token_id in tokens_ids:
            for vocab_token, vocab_token_id in self.vocab.items():
                if vocab_token_id == token_id:
                    tokens.append(vocab_token)
                    break

        text = "".join(tokens)
        text = text.replace("Ġ", " ").replace("Ċ", "\n").replace("ĉ", "\t")
        return text
