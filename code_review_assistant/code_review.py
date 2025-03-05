#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

from llama_index.core import Settings, load_index_from_storage, StorageContext
try:
    from llama_index_llms_ollama import Ollama
    from llama_index_embeddings_ollama import OllamaEmbedding
except ImportError:
    try:
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
    except ImportError:
        print("Error: Could not import Ollama modules. Please make sure llama-index-llms-ollama and llama-index-embeddings-ollama are installed.")
        sys.exit(1)

def load_file_content(file_path: str) -> str:
    """
    Load the content of a file.

    Args:
        file_path: Path to the file to load

    Returns:
        The content of the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try Latin-1 if UTF-8 decoding fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def review_code(
    file_path: str,
    index_dir: str = "./data",
    model_name: str = "codellama:latest",
    embedding_model_name: str = "codellama:latest",
    temperature: float = 0.1,
    base_url: str = "http://127.0.0.1:11434",
    request_timeout: float = 60.0,
) -> None:
    """
    Perform a code review on the specified file.

    Args:
        file_path: Path to the file to review
        index_dir: Directory where the index is stored
        model_name: Ollama model name to use
        embedding_model_name: Ollama model name to use for embeddings
        temperature: Temperature parameter for generation
        base_url: Base URL for Ollama API
        request_timeout: Timeout for API requests in seconds
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Check if index directory exists
    if not os.path.exists(index_dir):
        print(f"Warning: Index directory '{index_dir}' not found.")
        print("Proceeding with code review without project knowledge.")
        has_index = False
    else:
        has_index = True

    print(f"Using Ollama API at: {base_url}")
    print(f"Request timeout: {request_timeout} seconds")

    # Test connection to Ollama server
    try:
        import requests
        version_response = requests.get(f"{base_url}/api/version", timeout=10)
        if version_response.status_code == 200:
            version_info = version_response.json()
            print(f"Connected to Ollama server version: {version_info.get('version', 'unknown')}")
        else:
            print(f"Warning: Could not get Ollama server version. Status code: {version_response.status_code}")
            print("Attempting to continue anyway...")
    except Exception as e:
        print(f"Warning: Could not connect to Ollama server at {base_url}: {e}")
        print("Please make sure Ollama is running and accessible.")
        user_input = input("Do you want to continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            sys.exit(1)

    # Load file content
    code_content = load_file_content(file_path)
    file_extension = os.path.splitext(file_path)[1]

    # Set up Ollama model
    llm = Ollama(
        model=model_name,
        base_url=base_url,
        request_timeout=request_timeout,
        temperature=temperature,
    )

    # Update global settings
    Settings.llm = llm

    # Create review prompt
    review_prompt = f"""
As an experienced senior engineer, please review the following code.
File: {file_path}

Provide a detailed explanation of issues, improvements, and suggestions based on best practices.
Evaluate the code from the following perspectives:
1. Code quality and readability
2. Performance issues
3. Security concerns
4. Error handling
5. Design pattern application
6. Testability
7. Documentation

Code:
```{file_extension}
{code_content}
```

Please provide a detailed code review in English.
"""

    # Utilize project knowledge if index exists
    if has_index:
        try:
            # Set up embedding model
            embed_model = OllamaEmbedding(
                model_name=embedding_model_name,
                base_url=base_url,
                request_timeout=request_timeout
            )
            Settings.embed_model = embed_model

            # Load index
            storage_context = StorageContext.from_defaults(persist_dir=index_dir)
            index = load_index_from_storage(storage_context)

            # Create query engine
            query_engine = index.as_query_engine(
                similarity_top_k=3,
                response_mode="compact",
            )

            # Get project knowledge
            context_query = f"Please provide specifications and design information related to this file: {file_path}"
            context_response = query_engine.query(context_query)

            # Add additional context to prompt
            review_prompt += f"""
Additional project context:
{context_response.response}

Please consider the above project context in your code review.
"""
        except Exception as e:
            print(f"Warning: Failed to retrieve context from index: {e}")
            print("Proceeding with code review without project knowledge.")

    print(f"Performing code review for file '{file_path}'...")

    # Execute review
    review_response = llm.complete(review_prompt)

    # Display results
    print("\n" + "=" * 80)
    print(f"【Code Review Results: {file_path}】")
    print("=" * 80)
    print(review_response.text)
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Code review tool using Ollama")
    parser.add_argument("file_path", help="Path to the file to review")
    parser.add_argument("--index-dir", "-i", default="./data", help="Directory where the index is stored")
    parser.add_argument("--model", "-m", default="codellama:latest", help="Ollama model name to use")
    parser.add_argument("--embedding-model", "-e", default="codellama:latest", help="Ollama model name to use for embeddings")
    parser.add_argument("--temperature", "-t", type=float, default=0.1, help="Temperature parameter for generation")
    parser.add_argument("--base-url", "-u", default="http://127.0.0.1:11434", help="Base URL for Ollama API")
    parser.add_argument("--request-timeout", "-r", type=float, default=60.0, help="Timeout for API requests in seconds")

    args = parser.parse_args()

    review_code(
        args.file_path,
        args.index_dir,
        args.model,
        args.embedding_model,
        args.temperature,
        args.base_url,
        args.request_timeout,
    )

if __name__ == "__main__":
    main()
