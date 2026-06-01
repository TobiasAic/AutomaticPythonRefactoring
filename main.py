import argparse
from pathlib import Path
import logging

from refactoring_system import RefactoringSystem
from utility.path_utils import get_filepaths_to_refactor, get_test_filepaths, find_lowest_common_ancestor_path
from logging_setup import setup_logging


if __name__ == '__main__':
    setup_logging(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Automatic Python Refactoring Tool')
    parser.add_argument('path', help='Path to Python file/folder containing Python files/a text file with paths to Python files to refactor')
    parser.add_argument('--branch', help='Name of the branch that will be created for the refactoring changes', default='refactor')
    parser.add_argument('--tests', help='Path to pytest file/folder containing pytest files/a text file with paths to pytest files. If not specified, test files will be searched in the path directory.', default=None)
    args = parser.parse_args()

    path_argument = Path(args.path)
    tests_argument = Path(args.tests) if args.tests else None

    filepaths_to_refactor = get_filepaths_to_refactor(path_argument)
    test_filepaths = get_test_filepaths(tests_argument, path_argument)
    git_repository_path = find_lowest_common_ancestor_path(filepaths_to_refactor + test_filepaths)

    print("Running the refactoring system with the following parameters:")
    print(f"Root Path: {git_repository_path}")
    print(f"Files to Refactor:\n- {'\n- '.join(str(p.relative_to(git_repository_path)) for p in filepaths_to_refactor)}")
    print(f"Test Files:\n- {'\n- '.join(str(p.relative_to(git_repository_path)) for p in test_filepaths)}")

    refactoring_system = RefactoringSystem(git_repository_path, filepaths_to_refactor, test_filepaths, args.branch)
    refactoring_system.run(max_iterations=5)