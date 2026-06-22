# Call-Me-Maybe

## Description

Call-Me-Maybe is a local LLM function-calling experiment that converts natural-language prompts into structured JSON function calls.

Instead of returning a free-form answer, the model must choose one function from a provided function schema and extract the required parameters from the user prompt.

Example output:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {
    "a": 2.0,
    "b": 3.0
  }
}
```

The project focuses on reliable structured generation with small local language models by using constrained decoding, schema-aware prompts, and token-level validation.

## Features

- Local inference with Hugging Face causal language models
- Default support for `Qwen/Qwen3-0.6B`
- Custom tokenization / encoding / decoding flow
- Constrained decoding to reduce invalid function names and malformed values
- JSON input/output pipeline
- Function schema parsing and parameter extraction
- Terminal visualizer for live token generation
- GUI visualizer for a more interactive generation view
- Configurable model, input files, output file, and visualizer from the CLI

## Visualizers

Call-Me-Maybe includes two visualizers that make the generation process easier to inspect.

### Terminal Visualizer

The terminal visualizer streams generated tokens directly in the console and prints each final structured result.

```bash
uv run python -m src --visualizer terminal
```

<p align="center">
  <img src="https://github.com/mossaablaktaoui/Assests/blob/main/terminal-visualizer.png?raw=true" width="60%" alt="Terminal visualizer demo">
</p>


### GUI Visualizer

The GUI visualizer opens a Tkinter window showing:

- current prompt progress;
- elapsed generation time;
- the active prompt;
- live generated tokens;
- final parsed JSON result.

```bash
uv run python -m src --visualizer gui
```

<p align="center">
  <img src="https://github.com/mossaablaktaoui/Assests/blob/main/Screenshot%20from%202026-06-22%2019-29-30.png?raw=true" width="60%" alt="Terminal visualizer demo">
</p>


## Project Structure

```text
.
├── README.md
└── src
    ├── data
    │   ├── input
    │   └── output
    ├── llm_sdk
    ├── src
    │   ├── builder.py
    │   ├── decoder.py
    │   ├── file_manager.py
    │   ├── gui_visualizer.py
    │   ├── LLM_model.py
    │   ├── models.py
    │   └── terminal_visualizer.py
    ├── Makefile
    └── pyproject.toml
```

## Installation

From the repository root:

```bash
cd src
make install
```

Or directly with `uv`:

```bash
cd src
uv sync
```

## Usage

Run with the default configuration:

```bash
cd src
make run
```

Run manually:

```bash
cd src
uv run python -m src
```

Use explicit files:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Use another compatible model:

```bash
uv run python -m src --model Qwen/Qwen3-1.7B
```

Choose a visualizer:

```bash
uv run python -m src --visualizer terminal
uv run python -m src --visualizer gui
```

## CLI Options

| Option | Description | Default |
| --- | --- | --- |
| `--functions_definition` | JSON file containing available functions | `data/input/functions_definition.json` |
| `--input` | JSON file containing prompts | `data/input/function_calling_tests.json` |
| `--output` | Output JSON file | `data/output/function_calling_results.json` |
| `--model` | Hugging Face causal language model | `Qwen/Qwen3-0.6B` |
| `--visualizer` | Display mode: `terminal` or `gui` | `terminal` |

## Input Format

Function definitions are stored as JSON and describe the available function names, parameters, return types, and descriptions.

Prompt input example:

```json
[
  {
    "prompt": "Reverse the string 'hello'"
  }
]
```

## Output Format

The program writes a JSON array of generated function calls:

```json
[
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {
      "s": "hello"
    }
  }
]
```

## How It Works

1. Load function definitions and user prompts from JSON files.
2. Build a prompt asking the model to select the correct function.
3. Use constrained decoding to keep generated function names inside the known function list.
4. Generate each parameter separately according to the selected function schema.
5. Cast generated values into the expected Python/JSON types.
6. Save the final structured calls to the output file.
7. Stream progress through the selected visualizer.

## Concepts I Learned

While building this project, I practiced and learned several important concepts:

- **Function calling with LLMs**: converting natural language into structured function calls instead of free-form text.
- **Constrained decoding**: limiting token choices during generation to improve reliability.
- **Token-level generation**: inspecting and handling model output one token at a time.
- **Tokenizer internals**: working with encode/decode logic, token IDs, vocabulary behavior, and generated text reconstruction.
- **Schema-guided generation**: using function definitions to guide what the model is allowed to produce.
- **Type casting and validation**: converting generated strings into integers, floats, booleans, and strings safely.
- **Local model inference**: running small Hugging Face models locally through Python.
- **Streaming UI updates**: displaying live generation in both terminal and GUI modes.
- **Threading with Tkinter**: running model generation in the background while keeping the GUI responsive.
- **CLI design**: exposing model, input/output, and visualizer choices through command-line flags.
- **Python project hygiene**: linting, type-checking, modular file organization, and reproducible dependency management with `uv`.


<p align="right"><code>This project was completed in 22 June 2026.</code></p>
