from refactoring.extract_method_refactoring import (
    ExtractMethodArguments,
    ExtractMethodRefactoring,
)
from tests.unit.refactoring.shared import example_code_file_path, read_file


def test_extract_method_refactoring():
    original_code = read_file(example_code_file_path)
    extract_method_refactoring = ExtractMethodRefactoring(original_code, refactoring_arguments=ExtractMethodArguments(start_line=45, end_line=47, new_name="extracted_method"))
    expected_code = read_file("tests/test_files/extracted_method.py")
    assert extract_method_refactoring.new_code == expected_code