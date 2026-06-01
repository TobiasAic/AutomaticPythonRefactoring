import os
from pathlib import Path
import subprocess

def get_filepaths_to_refactor(path_argument: Path) -> list[Path]:
    if path_argument.is_file():
        if path_argument.suffix == '.py': # user gave a single .py file
            return [path_argument]
        elif path_argument.suffix == '.txt': # user gave a text file with paths to .py files
            return extract_filepaths_from_txt(path_argument)
    elif path_argument.is_dir(): # user gave a directory, find all .py files in the directory and subdirectories
        return find_python_files_in_dir(path_argument)

def get_test_filepaths(tests_argument: Path, path_argument: Path) -> list[Path]:
    if not tests_argument: # no test path provided, search for test files in the same directory as the files to refactor
        if path_argument.is_file():
            return  []
        else:
            return find_python_files_in_dir(path_argument)

    if tests_argument.is_file():
        if tests_argument.suffix == '.py': # user gave a single pytest file
            return [tests_argument]
        elif tests_argument.suffix == '.txt': # user gave a text file with paths to pytest files
            return extract_filepaths_from_txt(tests_argument)
    elif tests_argument.is_dir(): # user gave a directory, find all pytest files in the directory and subdirectories
        return find_python_files_in_dir(tests_argument)

def find_lowest_common_ancestor_path(paths: list[Path]) -> Path:
    """ Finds the lowest common ancestor directory path for a list of file paths. """
    string_paths = [str(path) for path in paths]
    common_path = Path(os.path.commonpath(string_paths))
    if common_path.is_file():
        common_path = common_path.parent
    return common_path

def extract_filepaths_from_txt(txt_path: Path) -> list[Path]:
    """ Extracts file paths from a text file, where each line is expected to be a path to a .py file. """
    filepaths = []
    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith('.py'):
                filepaths.append(Path(line))
            else:
                raise ValueError(f"Invalid file path in text file: {line}. Only .py files are allowed.")
    return filepaths

def find_python_files_in_dir(dir_path: Path) -> list[Path]:
    """ Recursively finds all .py files in a directory and its subdirectories. """
    filepaths = []
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if filename.endswith('.py'):
                filepaths.append(Path(root) / filename)
    return filepaths

def find_pytest_files_in_dir(dir_path: Path) -> list[Path]:
    collected_pytests = subprocess.run(['pytest', '--collect-only', '-qq', str(dir_path)], capture_output=True, text=True)
    print(f"Collected pytest files:\n{collected_pytests.stdout}")
    pytest_filepaths = []
    for line in collected_pytests.stdout.splitlines():
        relative_path = line.split(':')[0].strip()
        absolute_path = os.path.join(dir_path, relative_path)
        pytest_filepaths.append(Path(absolute_path))
    return pytest_filepaths

if __name__ == "__main__":
    path = Path("/home/tobias/Desktop/code_repositories/abgabenchecker/docker-controller")
    print(find_pytest_files_in_dir(path))