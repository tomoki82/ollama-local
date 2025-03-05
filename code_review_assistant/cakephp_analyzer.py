#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class CakePHP210Analyzer:
    """Class for analyzing CakePHP 2.10 code"""

    def __init__(self, project_path: str):
        """Initialize the analyzer with the project path

        Args:
            project_path: Path to the CakePHP project to analyze
        """
        self.project_path = project_path
        self.issues = []
        self.cake_version = "2.10"

        # Define CakePHP MVC directory paths
        self.models_dir = os.path.join(project_path, 'app', 'Model')
        self.views_dir = os.path.join(project_path, 'app', 'View')
        self.controllers_dir = os.path.join(project_path, 'app', 'Controller')
        self.components_dir = os.path.join(project_path, 'app', 'Controller', 'Component')
        self.behaviors_dir = os.path.join(project_path, 'app', 'Model', 'Behavior')
        self.helpers_dir = os.path.join(project_path, 'app', 'View', 'Helper')

        # Deprecated methods in CakePHP 2.10 and their recommended alternatives
        self.deprecated_methods = {
            "Set::": "Hash::",
            "->saveField(": "->save()",
            "->data": "->request->data",
            "->Model->": "->",
            "->paginate(null": "->paginate()",
            "->render(null": "->render()",
            "->beforeFilter(parent::beforeFilter": "parent::beforeFilter(); // then add your code",
            "->beforeRender(parent::beforeRender": "parent::beforeRender(); // then add your code",
            "->afterFilter(parent::afterFilter": "parent::afterFilter(); // then add your code",
            "->fields": "->schema()",
            "->name": "Table configuration",
            "->del(": "->delete(",
            "Router::connect": "Router::scope",
            "CakeRequest": "Request class",
            "CakeResponse": "Response class",
            "CakeSession": "Session class",
            "->Session->": "->getSession()->",
            "->Auth->login": "->Auth->identify()",
            "->data->": "->request->data->"
        }

        # Common security vulnerability patterns
        self.security_patterns = {
            "sql_injection": [
                r"->query\(\s*[\"']SELECT.*\$(?!\{)",
                r"->execute\(\s*[\"']SELECT.*\$(?!\{)",
                r"->query\(\s*[\"']UPDATE.*\$(?!\{)",
                r"->query\(\s*[\"']DELETE.*\$(?!\{)",
                r"->query\(\s*[\"']INSERT.*\$(?!\{)",
                r"->rawQuery\(\s*[\"'].*\$(?!\{)"
            ],
            "xss": [
                r"echo\s+\$(?!this->Html->|this->Form->)(?!.*h\()",
                r"<\?=\s*\$(?!this->Html->|this->Form->)(?!.*h\()"
            ],
            "csrf": [
                r"SecurityComponent.*csrf\s*=>\s*false"
            ],
            "mass_assignment": [
                r"->saveAll\(\$this->request->data",
                r"->save\(\$this->request->data\)",
                r"->save\(\$_POST",
                r"->save\(\$data(?!.*[\'\"]\w+[\'\"])"
            ]
        }

    def analyze_project(self) -> List[Dict[str, Any]]:
        """Analyze the entire project

        Returns:
            List of issue dictionaries with details about found problems
        """
        print(f"Analyzing CakePHP 2.10 project at: {self.project_path}")

        if not os.path.exists(self.project_path):
            print(f"Error: Project path '{self.project_path}' does not exist.")
            return []

        self._scan_files()
        return self.issues

    def _scan_files(self):
        """Scan all files in the project and perform analysis"""
        php_extensions = ['.php', '.ctp']

        # Walk through the project directory
        for root, _, files in os.walk(self.project_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in php_extensions:
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path)

    def _analyze_file(self, file_path: str):
        """Analyze a single file

        Args:
            file_path: Path to the file to analyze
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                self.issues.append({
                    "file": file_path,
                    "type": "file_error",
                    "severity": "error",
                    "message": f"Could not read file: {str(e)}"
                })
                return

        # Run all checks
        self.issues.extend(self.check_naming_conventions(file_path, content))
        self.issues.extend(self.check_deprecated_features(file_path, content))
        self.issues.extend(self.check_security_issues(file_path, content))

    def check_naming_conventions(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check adherence to CakePHP naming conventions

        Args:
            file_path: Path to the file being analyzed
            content: Content of the file

        Returns:
            List of naming convention issues
        """
        issues = []
        rel_path = os.path.relpath(file_path, self.project_path)

        # Controller checks
        if "/Controller/" in file_path and not "/Component/" in file_path:
            # Controller class should end with 'Controller'
            class_match = re.search(r"class\s+(\w+)", content)
            if class_match:
                class_name = class_match.group(1)
                if not class_name.endswith("Controller"):
                    issues.append({
                        "file": rel_path,
                        "type": "naming_convention",
                        "severity": "error",
                        "message": f"Controller class '{class_name}' does not follow CakePHP naming convention. It should end with 'Controller'."
                    })

                # Controller class should be in plural form before 'Controller'
                base_name = class_name.replace("Controller", "")
                if base_name == base_name.rstrip('s'):  # Simple singular check
                    issues.append({
                        "file": rel_path,
                        "type": "naming_convention",
                        "severity": "warning",
                        "message": f"Controller '{class_name}' should be named in plural form (e.g., '{base_name}sController')."
                    })

        # Model checks
        if "/Model/" in file_path and not "/Behavior/" in file_path:
            # Model class should be singular
            class_match = re.search(r"class\s+(\w+)", content)
            if class_match:
                class_name = class_match.group(1)
                if class_name.endswith('s') and not class_name.endswith('Status'):
                    issues.append({
                        "file": rel_path,
                        "type": "naming_convention",
                        "severity": "warning",
                        "message": f"Model class '{class_name}' should be in singular form according to CakePHP conventions."
                    })

        # Function naming conventions
        # Controller action methods should be camelCase
        if "/Controller/" in file_path:
            function_matches = re.finditer(r"public\s+function\s+(\w+)\s*\(", content)
            for match in function_matches:
                function_name = match.group(1)
                if function_name != 'beforeFilter' and function_name != 'afterFilter' and function_name != 'beforeRender':
                    if not function_name[0].islower() or '_' in function_name:
                        issues.append({
                            "file": rel_path,
                            "type": "naming_convention",
                            "severity": "warning",
                            "message": f"Action method '{function_name}' should use camelCase naming convention."
                        })

        return issues

    def check_deprecated_features(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for usage of deprecated methods and features

        Args:
            file_path: Path to the file being analyzed
            content: Content of the file

        Returns:
            List of deprecated feature issues
        """
        issues = []
        rel_path = os.path.relpath(file_path, self.project_path)

        for deprecated, alternative in self.deprecated_methods.items():
            matches = re.finditer(re.escape(deprecated), content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "file": rel_path,
                    "line": line_num,
                    "type": "deprecated_feature",
                    "severity": "warning",
                    "message": f"Deprecated feature '{deprecated}' used. Consider using '{alternative}' instead."
                })

        # Check for specific patterns indicating deprecated usage
        if re.search(r"App::uses\s*\(\s*['\"]Controller['\"]", content):
            line_num = content.find("App::uses") + 1
            issues.append({
                "file": rel_path,
                "line": line_num,
                "type": "deprecated_feature",
                "severity": "warning",
                "message": "App::uses() for loading controllers is deprecated. CakePHP 2.10 uses autoloading."
            })

        return issues

    def check_security_issues(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities in the code

        Args:
            file_path: Path to the file being analyzed
            content: Content of the file

        Returns:
            List of security issue dictionaries
        """
        issues = []
        rel_path = os.path.relpath(file_path, self.project_path)

        # Check for SQL injection vulnerabilities
        for pattern in self.security_patterns["sql_injection"]:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "file": rel_path,
                    "line": line_num,
                    "type": "security_risk",
                    "severity": "critical",
                    "message": "Potential SQL injection risk. Use parameterized queries with bound parameters instead of string concatenation."
                })

        # Check for XSS vulnerabilities
        if file_path.endswith(".ctp") or "/View/" in file_path:
            for pattern in self.security_patterns["xss"]:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "file": rel_path,
                        "line": line_num,
                        "type": "security_risk",
                        "severity": "high",
                        "message": "Potential XSS vulnerability. Use h() function or echo $this->Html->... to properly escape output."
                    })

        # Check for CSRF protection issues
        for pattern in self.security_patterns["csrf"]:
            if re.search(pattern, content):
                issues.append({
                    "file": rel_path,
                    "type": "security_risk",
                    "severity": "high",
                    "message": "CSRF protection is disabled. Consider enabling CSRF protection in SecurityComponent."
                })

        # Check if Security component is used in controllers
        if "/Controller/" in file_path and not "/Component/" in file_path:
            if not re.search(r"public\s+\$components\s*=.*Security", content):
                issues.append({
                    "file": rel_path,
                    "type": "security_risk",
                    "severity": "medium",
                    "message": "SecurityComponent not used. Consider adding Security component for CSRF protection and form tampering prevention."
                })

        # Check for mass assignment vulnerabilities
        for pattern in self.security_patterns["mass_assignment"]:
            matches = re.finditer(pattern, content)
            for match in matches:
                if not re.search(r"->save\(\$this->request->data\s*,\s*['\"]fieldList['\"]", content):
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "file": rel_path,
                        "line": line_num,
                        "type": "security_risk",
                        "severity": "high",
                        "message": "Potential mass assignment vulnerability. Use the fieldList option in save() to specify allowed fields."
                    })

        return issues

    def format_issues_for_output(self) -> Dict[str, Any]:
        """Format issues for output display

        Returns:
            Dictionary with categorized issues
        """
        result = {
            "total_issues": len(self.issues),
            "critical": [],
            "high": [],
            "medium": [],
            "warning": [],
            "info": [],
        }

        for issue in self.issues:
            severity = issue.get("severity", "info")
            if severity == "critical":
                result["critical"].append(issue)
            elif severity == "high":
                result["high"].append(issue)
            elif severity == "medium":
                result["medium"].append(issue)
            elif severity == "warning":
                result["warning"].append(issue)
            else:
                result["info"].append(issue)

        return result

