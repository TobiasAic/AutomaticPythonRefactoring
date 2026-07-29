from refactoring.multi_rename_refactoring import MultiRenameRefactoring, RenameArguments
from tests.unit.refactoring.shared import example_code_file_path, read_file


def test_multi_rename_refactoring():
    original_code = read_file(example_code_file_path)
    renames = [
        RenameArguments(line_number=19, old_name='base_dir', new_name='new_dir'),
        RenameArguments(line_number=44, old_name='progress', new_name='new_progress'),
        RenameArguments(line_number=11, old_name='done', new_name='new_done'),
    ]

    refactoring = MultiRenameRefactoring(original_code, renames)

    expected_code = read_file("tests/test_files/multi_rename.py")
    assert refactoring.new_code == expected_code 
