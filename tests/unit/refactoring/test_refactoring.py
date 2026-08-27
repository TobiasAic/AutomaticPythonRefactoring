# AI-generated

from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from tree_of_thoughts.refactoring_category import CODE_QUALITY
from utility.readability_analyzer import ReadabilityAnalyzer


def test_tool_name_defaults_to_no_tool():
    refactoring = Refactoring("old", "new")

    assert refactoring.tool_name() == "no tool"


def test_get_diff_shows_added_and_removed_lines():
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    diff = refactoring.get_diff()

    assert "-a = 1" in diff
    assert "+a = 2" in diff


def test_get_diff_is_empty_for_identical_code():
    refactoring = Refactoring("a = 1\n", "a = 1\n")

    assert refactoring.get_diff() == ""


def test_get_commit_message_reports_missing_fields_when_unset():
    refactoring = Refactoring("old", "new")

    message = refactoring.get_commit_message()

    assert "Missing evaluation" in message
    assert "Category: Missing category" in message
    assert "Compiles: Missing compilation status" in message
    assert "Tests Changed: Missing test change status" in message
    assert "Missing metrics" in message


def test_get_commit_message_includes_set_fields():
    refactoring = Refactoring("old", "new")
    refactoring.set_evaluation(RefactoringEvaluation(description="Rename variable", correct=True, grade=2))
    refactoring.set_category(CODE_QUALITY)
    refactoring.set_compiles(True)
    refactoring.set_tests_changed(False)

    message = refactoring.get_commit_message()

    assert message.startswith("Rename variable")
    assert "Category: CODE_QUALITY" in message
    assert "Grade: 2" in message
    assert "Correct: True" in message
    assert "Compiles: True" in message
    assert "Tests Changed: False" in message


def test_to_dict_and_from_dict_round_trip_with_all_fields_set():
    refactoring = Refactoring("old", "new")
    refactoring.set_evaluation(RefactoringEvaluation(description="Rename variable", correct=True, grade=2))
    refactoring.set_category(CODE_QUALITY)
    refactoring.set_compiles(True)
    refactoring.set_tests_changed(False)
    refactoring.set_metrics(ReadabilityAnalyzer.analyze_code("x = 1\n"))

    restored = Refactoring.from_dict(refactoring.to_dict())

    assert restored.old_code == refactoring.old_code
    assert restored.new_code == refactoring.new_code
    assert restored.category is CODE_QUALITY
    assert restored.evaluation == refactoring.evaluation
    assert restored.compiles is True
    assert restored.tests_changed is False
    assert restored.metrics == refactoring.metrics


def test_to_dict_and_from_dict_round_trip_with_no_optional_fields_set():
    refactoring = Refactoring("old", "new")

    restored = Refactoring.from_dict(refactoring.to_dict())

    assert restored.old_code == "old"
    assert restored.new_code == "new"
    assert restored.category is None
    assert restored.evaluation is None
    assert restored.compiles is None
    assert restored.tests_changed is None
    assert restored.metrics is None
