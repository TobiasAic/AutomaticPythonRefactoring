from refactoring.rename_refactoring import RenameRefactoring
from refactoring.rename_shared import RenameArguments
from tests.unit.refactoring.shared import example_code_file_path, read_file


def test_rename_local_variable():
    original_code = read_file(example_code_file_path)
    refactoring = RenameRefactoring(
        original_code,
        refactoring_arguments=RenameArguments(
            line_number=60,
            old_name="user",
            new_name="renamed_user"
        )
    )
    expected_code = read_file("tests/test_files/renamed_user.py")
    assert refactoring.new_code == expected_code

def test_rename_attribute():
    original_code = read_file(example_code_file_path)
    refactoring = RenameRefactoring(
        original_code,
        refactoring_arguments=RenameArguments(
            line_number=19,
            old_name="base_dir",
            new_name="renamed_attribute"
        )
    )
    expected_code = read_file("tests/test_files/renamed_attribute.py")
    assert refactoring.new_code == expected_code