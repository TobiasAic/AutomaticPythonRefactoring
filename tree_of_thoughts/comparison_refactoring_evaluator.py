import json

from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from llm.openai_llm import OpenAILLM
from llm.llm_types import LLMResponse
from utility.cli import CLI
from utility.readability_analyzer import ReadabilityAnalyzer

class ComparisonRefactoringEvaluator:
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

    def __init__(self, llm: OpenAILLM):
        self.llm = llm

    def batch_evaluate(self, refactorings: list[Refactoring]):
        metric_improvements = [self.get_metrics(refactoring) for refactoring in refactorings]
        refactorings_with_ids = [{"refactoring_id": i, "refactoring": refactoring} for i, refactoring in enumerate(refactorings)]
        refactoring_dict = [{"refactoring_id": i,"diff": refactoring.get_diff(), "metrics": metric} for i, (refactoring, metric) in enumerate(zip(refactorings, metric_improvements))]
        conventional_commits_specification = self.load_md_as_string("tree_of_thoughts/conventional_commits_specification.md")

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
        
    def get_metrics(self, refactoring: Refactoring) -> str:
        try: 
            metrics_before = ReadabilityAnalyzer.analyze_code(refactoring.old_code)
            metrics_after = ReadabilityAnalyzer.analyze_code(refactoring.new_code)
            metric_improvements = metrics_before.get_string_improvements(metrics_after)
        except Exception as e:
            metric_improvements = f"Failed to analyze metrics. There might be an issue with the code. Error: {e}"
        return metric_improvements

    def extract_evaluations(self, llm_response: LLMResponse) -> dict[int, RefactoringEvaluation]:
        try:
            if llm_response.text is None:
                raise ValueError("LLM response does not contain text content.")
            if "```json" in llm_response.text:
                start_index = llm_response.text.index("```json") + len("```json")
                end_index = llm_response.text.index("```", start_index)
                json_content = llm_response.text[start_index:end_index].strip()
            else:
                json_content = llm_response.text.strip()
            data = json.loads(json_content)
        except json.JSONDecodeError:
            raise ValueError("LLM response is not a valid JSON object.")

        result = {}
        for item in data:
            if not all(key in item for key in ["refactoring_id", "commit_message", "correct", "grade"]):
                raise ValueError("LLM response JSON object is missing required fields.")
            result[item["refactoring_id"]] = RefactoringEvaluation(
                description=item["commit_message"],
                correct=item["correct"],
                grade=item["grade"]
            )
        
        return result
    
    def load_md_as_string(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()