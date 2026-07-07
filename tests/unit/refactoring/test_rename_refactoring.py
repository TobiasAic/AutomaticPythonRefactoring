from refactoring.rename_refactoring import RenameRefactoring
from tests.unit.refactoring.shared import example_code_file, compare_files
from refactoring.rename_shared import RenameArguments

def test_rename_local_variable(example_code_file):
    refactoring = RenameRefactoring(
        filepath=example_code_file,
        refactoring_arguments=RenameArguments(
            line_number=60,
            old_name="user",
            new_name="renamed_user"
        )
    )
    refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/renamed_user.py")
    refactoring.revert()

def test_rename_attribute(example_code_file):
    refactoring = RenameRefactoring(
        filepath=example_code_file,
        refactoring_arguments=RenameArguments(
            line_number=19,
            old_name="base_dir",
            new_name="renamed_attribute"
        )
    )
    refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/renamed_attribute.py")
    refactoring.revert()