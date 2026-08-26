from tree_of_thoughts.refactoring_category import (
    CONDITIONAL_LOGIC,
    RefactoringCategory,
)


def test_refactoring_categories_are_instances():
    assert isinstance(CONDITIONAL_LOGIC, RefactoringCategory)
    assert CONDITIONAL_LOGIC.get_name() == "CONDITIONAL_LOGIC"