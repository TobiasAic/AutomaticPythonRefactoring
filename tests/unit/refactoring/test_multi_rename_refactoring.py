import pytest

from refactoring.multi_rename_refactoring import (
    MultiRenameRefactoring,
    MultiRenameTool,
    RenameArguments,
    calculate_offset,
)
from tests.unit.refactoring.shared import example_code_file_path, read_file, single_segment_code_file


def test_multi_rename_refactoring():
    original_code = read_file(example_code_file_path)
    renames = [
        RenameArguments(context_code='self.base_dir = ', old_name='base_dir', new_name='new_dir'),
        RenameArguments(context_code='progress = ', old_name='progress', new_name='new_progress'),
        RenameArguments(context_code='done: bool = False', old_name='done', new_name='new_done'),
    ]
    code_file = single_segment_code_file(original_code)

    refactoring = MultiRenameRefactoring(code_file, 0, renames)

    expected_code = read_file("tests/test_files/multi_rename.py")
    assert refactoring.new_code == expected_code


def test_calculate_offset_locates_identifier_within_context():
    code_file = single_segment_code_file("x = 1\ny = 2\n")

    offset = calculate_offset(code_file, 0, "y = 2", "y")

    marked_code, _ = code_file.marked_code_and_offset(0)
    assert marked_code[offset:].startswith("y = 2")


def test_calculate_offset_rejects_non_unique_context_code():
    code_file = single_segment_code_file("y = 2\ny = 2\n")

    with pytest.raises(ValueError, match="context_code"):
        calculate_offset(code_file, 0, "y = 2", "y")


def test_calculate_offset_rejects_non_unique_identifier_within_context():
    code_file = single_segment_code_file("y = y + 1\n")

    with pytest.raises(ValueError, match="old_name"):
        calculate_offset(code_file, 0, "y = y + 1", "y")


def test_get_description_declares_the_multi_rename_function():
    description = MultiRenameTool.get_description()

    assert description["function"]["name"] == "multi_rename"


def test_call_builds_refactoring_from_arguments():
    original_code = read_file(example_code_file_path)
    arguments = {
        "changes": [
            {"context_code": "self.base_dir = ", "old_name": "base_dir", "new_name": "new_dir"},
            {"context_code": "progress = ", "old_name": "progress", "new_name": "new_progress"},
            {"context_code": "done: bool = False", "old_name": "done", "new_name": "new_done"},
        ]
    }
    code_file = single_segment_code_file(original_code)

    refactoring = MultiRenameTool.call(code_file, 0, arguments)

    expected_code = read_file("tests/test_files/multi_rename.py")
    assert refactoring.new_code == expected_code


def test_call_defaults_to_empty_changes_list_when_missing():
    original_code = read_file(example_code_file_path)
    code_file = single_segment_code_file(original_code)

    refactoring = MultiRenameTool.call(code_file, 0, {})

    assert refactoring.new_code == original_code
