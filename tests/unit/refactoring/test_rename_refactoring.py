import pytest

from refactoring.rename_refactoring import RenameRefactoring

def test_rename_local_variable():
    with open("tests/test_files/example.py", "r") as file:
        original_code = file.read()

    marked_code = insert_marker(original_code, line_number=60, identifier="user")
    offset = marked_code.index("<MARKER>")

    refactoring = RenameRefactoring(
        filepath="tests/test_files/example.py",
        offset=offset,
        new_name="renamed_user"
    )
    refactoring.execute()
    assert compare_files("tests/test_files/example.py", "tests/test_files/renamed_user.py")
    refactoring.revert()

def test_rename_attribute():
    with open("tests/test_files/example.py", "r") as file:
        original_code = file.read()

    marked_code = insert_marker(original_code, line_number=19, identifier="base_dir")
    offset = marked_code.index("<MARKER>")

    refactoring = RenameRefactoring(
        filepath="tests/test_files/example.py",
        offset=offset,
        new_name="renamed_attribute"
    )
    refactoring.execute()
    assert compare_files("tests/test_files/example.py", "tests/test_files/renamed_attribute.py")
    refactoring.revert()


def insert_marker(code: str, line_number: int, identifier: str) -> str:
    lines = code.splitlines()
    marked_lines = []
    for i, line in enumerate(lines):
        if i == line_number-1:
            marked_lines.append(line.replace(identifier, f"<MARKER>{identifier}"))
        else:
            marked_lines.append(line)     
    return "\n".join(marked_lines)

def compare_files(file1: str, file2: str) -> bool:
    with open(file1, "r") as f1, open(file2, "r") as f2:
        return f1.read() == f2.read()