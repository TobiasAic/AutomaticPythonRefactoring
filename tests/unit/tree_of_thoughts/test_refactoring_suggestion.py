# AI-generated

from tree_of_thoughts.refactoring_suggestion import (
    ExtractFunction,
    RefactoringSuggestion,
    RemoveDeadCode,
)


def test_get_description_includes_name_and_examples():
    suggestion = RefactoringSuggestion(
        name="My Suggestion",
        example_before="before_code()",
        example_after="after_code()",
        notes="Some notes.",
    )

    description = suggestion.get_description()

    assert "My Suggestion" in description
    assert "before_code()" in description
    assert "after_code()" in description
    assert "Some notes." in description


def test_get_description_omits_empty_notes_section_content():
    description = RemoveDeadCode.get_description()

    assert "Remove Dead Code" in description
    assert "Example before:" in description
    assert "Example after:" in description


def test_extract_function_notes_reference_the_provided_tool():
    assert "tool" in ExtractFunction.notes.lower()
