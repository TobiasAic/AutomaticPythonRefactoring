from __future__ import annotations

import difflib
import json
from typing import TYPE_CHECKING

from refactoring.refactoring_evaluation import RefactoringEvaluation
from utility.readability_analyzer import ReadabilityMetrics

if TYPE_CHECKING:
    from tree_of_thoughts.refactoring_category import RefactoringCategory


class Refactoring:
    """ Base class representing a refactoring operation."""

    def __init__(self, old_code: str, new_code: str):
        self.old_code = old_code
        self.new_code = new_code
        self.evaluation = None
        self.category: RefactoringCategory = None
        self.compiles: bool = None
        self.tests_changed: bool = None
        self.metrics: ReadabilityMetrics = None

    def get_diff(self) -> str:
        """Returns a unified diff between the old and new code.

        Returns:
            str: A string representing the diff between the old and new code. 
        """
        diff = difflib.unified_diff(
            self.old_code.splitlines(),
            self.new_code.splitlines(),
            fromfile='before refactoring',
            tofile='after refactoring',
            lineterm=''
        )
        return '\n'.join(diff)

    def get_commit_message(self) -> str:
        """Returns the commit message from the evaluation, if available.

        Returns:
            str: The commit message, or None if no evaluation is set.
        """
        description = self.evaluation.description if self.evaluation else "Missing evaluation"
        grade = self.evaluation.grade if self.evaluation else "Missing grade"
        correct = self.evaluation.correct if self.evaluation else "Missing correctness"
        category = self.category.get_name() if self.category else "Missing category"
        tool = self.tool_name()
        compiles = self.compiles if self.compiles is not None else "Missing compilation status"
        tests_changed = self.tests_changed if self.tests_changed is not None else "Missing test change status"
        metrics = self.metrics.to_dict() if self.metrics else "Missing metrics"

        return f"{description}\n\nCategory: {category}\nTool: {tool}\nGrade: {grade}\nCorrect: {correct}\nCompiles: {compiles}\nTests Changed: {tests_changed}\nMetrics:\n{json.dumps(metrics, indent=2)}"

    def to_string(self) -> str:
        tool_name = self.tool_name()

        if not self.evaluation:
            return f"no evaluation, {tool_name}"
        else:
            # Get the first line of the description
            short_description = self.evaluation.description.splitlines()[0]
            correct_string = "Correct" if self.evaluation.correct else "Incorrect"
            return f"{correct_string}, {self.evaluation.grade}, {short_description}, {tool_name}"

    def is_valid(self) -> bool:
        if not self.evaluation: # If this refactoring has not been evaluated its not valid
            return False
        return self.evaluation.correct and self.evaluation.grade > 0 and self.compiles and not self.tests_changed

    def tool_name(self) -> str:
        """ The name of the tool that produced this refactoring, or "no tool" for the free-text path. """
        return "no tool"

    def set_evaluation(self, evaluation: RefactoringEvaluation) -> None:
        """ Set the evaluation for the refactoring. """
        self.evaluation = evaluation

    def set_category(self, category: RefactoringCategory) -> None:
        """ Set the category for the refactoring. """
        self.category = category

    def set_compiles(self, compiles: bool) -> None:
        """ Set whether the refactored code compiles. """
        self.compiles = compiles

    def set_tests_changed(self, tests_changed: bool) -> None:
        """ Set whether the refactored code changes the behavior of any tests. """
        self.tests_changed = tests_changed

    def set_metrics(self, metrics: ReadabilityMetrics) -> None:
        """ Set the readability metrics for the refactored code. """
        self.metrics = metrics

    def to_dict(self) -> dict:
        return {
            "old_code": self.old_code,
            "new_code": self.new_code,
            "category": self.category.get_name() if self.category else None,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "compiles": self.compiles,
            "tests_changed": self.tests_changed,
            "metrics": self.metrics.to_dict() if self.metrics else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Refactoring':
        from tree_of_thoughts.refactoring_category import CATEGORIES_BY_NAME

        refactoring = cls(
            old_code=data["old_code"],
            new_code=data["new_code"]
        )
        if data.get("category"):
            refactoring.category = CATEGORIES_BY_NAME[data["category"]]
        if data.get("evaluation"):
            refactoring.evaluation = RefactoringEvaluation.from_dict(data["evaluation"])
        if data.get("compiles") is not None:
            refactoring.compiles = data["compiles"]
        if data.get("tests_changed") is not None:
            refactoring.tests_changed = data["tests_changed"]
        if data.get("metrics"):
            refactoring.metrics = ReadabilityMetrics.from_dict(data["metrics"])
        return refactoring
