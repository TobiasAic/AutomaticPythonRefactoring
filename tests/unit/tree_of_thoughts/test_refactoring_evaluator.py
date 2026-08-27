# AI-generated

import json

from llm.llm_types import LLMResponse
from refactoring.refactoring import Refactoring
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator


class ScriptedLLM:
    def __init__(self, response=None, responses=None):
        self._response = response
        self._responses = responses

    def generate(self, prompt):
        return self._response

    def batch_generate(self, prompts):
        return self._responses


VALID_JSON = json.dumps({"commit_message": "fix: improve naming", "correct": True, "grade": 2})


def test_evaluate_extracts_evaluation_from_plain_json_response():
    evaluator = RefactoringEvaluator(ScriptedLLM(response=LLMResponse(text=VALID_JSON)))
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    evaluation = evaluator.evaluate(refactoring)

    assert evaluation.description == "fix: improve naming"
    assert evaluation.correct is True
    assert evaluation.grade == 2


def test_evaluate_extracts_evaluation_from_response_wrapped_in_markdown_fence():
    wrapped = f"Here is the evaluation:\n```json\n{VALID_JSON}\n```\nThanks."
    evaluator = RefactoringEvaluator(ScriptedLLM(response=LLMResponse(text=wrapped)))
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    evaluation = evaluator.evaluate(refactoring)

    assert evaluation.grade == 2


def test_evaluate_returns_none_when_response_has_no_text():
    evaluator = RefactoringEvaluator(ScriptedLLM(response=LLMResponse(text=None)))
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    assert evaluator.evaluate(refactoring) is None


def test_evaluate_returns_none_when_response_is_not_valid_json():
    evaluator = RefactoringEvaluator(ScriptedLLM(response=LLMResponse(text="not json")))
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    assert evaluator.evaluate(refactoring) is None


def test_evaluate_returns_none_when_json_is_missing_required_fields():
    incomplete = json.dumps({"commit_message": "fix: improve naming"})
    evaluator = RefactoringEvaluator(ScriptedLLM(response=LLMResponse(text=incomplete)))
    refactoring = Refactoring("a = 1\n", "a = 2\n")

    assert evaluator.evaluate(refactoring) is None


def test_batch_evaluate_sets_evaluation_on_each_refactoring():
    responses = [LLMResponse(text=VALID_JSON), LLMResponse(text=VALID_JSON)]
    evaluator = RefactoringEvaluator(ScriptedLLM(responses=responses))
    refactorings = [Refactoring("a = 1\n", "a = 2\n"), Refactoring("b = 1\n", "b = 2\n")]

    evaluator.batch_evaluate(refactorings)

    assert all(refactoring.evaluation is not None for refactoring in refactorings)
    assert refactorings[0].evaluation.grade == 2


def test_batch_evaluate_leaves_evaluation_unset_for_invalid_responses():
    responses = [LLMResponse(text="not json"), LLMResponse(text=VALID_JSON)]
    evaluator = RefactoringEvaluator(ScriptedLLM(responses=responses))
    refactorings = [Refactoring("a = 1\n", "a = 2\n"), Refactoring("b = 1\n", "b = 2\n")]

    evaluator.batch_evaluate(refactorings)

    assert refactorings[0].evaluation is None
    assert refactorings[1].evaluation.grade == 2
