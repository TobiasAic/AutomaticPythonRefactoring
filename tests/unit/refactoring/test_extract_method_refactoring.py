from refactoring.extract_method_refactoring import (
    ExtractMethodArguments,
    ExtractMethodRefactoring,
    ExtractMethodTool,
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


def test_get_description_declares_the_extract_method_function():
    description = ExtractMethodTool.get_description()

    assert description["function"]["name"] == "extract_method"


def test_call_builds_refactoring_from_arguments():
    original_code = read_file(example_code_file_path)
    code_to_extract = (
        '\tprint(f"User: {user_name}")\n'
        '\tprint(f"Tasks: {len(tasks)}")\n'
        '\tprint(f"Progress: {progress:.0%}")\n'
    )
    arguments = {"code_to_extract": code_to_extract, "new_name": "extracted_method"}

    refactoring = ExtractMethodTool.call(original_code, arguments)

    expected_code = read_file("tests/test_files/extracted_method.py")
    assert refactoring.new_code == expected_code


def test_call_returns_none_when_code_to_extract_does_not_match():
    original_code = read_file(example_code_file_path)
    arguments = {"code_to_extract": "not_present_in_file()", "new_name": "extracted_method"}

    refactoring = ExtractMethodTool.call(original_code, arguments)

    assert refactoring is None