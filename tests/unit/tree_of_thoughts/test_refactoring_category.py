from tree_of_thoughts.refactoring_category import (
    ALL_CATEGORIES,
    CATEGORIES_BY_NAME,
    CODE_QUALITY,
    CONDITIONAL_LOGIC,
    METHOD_STRUCTURE,
    RefactoringCategory,
)


def test_refactoring_categories_are_instances():
    assert isinstance(CONDITIONAL_LOGIC, RefactoringCategory)
    assert CONDITIONAL_LOGIC.get_name() == "CONDITIONAL_LOGIC"


def test_get_tools_defaults_to_empty_list():
    assert CONDITIONAL_LOGIC.get_tools() == []


def test_get_tools_returns_configured_tools():
    tools = METHOD_STRUCTURE.get_tools()

    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "extract_method"


def test_get_refactoring_suggestions_string_lists_every_suggestion():
    suggestions_string = CONDITIONAL_LOGIC.get_refactoring_suggestions_string()

    for suggestion in CONDITIONAL_LOGIC.get_refactoring_suggestions():
        assert suggestion.name in suggestions_string


def test_get_refactoring_suggestions_string_reports_when_none_are_configured():
    category = RefactoringCategory(name="EMPTY", description="No suggestions here.")

    assert category.get_refactoring_suggestions_string() == "No specific refactoring suggestions provided."


def test_get_prompt_includes_name_description_and_suggestions():
    prompt = CONDITIONAL_LOGIC.get_prompt()

    assert "Category: CONDITIONAL_LOGIC" in prompt
    assert CONDITIONAL_LOGIC.get_description() in prompt
    assert "Decompose Conditional" in prompt


def test_all_categories_are_registered_by_name():
    assert CATEGORIES_BY_NAME == {category.get_name(): category for category in ALL_CATEGORIES}
    assert CATEGORIES_BY_NAME["CODE_QUALITY"] is CODE_QUALITY
