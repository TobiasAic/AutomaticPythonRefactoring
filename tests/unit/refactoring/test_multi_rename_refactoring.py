# AI-generated

import pytest

from refactoring.multi_rename_refactoring import (
    MultiRenameRefactoring,
    MultiRenameTool,
    RenameArguments,
    calculate_offset,
)
from tests.unit.refactoring.shared import example_code_file_path, read_file


def test_multi_rename_refactoring():
    original_code = read_file(example_code_file_path)
    renames = [
        RenameArguments(context_code='self.base_dir = ', old_name='base_dir', new_name='new_dir'),
        RenameArguments(context_code='progress = ', old_name='progress', new_name='new_progress'),
        RenameArguments(context_code='done: bool = False', old_name='done', new_name='new_done'),
    ]

    refactoring = MultiRenameRefactoring(original_code, renames)

    expected_code = read_file("tests/test_files/multi_rename.py")
    assert refactoring.new_code == expected_code


def test_calculate_offset_locates_identifier_within_context():
    code = "x = 1\ny = 2\n"

    offset = calculate_offset(code, "y = 2", "y")

    assert code[offset:].startswith("y = 2")


def test_calculate_offset_rejects_non_unique_context_code():
    code = "y = 2\ny = 2\n"

    with pytest.raises(ValueError, match="context_code"):
        calculate_offset(code, "y = 2", "y")


def test_calculate_offset_rejects_non_unique_identifier_within_context():
    code = "y = y + 1\n"

    with pytest.raises(ValueError, match="old_name"):
        calculate_offset(code, "y = y + 1", "y")


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

    refactoring = MultiRenameTool.call(original_code, arguments)

    expected_code = read_file("tests/test_files/multi_rename.py")
    assert refactoring.new_code == expected_code


def test_call_defaults_to_empty_changes_list_when_missing():
    original_code = read_file(example_code_file_path)

    refactoring = MultiRenameTool.call(original_code, {})

    assert refactoring.new_code == original_code
