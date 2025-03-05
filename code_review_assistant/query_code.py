#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from typing import Optional

from llama_index.core import Settings, load_index_from_storage, StorageContext
from llama_index.core.response.notebook_utils import display_response
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

def query_code_index(
    query: str,
    index_dir: str = "./data",
    model_name: str = "codellama:latest",
    embedding_model_name: str = "codellama:latest",
    temperature: float = 0.1,
    max_tokens: int = 2048,
    base_url: str = "http://127.0.0.1:11434",
    request_timeout: float = 60.0,
) -> None:
    """
    Execute a query against the indexed codebase.

    Args:
        query: The query to execute
        index_dir: Directory where the index is stored
        model_name: Ollama model name to use
        embedding_model_name: Ollama model name to use for embeddings
        temperature: Temperature parameter for generation
        max_tokens: Maximum number of tokens to generate
        base_url: Base URL for Ollama API
        request_timeout: Timeout for API requests in seconds
    """
    # Check if index directory exists
    if not os.path.exists(index_dir):
        print(f"Error: Index directory '{index_dir}' not found.")
        print("Please run 'index_code.py' first to create an index.")
        sys.exit(1)

    print(f"Executing query from index '{index_dir}'...")
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

    # Set up Ollama models
    llm = Ollama(
        model=model_name,
        base_url=base_url,
        request_timeout=request_timeout,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    embed_model = OllamaEmbedding(
        model_name=embedding_model_name,
        base_url=base_url,
        request_timeout=request_timeout
    )

    # Update global settings
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Load index
    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    index = load_index_from_storage(storage_context)

    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=5,  # Use top k search results
        response_mode="compact",  # Compact response
    )

    # Execute query
    print(f"\nQuery: {query}")
    print("\nGenerating response...\n")
    response = query_engine.query(query)

    # Display response
    print("=" * 80)
    print(response.response)
    print("=" * 80)

    # Display source nodes
    print("\nSource references:")
    for i, node in enumerate(response.source_nodes):
        print(f"\n[{i+1}] {node.metadata.get('file_path', 'Unknown')}")
        print(f"Relevance score: {node.score:.4f}")
        print("-" * 40)
        print(node.text[:300] + "..." if len(node.text) > 300 else node.text)

def interactive_mode(
    index_dir: str = "./data",
    model_name: str = "codellama:latest",
    embedding_model_name: str = "codellama:latest",
    base_url: str = "http://127.0.0.1:11434",
    request_timeout: float = 60.0,
) -> None:
    """
    Run queries in interactive mode.

    Args:
        index_dir: Directory where the index is stored
        model_name: Ollama model name to use
        embedding_model_name: Ollama model name to use for embeddings
        base_url: Base URL for Ollama API
        request_timeout: Timeout for API requests in seconds
    """
    print("Starting interactive mode. Type 'exit' or 'quit' to end the session.")
    print(f"Using Ollama API at: {base_url}")

    while True:
        try:
            query = input("\nEnter your query: ")
            if query.lower() in ["exit", "quit"]:
                print("Exiting interactive mode.")
                break

            if not query.strip():
                continue

            query_code_index(
                query,
                index_dir,
                model_name,
                embedding_model_name,
                base_url=base_url,
                request_timeout=request_timeout
            )

        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Start interactive mode if no arguments
        interactive_mode()
    else:
        # Process as a single query if arguments are provided
        query = sys.argv[1]
        index_dir = sys.argv[2] if len(sys.argv) > 2 else "./data"
        base_url = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:11434"

        query_code_index(query, index_dir, base_url=base_url)
