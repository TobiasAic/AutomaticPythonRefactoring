import pytest

from tree_of_thoughts.refactoring_category import (
    CONDITIONAL_LOGIC,
    RefactoringCategory,
)
from tree_of_thoughts.refactoring_generator import RefactoringGenerator


def test_refactoring_categories_are_instances():
    assert isinstance(CONDITIONAL_LOGIC, RefactoringCategory)
    assert CONDITIONAL_LOGIC.get_name() == "CONDITIONAL_LOGIC"


def test_python_code_extraction():
    python_code = """
    def example():
        print("This is the refactored code.")
    """

    response = f"""
    Here is the refactored code:

    ```python
    {python_code}
    ```

    Let me know if you need any further changes.
    """

    generator = RefactoringGenerator(None)  # This test does not require setting the LLM 
    extracted_code = generator.extract_python_code(response)
    assert extracted_code == python_code.strip()

def test_failed_python_code_extraction():
    response = """
    Here is the refactored code without proper markers:

    ```python
    def example():
        print("This code is not wrapped in markdown markers.")

    Let me know if you need any further changes.
    """

    generator = RefactoringGenerator(None)  # This test does not require setting the LLM 
    with pytest.raises(ValueError):
        generator.extract_python_code(response)