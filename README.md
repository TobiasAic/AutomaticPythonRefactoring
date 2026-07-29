# Automatic Python Refactoring

Automatic Python Refactoring is a Python project for automated code refactoring with Large Language Models (LLMs). It combines LLM-generated refactoring ideas, evaluation, validation through compilation and tests, and readability tracking to help improve code quality iteratively.

## What it does

The system can:

- inspect Python files and generate candidate refactorings
- evaluate those refactorings with an LLM-based scorer
- validate each candidate by compiling the file and rerunning tests
- apply the best refactoring candidate
- record readability metrics and save results for later review

## Project structure

- [main.py](main.py) – CLI entry point for running the tool
- [refactoring_system.py](refactoring_system.py) – orchestrates the refactoring workflow
- [refactoring/](refactoring/) – refactoring implementations and storage logic
- [llm/](llm/) – LLM integrations and prompt handling
- [tree_of_thoughts/](tree_of_thoughts/) – generation and evaluation logic
- [utility/](utility/) – configuration, git handling, testing, and analysis helpers

## Requirements

This project uses Python and the dependencies listed in [requirements.txt](requirements.txt).

Install them with:

```bash
pip install -r requirements.txt
```

## Configuration

The tool expects a TOML configuration file. The config file is resolved relative to the directory that contains it, and the following fields are required:

```toml
target_file_paths = ["src/example.py"]
git_repo_path = "."
branch_name = "automatic-refactor"
pyenv_name = "your-pyenv-name"
test_file_path = "."
max_iterations = 3
statistics_directory = "stats"
show_tree = false
```

### Field descriptions

- `target_file_paths`: list of file paths to refactor, relative to the config file directory
- `git_repo_path`: path to the git repository root
- `branch_name`: name of the branch used for the refactoring run
- `pyenv_name`: Python environment name used by `pyenv` for test execution
- `test_file_path`: relative path to the pytest file to run for validation 
- `max_iterations`: number of refactoring iterations to attempt per file
- `statistics_directory`: directory where readability plots and metrics are written
- `show_tree`: whether to apply all evaluated refactorings or only the best one

## Running the tool

Run the tool with:

```bash
python main.py /path/to/config.toml
```

Example:

```bash
python main.py config.toml
```
