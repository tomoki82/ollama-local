#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, TextIO

# Import the CakePHP analyzer
try:
    from cakephp_analyzer import analyze_cakephp
except ImportError:
    # If imported from a different directory
    try:
        from code_review_assistant.cakephp_analyzer import analyze_cakephp
    except ImportError:
        print("Warning: Could not import CakePHP analyzer. CakePHP-specific analysis will be disabled.")
        analyze_cakephp = None

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
    output_file: Optional[str] = None,
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
        output_file: Optional path to save the review results
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

    # Check if it's a CakePHP file and analyze with CakePHP analyzer
    cakephp_issues = None
    if analyze_cakephp and (file_extension in ['.php', '.ctp'] or '/cakephp' in file_path.lower() or '/cake' in file_path.lower()):
        print("Detected potential CakePHP file. Running CakePHP-specific analysis...")

        # Try to find the CakePHP project root
        project_root = file_path
        cakephp_markers = ['app/Controller', 'app/Model', 'app/View', 'app/Config', 'lib/Cake']

        while os.path.dirname(project_root) != project_root:  # Stop at filesystem root
            project_root = os.path.dirname(project_root)
            # Check if this directory has CakePHP structure
            if any(os.path.exists(os.path.join(project_root, marker)) for marker in cakephp_markers):
                break

        if project_root == os.path.dirname(project_root):  # If we reached filesystem root
            project_root = os.path.dirname(file_path)  # Default to the file's directory

        print(f"Using CakePHP project root: {project_root}")

        try:
            cakephp_issues = analyze_cakephp(project_root, output_format=None)

            # Add CakePHP issues to prompt
            if cakephp_issues and cakephp_issues["total_issues"] > 0:
                cake_issues_str = []

                if cakephp_issues["critical"]:
                    cake_issues_str.append("CRITICAL ISSUES:")
                    for issue in cakephp_issues["critical"]:
                        issue_str = f"[{issue['type']}] {issue['file']}"
                        if "line" in issue:
                            issue_str += f":{issue['line']}"
                        issue_str += f" - {issue['message']}"
                        cake_issues_str.append(issue_str)

                if cakephp_issues["high"]:
                    cake_issues_str.append("\nHIGH SEVERITY ISSUES:")
                    for issue in cakephp_issues["high"]:
                        issue_str = f"[{issue['type']}] {issue['file']}"
                        if "line" in issue:
                            issue_str += f":{issue['line']}"
                        issue_str += f" - {issue['message']}"
                        cake_issues_str.append(issue_str)

                # Add medium and warning issues
                for severity in ["medium", "warning"]:
                    if cakephp_issues[severity]:
                        cake_issues_str.append(f"\n{severity.upper()} ISSUES:")
                        for issue in cakephp_issues[severity]:
                            issue_str = f"[{issue['type']}] {issue['file']}"
                            if "line" in issue:
                                issue_str += f":{issue['line']}"
                            issue_str += f" - {issue['message']}"
                            cake_issues_str.append(issue_str)

                # Add to review prompt
                review_prompt += "\n\nCakePHP Specific Analysis Results:\n"
                review_prompt += "\n".join(cake_issues_str)
                review_prompt += "\n\nPlease address these CakePHP specific issues in your review."
        except Exception as e:
            print(f"Error during CakePHP analysis: {e}")
            print("Continuing with standard code review...")

    # Execute review
    review_response = llm.complete(review_prompt)

    # Open output file if specified
    output_stream = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout

    try:
        # Display results
        print_output(output_stream, "\n" + "=" * 80)
        print_output(output_stream, f"【Code Review Results: {file_path}】")
        print_output(output_stream, "=" * 80)

        # Display CakePHP-specific issues if available
        if cakephp_issues and cakephp_issues["total_issues"] > 0:
            print_output(output_stream, "CakePHP Specific Issues:")
            print_output(output_stream, "-" * 40)
            print_output(output_stream, f"Total issues found: {cakephp_issues['total_issues']}")

            if cakephp_issues["critical"]:
                print_output(output_stream, "\nCRITICAL ISSUES:")
                for issue in cakephp_issues["critical"]:
                    file_info = issue["file"]
                    if "line" in issue:
                        file_info += f":{issue['line']}"
                    print_output(output_stream, f"[{issue['type']}] {file_info}")
                    print_output(output_stream, f"  {issue['message']}")

            if cakephp_issues["high"]:
                print_output(output_stream, "\nHIGH SEVERITY ISSUES:")
                for issue in cakephp_issues["high"]:
                    file_info = issue["file"]
                    if "line" in issue:
                        file_info += f":{issue['line']}"
                    print_output(output_stream, f"[{issue['type']}] {file_info}")
                    print_output(output_stream, f"  {issue['message']}")

            # Add medium and warning issues summary
            for severity in ["medium", "warning"]:
                if cakephp_issues[severity]:
                    print_output(output_stream, f"\n{severity.upper()} ISSUES: {len(cakephp_issues[severity])}")

            print_output(output_stream, "\n" + "-" * 40)

        print_output(output_stream, "\nGeneral Code Review:")
        print_output(output_stream, review_response.text)
        print_output(output_stream, "=" * 80)
    finally:
        # Close file if it was opened
        if output_file and output_stream != sys.stdout:
            output_stream.close()
            print(f"Review results saved to: {output_file}")

def print_output(output_stream: TextIO, message: str) -> None:
    """Print message to the specified output stream.

    Args:
        output_stream: The output stream to write to (file or stdout)
        message: The message to print
    """
    print(message, file=output_stream)

def main():
    parser = argparse.ArgumentParser(description="Code review tool using Ollama")
    parser.add_argument("file_path", help="Path to the file to review")
    parser.add_argument("--index-dir", "-i", default="./data", help="Directory where the index is stored")
    parser.add_argument("--model", "-m", default="codellama:latest", help="Ollama model name to use")
    parser.add_argument("--embedding-model", "-e", default="codellama:latest", help="Ollama model name to use for embeddings")
    parser.add_argument("--temperature", "-t", type=float, default=0.1, help="Temperature parameter for generation")
    parser.add_argument("--base-url", "-u", default="http://127.0.0.1:11434", help="Base URL for Ollama API")
    parser.add_argument("--request-timeout", "-r", type=float, default=60.0, help="Timeout for API requests in seconds")
    parser.add_argument("--output", "-o", help="Path to save the review results (defaults to terminal output)")
    parser.add_argument("--log-dir", "-l", help="Directory to save log files (auto-generates filenames)")

    args = parser.parse_args()

    # Determine output file path
    output_file = None
    if args.output:
        output_file = args.output
    elif args.log_dir:
        # Create log directory if it doesn't exist
        log_dir = Path(args.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create filename based on the reviewed file and timestamp
        filename = os.path.basename(args.file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = str(log_dir / f"review_{filename}_{timestamp}.txt")

    review_code(
        args.file_path,
        args.index_dir,
        args.model,
        args.embedding_model,
        args.temperature,
        args.base_url,
        args.request_timeout,
        output_file,
    )

if __name__ == "__main__":
    main()
