# AI-generated

import pytest

from refactoring.refactoring_evaluation import RefactoringEvaluation


def test_construction_accepts_grades_in_range():
    evaluation = RefactoringEvaluation(description="Improve naming", correct=True, grade=3)

    assert evaluation.grade == 3


@pytest.mark.parametrize("grade", [-4, 4, 10, -10])
def test_construction_rejects_grades_out_of_range(grade):
    with pytest.raises(ValueError):
        RefactoringEvaluation(description="desc", correct=True, grade=grade)


def test_sorting_value_returns_grade_when_correct():
    evaluation = RefactoringEvaluation(description="desc", correct=True, grade=2)

    assert evaluation.sorting_value() == 2


def test_sorting_value_sorts_incorrect_evaluations_below_any_grade():
    evaluation = RefactoringEvaluation(description="desc", correct=False, grade=-3)

    assert evaluation.sorting_value() == -4


def test_to_dict_and_from_dict_round_trip():
    evaluation = RefactoringEvaluation(description="Rename variable", correct=True, grade=1)

    restored = RefactoringEvaluation.from_dict(evaluation.to_dict())

    assert restored == evaluation
