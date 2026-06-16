from refactoring.rename_refactoring import RenameRefactoring
from tests.unit.refactoring.shared import example_code_file, compare_files

def test_rename_local_variable(example_code_file):
    with open(example_code_file, "r") as file:
        original_code = file.read()

    marked_code = insert_marker(original_code, line_number=60, identifier="user")
    offset = marked_code.index("<MARKER>")

    refactoring = RenameRefactoring(
        filepath=example_code_file,
        offset=offset,
        new_name="renamed_user"
    )
    refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/renamed_user.py")
    refactoring.revert()

def test_rename_attribute(example_code_file):
    with open(example_code_file, "r") as file:
        original_code = file.read()

    marked_code = insert_marker(original_code, line_number=19, identifier="base_dir")
    offset = marked_code.index("<MARKER>")

    refactoring = RenameRefactoring(
        filepath=example_code_file,
        offset=offset,
        new_name="renamed_attribute"
    )
    refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/renamed_attribute.py")
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
