#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CakePHP Analyzer Demonstration Script

This script demonstrates the different ways to use the CakePHP analyzer
with the sample files created for testing.
"""

import os
import sys
import subprocess
import time

# Ensure we run from the project root
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
os.chdir('..')  # Move up to project root

def print_header(text):
    """Print a formatted header for each demonstration"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def run_command(command, description=None):
    """Run a command and print its output"""
    if description:
        print(f"\n> {description}\n")

    print(f"$ {command}\n")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)

    if result.stderr:
        print("ERRORS:")
        print(result.stderr)

    return result

def main():
    """Run the demonstration script"""
    print_header("CakePHP 2.10 Code Analyzer Demonstration")

    # Check if the test project exists
    if not os.path.exists('cakephp_test_project'):
        print("Creating sample CakePHP project structure...\n")
        os.makedirs('cakephp_test_project/app/Controller', exist_ok=True)
        os.makedirs('cakephp_test_project/app/Model', exist_ok=True)
        os.makedirs('cakephp_test_project/app/View/Users', exist_ok=True)

        # Copy sample files if they exist
        for src, dest in [
            ('sample_code.php', 'cakephp_test_project/app/Controller/UserController.php'),
            ('sample_model.php', 'cakephp_test_project/app/Model/Users.php'),
            ('sample_view.ctp', 'cakephp_test_project/app/View/Users/view.ctp')
        ]:
            if os.path.exists(src):
                with open(src, 'r') as f_src, open(dest, 'w') as f_dest:
                    f_dest.write(f_src.read())
                print(f"Copied {src} to {dest}")

    # Demo 1: Run the analyzer on the entire project
    print_header("1. Analyzing the entire CakePHP project")
    run_command("python code_review_assistant/analyze_cakephp.py cakephp_test_project",
                "Analyze the entire CakePHP project structure")

    # Demo 2: Analyze a specific controller file
    print_header("2. Analyzing a specific controller file with auto-detect")
    run_command("python code_review_assistant/analyze_cakephp.py cakephp_test_project/app/Controller/UserController.php --auto-detect",
                "Analyze a specific controller file and auto-detect project root")

    # Demo 3: Use JSON output
    print_header("3. Using JSON output format")
    run_command("python code_review_assistant/analyze_cakephp.py cakephp_test_project --output json",
                "Analyze project with JSON output format (useful for integration)")

    # Demo 4: Integrated with code_review.py
    print_header("4. Using the integrated code review tool")
    run_command("python code_review_assistant/code_review.py cakephp_test_project/app/View/Users/view.ctp",
                "Analyze a CakePHP view file with the integrated code review tool")

    print_header("CakePHP Analyzer Demonstration Complete")
    print("""
For more information on using the CakePHP analyzer, see:
- code_review_assistant/README_CAKEPHP.md (Documentation)
- code_review_assistant/cakephp_analyzer.py (Core analyzer implementation)
- code_review_assistant/analyze_cakephp.py (Standalone CLI tool)
    """)

if __name__ == "__main__":
    main()
