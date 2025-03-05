# Ollama Code Review Assistant

This project is a tool that uses Ollama and llama-index to learn the knowledge of your codebase in a local environment and assist with code reviews. It supports projects using technology stacks such as CakePHP 2.10, jQuery, Redis, Memcached, MySQL, and Angular 1.

## Prerequisites

- Python 3.8 or higher
- Ollama (locally installed)
- CodeLlama model (or other suitable code model)

## Setup

1. Install Ollama (for macOS):
   ```bash
   brew install ollama
   ```

2. Start the Ollama service:
   ```bash
   brew services start ollama
   ```

3. Download the CodeLlama model:
   ```bash
   ollama pull codellama
   ```

4. Create a Python virtual environment and install the required packages:
   ```bash
   python -m venv ollama_env
   source ollama_env/bin/activate
   pip install --upgrade llama-index llama-index-embeddings-ollama llama-index-llms-ollama
   pip install matplotlib ipython  # Additional dependencies
   ```

## Directory Structure

The project has the following directory structure:
```
Ollama_local/
├── code_review_assistant/
│   ├── index_code.py
│   ├── query_code.py
│   ├── code_review.py
│   └── test_connection.py
├── data/
├── sample_code.js
├── sample_code.php
└── README.md
```

Make sure you run the scripts from the correct directory. All scripts should be run from the root directory of the project.

## Usage

### 0. Connection Test

Test the connection to the Ollama server to ensure it's properly configured:

```bash
python code_review_assistant/test_connection.py
```

This script will attempt to connect to the Ollama server using multiple URLs and identify the optimal connection URL.

### 1. Indexing Your Codebase

Index your project's codebase so that the LLM can learn about your code:

```bash
python code_review_assistant/index_code.py /path/to/your/project ./data
```

- `/path/to/your/project`: Path to the project you want to index
- `./data`: Directory to save the index (optional, default is `./data`)
- Additional options: You can specify a custom base URL like `http://127.0.0.1:11434`

### 2. Querying Your Codebase

Ask questions about your indexed codebase to get information about your project:

```bash
# Interactive mode
python code_review_assistant/query_code.py

# Single query
python code_review_assistant/query_code.py "How does the user authentication work?" ./data
```

### 3. Code Review

Perform a code review on a specific file:

```bash
python code_review_assistant/code_review.py /path/to/your/file.php --index-dir ./data
```

Options:
- `--index-dir`, `-i`: Index directory (default: `./data`)
- `--model`, `-m`: Ollama model to use (default: `codellama:latest`)
- `--embedding-model`, `-e`: Model to use for embeddings (default: `codellama:latest`)
- `--temperature`, `-t`: Temperature parameter for generation (default: `0.1`)
- `--base-url`, `-u`: Base URL for Ollama API (default: `http://127.0.0.1:11434`)
- `--request-timeout`, `-r`: Timeout for API requests in seconds (default: `60.0`)

## Key Features

1. **Codebase Indexing**: Analyzes your project's code and indexes it in a vector database.
2. **Knowledge Base Querying**: Ask questions about your indexed codebase to get information about your project's specifications and design.
3. **Code Review**: Perform code reviews on specific files, leveraging the knowledge of your project.

## Supported File Formats

By default, the following file extensions are indexed:
- `.php`, `.ctp` (CakePHP)
- `.js` (JavaScript/jQuery/Angular)
- `.html`, `.css`
- `.sql` (MySQL)
- `.json`, `.md`, `.txt`, `.yml`, `.yaml`

## Notes

- Indexing may take time depending on the size of your codebase.
- Code reviews for large files may only be partially processed due to model context length limitations.
- Consider using larger models (e.g., `codellama:13b`) for higher quality results.

## Troubleshooting

### Path and Directory Issues

- **File not found errors**: Make sure you're running the scripts from the root directory of the project (Ollama_local), not from inside the code_review_assistant directory.

  ```bash
  # INCORRECT (from inside code_review_assistant directory)
  python query_code.py "What is the purpose of this codebase?" ../

  # CORRECT (from the root directory)
  python code_review_assistant/query_code.py "What is the purpose of this codebase?" ./
  ```

- **Working directory**: If you get errors like `can't open file '/Users/.../query_code.py'`, check your current directory with `pwd` and navigate to the correct directory.

- **Relative paths**: When specifying paths for indexing or querying, make sure they are relative to your current working directory.

### Connection Issues

- Make sure the Ollama service is running.
- Use `127.0.0.1` instead of `localhost`. If you experience connection URL issues, run the `test_connection.py` script to identify the optimal URL.
- Ensure model names are exact (e.g., `codellama:latest`). Check installed models with `ollama list`.

### Common Problems

- If you have issues downloading models, check installed models with `ollama list`.
- If you encounter memory errors, use a smaller model or increase your system resources.
- If you encounter dependency errors, make sure all necessary packages are installed (especially `matplotlib` and `ipython`).

### Error Messages and Solutions

| Error Message | Possible Cause | Solution |
|------------|------------|------------|
| `Connection refused` | Ollama service is not running | Run `brew services start ollama` |
| `No module named 'matplotlib'` | Missing required libraries | Run `pip install matplotlib ipython` |
| `No such file or directory: '.../docstore.json'` | Index has not been created | Run `index_code.py` first |
| `Could not import Ollama modules` | Missing llama-index dependencies | Run `pip install llama-index-llms-ollama llama-index-embeddings-ollama` |
| `can't open file '/path/to/query_code.py'` | Running script from wrong directory | Navigate to the root directory and use `python code_review_assistant/query_code.py` |

## Advanced Usage

### Using Custom Models

To use a different model:

```bash
ollama pull llama3.2
python code_review_assistant/code_review.py file.php --model llama3.2:latest
```

### Handling Large Projects

For large projects, you can reduce processing time by indexing only specific directories:

```bash
python code_review_assistant/index_code.py /path/to/project/src ./data
```
