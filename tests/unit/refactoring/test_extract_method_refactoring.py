from refactoring.extract_method_refactoring import (
    ExtractMethodArguments,
    ExtractMethodRefactoring,
)
from tests.unit.refactoring.shared import example_code_file_path, read_file


def test_extract_method_refactoring():
    original_code = read_file(example_code_file_path)
    code_to_extract = (
        '\tprint(f"User: {user_name}")\n'
        '\tprint(f"Tasks: {len(tasks)}")\n'
        '\tprint(f"Progress: {progress:.0%}")\n'
    )
    extract_method_refactoring = ExtractMethodRefactoring(original_code, refactoring_arguments=ExtractMethodArguments(code_to_extract=code_to_extract, new_name="extracted_method"))
    expected_code = read_file("tests/test_files/extracted_method.py")
    assert extract_method_refactoring.new_code == expected_code