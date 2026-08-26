from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from refactoring_system import RefactoringSystem


def make_system() -> RefactoringSystem:
    """Build a RefactoringSystem instance without running __init__, since the
    methods under test here are pure and don't touch any instance state that
    __init__ would normally set up (git repo, LLM, config, ...)."""
    return RefactoringSystem.__new__(RefactoringSystem)


def make_refactoring(correct: bool, grade: int, compiles: bool = True, tests_changed: bool = False) -> Refactoring:
    refactoring = Refactoring("old", "new")
    refactoring.set_evaluation(RefactoringEvaluation(description="desc", correct=correct, grade=grade))
    refactoring.set_compiles(compiles)
    refactoring.set_tests_changed(tests_changed)
    return refactoring


def test_format_timespan_formats_seconds_as_h_mm_ss():
    system = make_system()

    assert system.format_timespan(3725) == "1:02:05"


def test_is_valid_refactoring_requires_correct_positive_grade_compiling_and_unchanged_tests():
    system = make_system()

    assert system.is_valid_refactoring(make_refactoring(correct=True, grade=1)) is True


def test_is_valid_refactoring_rejects_incorrect_refactoring():
    system = make_system()

    assert system.is_valid_refactoring(make_refactoring(correct=False, grade=1)) is False


def test_is_valid_refactoring_rejects_non_positive_grade():
    system = make_system()

    assert system.is_valid_refactoring(make_refactoring(correct=True, grade=0)) is False


def test_is_valid_refactoring_rejects_non_compiling_code():
    system = make_system()

    assert system.is_valid_refactoring(make_refactoring(correct=True, grade=1, compiles=False)) is False


def test_is_valid_refactoring_rejects_when_tests_changed():
    system = make_system()

    assert system.is_valid_refactoring(make_refactoring(correct=True, grade=1, tests_changed=True)) is False


def test_is_valid_refactoring_rejects_refactoring_without_evaluation():
    system = make_system()

    assert not system.is_valid_refactoring(Refactoring("old", "new"))


def test_sort_refactorings_by_evaluation_orders_by_grade_descending():
    system = make_system()
    low = make_refactoring(correct=True, grade=1)
    high = make_refactoring(correct=True, grade=3)
    mid = make_refactoring(correct=True, grade=2)

    sorted_refactorings = system.sort_refactorings_by_evaluation([low, high, mid])

    assert sorted_refactorings == [high, mid, low]


def test_sort_refactorings_by_evaluation_sorts_incorrect_and_unevaluated_last():
    system = make_system()
    valid = make_refactoring(correct=True, grade=1)
    incorrect = make_refactoring(correct=False, grade=3)
    unevaluated = Refactoring("old", "new")

    sorted_refactorings = system.sort_refactorings_by_evaluation([incorrect, valid, unevaluated])

    assert sorted_refactorings[0] is valid
    assert set(sorted_refactorings[1:]) == {incorrect, unevaluated}


def test_filter_refactorings_keeps_only_valid_refactorings():
    system = make_system()
    valid = make_refactoring(correct=True, grade=1)
    invalid = make_refactoring(correct=False, grade=1)

    filtered = system.filter_refactorings([valid, invalid])

    assert filtered == [valid]


def test_refactoring_printable_string_reports_missing_evaluation():
    system = make_system()
    refactoring = Refactoring("old", "new")

    result = system.refactoring_printable_string(refactoring)

    assert result == "no evaluation, no tool"


def test_refactoring_printable_string_reports_evaluated_refactoring():
    system = make_system()
    refactoring = make_refactoring(correct=True, grade=2)

    result = system.refactoring_printable_string(refactoring)

    assert result == "Correct, 2, desc, no tool"


def test_refactoring_printable_string_uses_only_first_line_of_description():
    system = make_system()
    refactoring = Refactoring("old", "new")
    refactoring.set_evaluation(RefactoringEvaluation(description="first line\nsecond line", correct=False, grade=-1))

    result = system.refactoring_printable_string(refactoring)

    assert result == "Incorrect, -1, first line, no tool"
