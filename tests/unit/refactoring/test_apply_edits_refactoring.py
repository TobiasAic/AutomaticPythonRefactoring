import pytest

from refactoring.apply_edits_refactoring import ApplyEditsRefactoring, EditArguments


def test_apply_edits_refactoring():
    original_code = "def foo():\n    x = 1\n    return x\n"
    edits = [EditArguments(old_code="x = 1", new_code="x = 2")]

    refactoring = ApplyEditsRefactoring(original_code, edits)

    assert refactoring.new_code == "def foo():\n    x = 2\n    return x\n"


def test_apply_edits_refactoring_multiple_edits():
    original_code = "a = 1\nb = 2\n"
    edits = [
        EditArguments(old_code="a = 1", new_code="a = 10"),
        EditArguments(old_code="b = 2", new_code="b = 20"),
    ]

    refactoring = ApplyEditsRefactoring(original_code, edits)

    assert refactoring.new_code == "a = 10\nb = 20\n"


def test_apply_edits_refactoring_rejects_non_unique_old_code():
    original_code = "x = 1\nx = 1\n"
    edits = [EditArguments(old_code="x = 1", new_code="x = 2")]

    with pytest.raises(ValueError):
        ApplyEditsRefactoring(original_code, edits)


def test_apply_edits_refactoring_rejects_missing_old_code():
    original_code = "x = 1\n"
    edits = [EditArguments(old_code="y = 1", new_code="y = 2")]

    with pytest.raises(ValueError):
        ApplyEditsRefactoring(original_code, edits)
