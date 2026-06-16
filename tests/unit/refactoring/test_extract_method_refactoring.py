from refactoring.extract_method_refactoring import ExtractMethodRefactoring, calculate_offset_for_line
from tests.unit.refactoring.shared import example_code_file, compare_files

def test_extract_method_refactoring(example_code_file):
    start_offset = calculate_offset_for_line(example_code_file, 45)
    end_offset = calculate_offset_for_line(example_code_file, 47, include_line=True)
    extract_method_refactoring = ExtractMethodRefactoring(filepath=example_code_file, start_offset=start_offset, end_offset=end_offset, new_method_name="extracted_method")
    extract_method_refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/extracted_method.py")
    extract_method_refactoring.revert()