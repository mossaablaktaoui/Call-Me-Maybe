*This project has been created as part of the 42 curriculum by mlaktaou.*

# Call-Me-Maybe

## Description

Call-Me-Maybe is a Python project that translates natural-language prompts into structured function calls. Instead of answering a question directly, the program selects the most appropriate function from a JSON function definition file and extracts the required parameters.

Example:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The goal is to use a small language model with constrained decoding so the generated output stays machine-readable, valid, and compatible with the provided function schema.

## Instructions

### Installation

Install dependencies with:

```bash
make install
```

### Run

```bash
make run
```

With explicit input/output files:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

With another compatible model:

```bash
uv run python -m src --model Qwen/Qwen3-1.7B
```

Choose a visualizer:

```bash
uv run python -m src --visualizer terminal
uv run python -m src --visualizer gui
```

The default model is:

```text
Qwen/Qwen3-0.6B
```

### Debug

```bash
make debug
```

### Clean

```bash
make clean
```

### Lint and type-check

```bash
make lint
```

## Input Files

The program expects two JSON files by default:

```text
data/input/functions_definition.json
data/input/function_calling_tests.json
```

`functions_definition.json` contains the available functions, their parameter names, parameter types, return type, and description.

`function_calling_tests.json` contains the natural-language prompts to process.

## Output File

The program writes results to:

```text
data/output/function_calling_results.json
```

The output is a JSON array. Each object contains exactly:

- `prompt`: original prompt
- `name`: selected function name
- `parameters`: extracted function arguments

## Performance Analysis

The implementation is designed for reliability rather than raw speed.

- **Validity**: function names are constrained to known definitions, which helps avoid hallucinated function names.
- **Schema matching**: parameters are generated according to the selected function definition.
- **Speed**: prompts are processed one by one. This is simple and memory-friendly, but not as fast as batching.
- **Reliability**: JSON writing is handled with Python's `json` module, ensuring the final file is valid JSON if generation succeeds.

Expected performance depends on the selected model and hardware. The default target remains Qwen/Qwen3-0.6B.

## Challenges Faced

- **Small model reliability**: small LLMs can easily produce malformed structured output, so generation had to be restricted.
- **Token-level constraints**: function names can span multiple tokens, requiring prefix-based token filtering.
- **Type conversion**: generated parameter strings must be safely converted into numbers, booleans, or strings.

## Example Usage

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json \
  --model Qwen/Qwen3-0.6B
```

Example output object:

```json
{
  "prompt": "Reverse the string 'hello'",
  "name": "fn_reverse_string",
  "parameters": {"s": "hello"}
}
```

## Bonus Features

- **Multiple model support**: the program accepts `--model` to run with compatible Hugging Face causal language models while keeping `Qwen/Qwen3-0.6B` as the default.
- **Public tokenizer implementation**: `LLM_Model` implements its own `tokenize`, `encode`, and `decode` logic using the vocabulary and merges files instead of relying directly on the SDK tokenizer methods in the main generation flow.
- **Visualization of generation**: `visualterm.py` displays prompts, generated tokens, results, errors, and elapsed time in the terminal.
- **Encoding/decoding integration**: constrained decoding uses token IDs from the custom encoder and converts selected tokens back to text during generation.

Not implemented bonus features:

- batching or advanced performance optimizations;
- comprehensive automated test suite;
- complex nested function arguments;
- advanced error recovery mechanisms.

## Resources

Useful references:

- Google
- Gemini
- ChatGPT
- YouTube

## AI Usage

AI was used as an assistant for:

- understanding hard concepts;
- understanding the project requirements;
- reviewing code structure against the subject;
- fixing flake8 and mypy issues;

