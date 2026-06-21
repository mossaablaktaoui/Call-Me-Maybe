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

or directly:

```bash
uv sync
```

### Run

Default execution:

```bash
make run
```

or:

```bash
uv run python -m src
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
uv run python -m src --model Qwen/Qwen2.5-0.5B
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

This runs:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
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

## Algorithm Explanation

The program follows this pipeline:

1. Load and validate the function definitions and prompts.
2. Build a prompt describing the available function signatures.
3. Ask the language model to select the function name.
4. Apply constrained decoding while generating the function name:
   - only token sequences that match available function names are allowed;
   - invalid function-name tokens are masked by setting their logits to negative infinity;
   - generation stops only when a full valid function name is produced.
5. For each required parameter, build a parameter-specific prompt.
6. Generate the parameter value using type-aware token restrictions:
   - numbers only allow numeric-related tokens;
   - booleans only allow boolean-like tokens;
   - strings are generated until a closing quote is detected.
7. Cast the generated value to the expected Python type.
8. Write the final structured JSON output.

This approach reduces reliance on prompting alone. The model still chooses the function and values, but the decoder restricts invalid choices during generation.

## Design Decisions

- **Python package layout**: source files are inside `src/` and are executed with `python -m src`.
- **Pydantic models**: input structures are validated using Pydantic classes.
- **FileManager**: centralizes CLI argument parsing, JSON loading, validation, and output writing.
- **Decoder**: handles token filtering and constrained token selection.
- **LLM_Model**: wraps the provided SDK and includes public tokenizer encode/decode logic.
- **Terminal visualizer**: `visualterm.py` provides simple terminal progress output without requiring a GUI.
- **Multiple model support**: the `--model` option allows testing compatible Hugging Face causal language models while keeping Qwen/Qwen3-0.6B as the default.

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
- **CLI compatibility**: the program must work with default paths and optional custom paths.
- **Headless execution**: a terminal visualizer was added to avoid depending on a GUI environment during evaluation.

## Testing Strategy

The project can be validated by:

1. Running `make lint` to check flake8 and mypy compliance.
2. Running the program with the default input files.
3. Checking that the output file is valid JSON.
4. Verifying every output object contains only `prompt`, `name`, and `parameters`.
5. Verifying selected function names exist in `functions_definition.json`.
6. Verifying all required parameters are present and have the expected types.
7. Testing edge cases such as:
   - missing input files;
   - malformed JSON;
   - empty prompts;
   - large numbers;
   - strings with quotes or special characters;
   - custom function definitions.

## Example Usage

```bash
uv run python -m src
```

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

Implemented or partially implemented bonus-related features:

- support for selecting compatible models with `--model`;
- public tokenizer encode/decode implementation in `LLM_Model`;
- terminal visualization of generation progress;
- basic integration of tokenization with constrained decoding.

## Resources

Useful references:

- Python documentation: https://docs.python.org/3/
- JSON documentation: https://docs.python.org/3/library/json.html
- argparse documentation: https://docs.python.org/3/library/argparse.html
- Pydantic documentation: https://docs.pydantic.dev/
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/
- Hugging Face Transformers documentation: https://huggingface.co/docs/transformers/
- Qwen model page: https://huggingface.co/Qwen/Qwen3-0.6B

## AI Usage

AI was used as an assistant for:

- understanding the project requirements;
- reviewing code structure against the subject;
- improving the Makefile;
- fixing flake8 and mypy issues;
- creating a terminal visualizer;
- drafting documentation.

All generated suggestions were reviewed and adapted before being included in the project.
