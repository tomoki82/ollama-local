#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import CakePHP analyzer
try:
    from cakephp_analyzer import analyze_cakephp, CakePHP210Analyzer
except ImportError:
    # If imported from a different directory
    try:
        from code_review_assistant.cakephp_analyzer import analyze_cakephp, CakePHP210Analyzer
    except ImportError:
        print("Error: Could not import CakePHP analyzer.")
        sys.exit(1)

def find_cakephp_project(start_path: str) -> str:
    """
    Find a CakePHP project root directory starting from the given path.

    Args:
        start_path: Path to start searching from

    Returns:
        The path to the CakePHP project root
    """
    if os.path.isfile(start_path):
        start_path = os.path.dirname(start_path)

    # CakePHP structure markers
    markers = ['app/Controller', 'app/Model', 'app/View', 'app/Config', 'lib/Cake']

    current_path = start_path
    while os.path.dirname(current_path) != current_path:  # Stop at filesystem root
        # Check if this directory has CakePHP structure
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in markers):
            return current_path
        current_path = os.path.dirname(current_path)

    # If we couldn't find a CakePHP project, return the original path
    return start_path

def main():
    """Main function to run the CakePHP analyzer"""
    parser = argparse.ArgumentParser(description="CakePHP 2.10 Code Analyzer")
    parser.add_argument("path", help="Path to the CakePHP project or file to analyze")
    parser.add_argument("--output", "-o", default="console", choices=["console", "json"],
                        help="Output format")
    parser.add_argument("--auto-detect", "-a", action="store_true",
                        help="Auto-detect CakePHP project root")
    parser.add_argument("--version", "-v", action="version", version="CakePHP Analyzer 1.0")

    args = parser.parse_args()

    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' not found.")
        sys.exit(1)

    # Auto-detect CakePHP project root if requested
    if args.auto_detect:
        detected_path = find_cakephp_project(args.path)
        if detected_path != args.path:
            print(f"Auto-detected CakePHP project root: {detected_path}")
            project_path = detected_path
        else:
            # If no CakePHP project was detected, check if we're analyzing a specific file
            if os.path.isfile(args.path):
                # Use the current working directory or parent directories
                cwd = os.getcwd()
                print(f"No CakePHP project structure found. Using current directory: {cwd}")
                project_path = cwd
            else:
                project_path = args.path
    else:
        project_path = args.path

    # Run the analyzer
    analyze_cakephp(project_path, args.output)

if __name__ == "__main__":
    main()
