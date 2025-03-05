# CakePHP 2.10 Code Analyzer

This tool provides specialized code analysis for CakePHP 2.10 applications, identifying common issues, security vulnerabilities, and adherence to CakePHP best practices and conventions.

## Features

The CakePHP analyzer focuses on three key areas:

1. **CakePHP Coding Convention Checks**
   - Controller naming (plural + 'Controller' suffix)
   - Model naming (singular form)
   - Method naming conventions (camelCase)
   - File structure conventions

2. **Deprecated Method and Feature Detection**
   - Identifies deprecated CakePHP 2.10 methods and properties
   - Suggests modern alternatives
   - Highlights autoloading issues

3. **Security Risk Identification**
   - SQL Injection vulnerabilities
   - XSS (Cross-Site Scripting) vulnerabilities
   - CSRF (Cross-Site Request Forgery) protection
   - Mass Assignment vulnerabilities
   - Proper output escaping

## Usage

The analyzer can be used in two different ways:

### 1. Standalone CakePHP Analyzer

Run the analyzer directly on a CakePHP project:

```bash
python code_review_assistant/analyze_cakephp.py /path/to/cakephp_project
```

Options:
- `--output`, `-o`: Output format (console, json)
- `--auto-detect`, `-a`: Auto-detect CakePHP project root
- `--version`, `-v`: Show version information

Example with auto-detection:
```bash
python code_review_assistant/analyze_cakephp.py /path/to/some/cakephp_file.php --auto-detect
```

### 2. Integrated with Code Review Tool

The analyzer is also integrated with the main code review system. When you run a code review on a PHP file, the system will automatically detect if it's a CakePHP file and run additional CakePHP-specific analysis:

```bash
python code_review_assistant/code_review.py /path/to/cakephp_file.php
```

CakePHP-specific issues will be included in the review results and passed to the LLM for enhanced CakePHP-aware code reviews.

## Issue Severity Levels

The analyzer categorizes issues by severity:

- **Critical**: Serious security vulnerabilities that should be fixed immediately
- **High**: Security issues or critical standard violations
- **Medium**: Important coding standard violations or potential problems
- **Warning**: Minor issues, conventions, or deprecated feature usage

## Examples

When run on a CakePHP project, the analyzer will produce output like:

```
================================================================================
CakePHP 2.10 Code Analysis Results
================================================================================
Total issues found: 21

CRITICAL ISSUES:
[security_risk] app/Controller/UserController.php:31
  Potential SQL injection risk. Use parameterized queries with bound parameters instead of string concatenation.

HIGH SEVERITY ISSUES:
[security_risk] app/Controller/UserController.php:38
  Potential mass assignment vulnerability. Use the fieldList option in save() to specify allowed fields.

[security_risk] app/View/Users/view.ctp:31
  Potential XSS vulnerability. Use h() function or echo $this->Html->... to properly escape output.

...
```

## Implementation Notes

The analyzer inspects CakePHP project files for:

1. **SQL Injection Vulnerabilities**:
   - Detects non-parameterized queries
   - Identifies string concatenation in SQL queries

2. **XSS Prevention**:
   - Checks for proper use of `h()` function
   - Verifies HTML helper usage for output

3. **Mass Assignment Protection**:
   - Identifies usage of `save()` without fieldList
   - Detects unprotected model saves

4. **CSRF Protection**:
   - Checks for SecurityComponent usage
   - Identifies disabled CSRF protection

## Extending the Analyzer

To add new rules or checks:
1. Add patterns to the appropriate collection in the `CakePHP210Analyzer` class
2. Implement detection logic in the relevant check method
3. Update issue reporting and documentation
