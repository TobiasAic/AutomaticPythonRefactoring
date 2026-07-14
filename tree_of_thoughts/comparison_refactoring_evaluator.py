import json
from typing import Optional

from refactoring.refactoring import Refactoring
from utility.cli import CLI
from tree_of_thoughts.conventional_commits_specification import conventional_commits_specification
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from refactoring.refactoring_evaluation import RefactoringEvaluation

class ComparisonRefactoringEvaluator(RefactoringEvaluator):
    prompt = """
    Your job is to review  refactorings on a piece of Python code based on the code diffs provided. 
    Your answer must be a JSON object with the following format:
    [
        {{
            "refactoring_id": 1,
            "commit_message": "A fitting commit message describing the refactoring",
            "correct": true/false,
            "grade": 0-10,
        }},
        {{
            "refactoring_id": 2,
            "commit_message": "A fitting commit message describing the refactoring",
            "correct": true/false,
            "grade": 0-10,
        }},
        ...
    ]

    The commit messages should adhere to the Conventional Commits specification with a few additions as provided here:
    {conventional_commits_specification}

    The correct fields should only be true if the refactoring does not alter the behavior of the code.
    The grades should be an integer between 0 and 10, where 0 indicates a poor refactoring that does not improve code quality, and 10 indicates an excellent refactoring that significantly enhances code quality.

    Review the following {number_of_refactorings} refactorings.
    They contain the ids, code diffs and changes in helpful metrics like the maintainability index.
    Guide your evaluation by the metrics where helpful. 

    {refactorings}
    """

    def evaluate(self, refactoring: Refactoring) -> Optional[RefactoringEvaluation]:
        raise NotImplementedError("This evaluator is designed for batch evaluation of multiple refactorings. Use batch_evaluate instead.")

    def batch_evaluate(self, refactorings: list[Refactoring]):
        metric_improvements = [self.get_metrics(refactoring) for refactoring in refactorings]
        refactorings_with_ids = [{"refactoring_id": i, "refactoring": refactoring} for i, refactoring in enumerate(refactorings)]
        refactoring_dict = [{"refactoring_id": i,"diff": refactoring.get_diff(), "metrics": metric} for i, (refactoring, metric) in enumerate(zip(refactorings, metric_improvements))]

        prompt = ComparisonRefactoringEvaluator.prompt.format(
            number_of_refactorings=len(refactorings),
            refactorings=json.dumps(refactoring_dict),
            conventional_commits_specification=conventional_commits_specification
        )
        response = self.llm.generate(prompt)

        try: 
            refactoring_evaluations = self.extract_evaluations(response)
            for refactoring_with_id in refactorings_with_ids:
                refactorings_with_ids[refactoring_with_id["refactoring_id"]]["refactoring"].evaluation = refactoring_evaluations[refactoring_with_id["refactoring_id"]]
        except ValueError as e:
            CLI.print_error(f"LLM did not return valid evaluations: {response}")