def format_console_output(result: Dict[str, Any]) -> str:
    """Format analysis results for console output

    Args:
        result: Dictionary with categorized issues

    Returns:
        Formatted string for console output
    """
    output = []

    output.append("=" * 80)
    output.append("CakePHP 2.10 Code Analysis Results")
    output.append("=" * 80)
    output.append(f"Total issues found: {result['total_issues']}")
    output.append("")

    if result["critical"]:
        output.append("\033[31m" + "CRITICAL ISSUES:" + "\033[0m")  # Red text
        for issue in result["critical"]:
            file_info = issue["file"]
            if "line" in issue:
                file_info += f":{issue['line']}"
            output.append(f"\033[31m[{issue['type']}]\033[0m {file_info}")
            output.append(f"  {issue['message']}")
            output.append("")

    if result["high"]:
        output.append("\033[33m" + "HIGH SEVERITY ISSUES:" + "\033[0m")  # Yellow text
        for issue in result["high"]:
            file_info = issue["file"]
            if "line" in issue:
                file_info += f":{issue['line']}"
            output.append(f"\033[33m[{issue['type']}]\033[0m {file_info}")
            output.append(f"  {issue['message']}")
            output.append("")

    if result["medium"]:
        output.append("MEDIUM SEVERITY ISSUES:")
        for issue in result["medium"]:
            file_info = issue["file"]
            if "line" in issue:
                file_info += f":{issue['line']}"
            output.append(f"[{issue['type']}] {file_info}")
            output.append(f"  {issue['message']}")
            output.append("")

    if result["warning"]:
        output.append("WARNINGS:")
        for issue in result["warning"]:
            file_info = issue["file"]
            if "line" in issue:
                file_info += f":{issue['line']}"
            output.append(f"[{issue['type']}] {file_info}")
            output.append(f"  {issue['message']}")
            output.append("")

    return "\n".join(output)

def analyze_cakephp(
    project_path: str,
    output_format: str = "console"
) -> Optional[Dict[str, Any]]:
    """Analyze a CakePHP 2.10 project

    Args:
        project_path: Path to the CakePHP project to analyze
        output_format: Format for output (console, json, or returning results)

    Returns:
        Analysis results as a dictionary if output_format is None, otherwise None
    """
    analyzer = CakePHP210Analyzer(project_path)
    analyzer.analyze_project()

    result = analyzer.format_issues_for_output()

    if output_format == "console":
        print(format_console_output(result))
        return None
    elif output_format == "json":
        import json
        print(json.dumps(result, indent=2))
        return None
    else:
        return result

def main():
    """Main function to run the analyzer from command line"""
    parser = argparse.ArgumentParser(description="CakePHP 2.10 Code Analyzer")
    parser.add_argument("project_path", help="Path to the CakePHP project to analyze")
    parser.add_argument("--output", "-o", default="console", choices=["console", "json"], help="Output format")
    args = parser.parse_args()

    analyze_cakephp(args.project_path, args.output)

if __name__ == "__main__":
    main()
