import pytest

from refactoring.extract_method_refactoring import ExtractMethodRefactoring, calculate_offset_for_line
from tests.unit.refactoring.test_rename_refactoring import compare_files

def test_extract_method_refactoring():
    start_offset = calculate_offset_for_line("tests/test_files/example.py", 45)
    end_offset = calculate_offset_for_line("tests/test_files/example.py", 47, include_line=True)
    extract_method_refactoring = ExtractMethodRefactoring(filepath="tests/test_files/example.py", start_offset=start_offset, end_offset=end_offset, new_method_name="extracted_method")
    extract_method_refactoring.execute()
    assert compare_files("tests/test_files/example.py", "tests/test_files/extracted_method.py")
    extract_method_refactoring.revert()