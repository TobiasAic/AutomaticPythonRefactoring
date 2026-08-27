import pytest

from refactoring.apply_edits_refactoring import (
    ApplyEditsRefactoring,
    ApplyEditsTool,
    EditArguments,
)
from tests.unit.refactoring.shared import single_segment_code_file


def test_apply_edits_refactoring():
    code_file = single_segment_code_file("def foo():\n    x = 1\n    return x\n")
    edits = [EditArguments(old_code="x = 1", new_code="x = 2")]

    refactoring = ApplyEditsRefactoring(code_file, 0, edits)

    assert refactoring.new_code == "def foo():\n    x = 2\n    return x\n"


def test_apply_edits_refactoring_multiple_edits():
    code_file = single_segment_code_file("a = 1\nb = 2\n")
    edits = [
        EditArguments(old_code="a = 1", new_code="a = 10"),
        EditArguments(old_code="b = 2", new_code="b = 20"),
    ]

    refactoring = ApplyEditsRefactoring(code_file, 0, edits)

    assert refactoring.new_code == "a = 10\nb = 20\n"


def test_apply_edits_refactoring_rejects_non_unique_old_code():
    code_file = single_segment_code_file("x = 1\nx = 1\n")
    edits = [EditArguments(old_code="x = 1", new_code="x = 2")]

    with pytest.raises(ValueError):
        ApplyEditsRefactoring(code_file, 0, edits)


def test_apply_edits_refactoring_rejects_missing_old_code():
    code_file = single_segment_code_file("x = 1\n")
    edits = [EditArguments(old_code="y = 1", new_code="y = 2")]

    with pytest.raises(ValueError):
        ApplyEditsRefactoring(code_file, 0, edits)


def test_get_description_declares_the_apply_edits_function():
    description = ApplyEditsTool.get_description()

    assert description["function"]["name"] == "apply_edits"


def test_call_builds_refactoring_from_standard_field_names():
    code_file = single_segment_code_file("x = 1\n")
    arguments = {"edits": [{"old_code": "x = 1", "new_code": "x = 2"}]}

    refactoring = ApplyEditsTool.call(code_file, 0, arguments)

    assert refactoring.new_code == "x = 2\n"


def test_call_resolves_alternate_field_name_aliases():
    code_file = single_segment_code_file("x = 1\n")
    arguments = {"edits": [{"old_text": "x = 1", "new_str": "x = 2"}]}

    refactoring = ApplyEditsTool.call(code_file, 0, arguments)

    assert refactoring.new_code == "x = 2\n"


def test_call_returns_none_when_edit_does_not_match():
    code_file = single_segment_code_file("x = 1\n")
    arguments = {"edits": [{"old_code": "does_not_exist", "new_code": "x = 2"}]}

    refactoring = ApplyEditsTool.call(code_file, 0, arguments)

    assert refactoring is None


def test_call_defaults_to_empty_edits_list_when_missing():
    code_file = single_segment_code_file("x = 1\n")

    refactoring = ApplyEditsTool.call(code_file, 0, {})

    assert refactoring.new_code == "x = 1\n"
