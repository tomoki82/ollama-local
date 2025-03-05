#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import List, Optional

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
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

def index_code_repository(
    repo_path: str,
    output_dir: str = "./data",
    file_extensions: Optional[List[str]] = None,
    model_name: str = "codellama:latest",
    embedding_model_name: str = "codellama:latest",
    base_url: str = "http://127.0.0.1:11434",
    request_timeout: float = 60.0,
) -> None:
    """
    Index a code repository and save it to a vector store.

    Args:
        repo_path: Path to the code repository to index
        output_dir: Directory to save the index
        file_extensions: List of file extensions to index (e.g. [".php", ".js", ".html"])
        model_name: Ollama model name to use
        embedding_model_name: Ollama model name to use for embeddings
        base_url: Base URL for Ollama API
        request_timeout: Timeout for API requests in seconds
    """
    print(f"Creating index for repository '{repo_path}'...")
    print(f"Using Ollama API at: {base_url}")
    print(f"Request timeout: {request_timeout} seconds")

    # Set default file extensions
    if file_extensions is None:
        file_extensions = [
            ".php", ".ctp", ".js", ".html", ".css",
            ".sql", ".json", ".md", ".txt", ".yml", ".yaml"
        ]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Test connection to Ollama server
    try:
        import requests
        version_response = requests.get(f"{base_url}/api/version", timeout=10)
        if version_response.status_code == 200:
            version_info = version_response.json()
            print(f"Connected to Ollama server version: {version_info.get('version', 'unknown')}")
        else:
            print(f"Warning: Could not get Ollama server version. Status code: {version_response.status_code}")
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
        request_timeout=request_timeout
    )
    embed_model = OllamaEmbedding(
        model_name=embedding_model_name,
        base_url=base_url,
        request_timeout=request_timeout
    )

    # Update global settings
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Set up text splitter
    text_splitter = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=100,
    )

    # Load files
    documents = []
    if os.path.isfile(repo_path):
        # Single file processing
        try:
            with open(repo_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with Latin-1 encoding if UTF-8 fails
            with open(repo_path, 'r', encoding='latin-1') as f:
                content = f.read()

        documents = [Document(text=content, metadata={"file_path": repo_path})]
        print(f"Loaded single file: {repo_path}")
    else:
        # Directory processing
        documents = SimpleDirectoryReader(
            input_dir=repo_path,
            recursive=True,
            required_exts=file_extensions,
            file_metadata=lambda file_path: {"file_path": file_path},
        ).load_data()
        print(f"Loaded {len(documents)} files from directory.")

    # Split documents into nodes
    nodes = text_splitter.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} nodes.")

    # Create index
    index = VectorStoreIndex(nodes)

    # Save index
    index.storage_context.persist(persist_dir=output_dir)
    print(f"Saved index to '{output_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index_code.py <repository_path> [output_directory] [base_url]")
        sys.exit(1)

    repo_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./data"
    base_url = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:11434"

    index_code_repository(repo_path, output_dir, base_url=base_url)
