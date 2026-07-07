from refactoring.multi_rename_refactoring import MultiRenameRefactoring, RenameArguments
from tests.unit.refactoring.shared import example_code_file, compare_files

def test_multi_rename_refactoring(example_code_file):
    renames = [
        RenameArguments(line_number=19, old_name='base_dir', new_name='new_dir'),
        RenameArguments(line_number=44, old_name='progress', new_name='new_progress'),
        RenameArguments(line_number=11, old_name='done', new_name='new_done'),
    ]

    refactoring = MultiRenameRefactoring(example_code_file, renames)

    refactoring.execute()
    assert compare_files(example_code_file, "tests/test_files/multi_rename.py")
    refactoring.revert()
    
