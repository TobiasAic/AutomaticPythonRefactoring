from refactoring.extract_method_refactoring import ExtractMethodRefactoring, ExtractMethodArguments
from tests.unit.refactoring.shared import example_code_file, compare_files

def test_extract_method_refactoring(example_code_file):
    extract_method_refactoring = ExtractMethodRefactoring(filepath=example_code_file, refactoring_arguments=ExtractMethodArguments(start_line=45, end_line=47, new_name="extracted_method"))
    extract_method_refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/extracted_method.py")
    extract_method_refactoring.revert()