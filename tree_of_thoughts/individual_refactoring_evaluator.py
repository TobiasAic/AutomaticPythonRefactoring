import json
from typing import Optional

from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from llm.openai_llm import OpenAILLM
from llm.llm_types import LLMResponse
from utility.cli import CLI
from readability_analyzer import ReadabilityAnalyzer

class IndividualRefactoringEvaluator:
    prompt = """
    Your job is to review a refactoring of a piece of Python code based on the code diff provided. 
    Your answer must be a JSON object with the following format:
    {{
        "commit_message": "A fitting commit message describing the refactoring",
        "correct": true/false,
        "grade": 0-10,
    }}

    The commit message should adhere to the Conventional Commits specification with a few additions as provided here:
    {conventional_commits_specification}

    The correct field should only be true if the refactoring does not alter the behavior of the code.
    The grade should be an integer between 0 and 10, where 0 indicates a poor refactoring that does not improve code quality, and 10 indicates an excellent refactoring that significantly enhances code quality.

    Here are how some metrics changed due to the refactoring:
    {metric_improvements}

    Here is the diff of the refactoring to review:
    {diff}
    """

    def __init__(self, llm: OpenAILLM):
        self.llm = llm

    def evaluate(self, refactoring: Refactoring) -> Optional[RefactoringEvaluation]:
        metric_improvements = self.get_metrics(refactoring)

        conventional_commits_specification = self.load_md_as_string("tree_of_thoughts/conventional_commits_specification.md")
        prompt = IndividualRefactoringEvaluator.prompt.format(
            diff=refactoring.get_diff(),
            conventional_commits_specification=conventional_commits_specification,
            metric_improvements=metric_improvements
        )
        response = self.llm.generate(prompt)

        try: 
            refactoring_evaluation = self.extract_evaluation(response)
            return refactoring_evaluation
        except ValueError as e:
            CLI.print_error(f"LLM did not return a valid evaluation: {response}")
            return None
        
    def batch_evaluate(self, refactorings: list[Refactoring]):
        prompts = []
        for refactoring in refactorings:
            metric_improvements = self.get_metrics(refactoring)

            conventional_commits_specification = self.load_md_as_string("tree_of_thoughts/conventional_commits_specification.md")
            prompt = IndividualRefactoringEvaluator.prompt.format(
                diff=refactoring.get_diff(),
                conventional_commits_specification=conventional_commits_specification,
                metric_improvements=metric_improvements
            )
            prompts.append(prompt)

        llm_responses = self.llm.batch_generate(prompts)

        for refactoring, response in zip(refactorings, llm_responses):
            try: 
                refactoring_evaluation = self.extract_evaluation(response)
                refactoring.evaluation = refactoring_evaluation
            except ValueError as e:
                CLI.print_error(f"LLM did not return a valid evaluation: {response}")

    def get_metrics(self, refactoring: Refactoring) -> str:
        try: 
            metrics_before = ReadabilityAnalyzer.analyze_code(refactoring.old_code)
            metrics_after = ReadabilityAnalyzer.analyze_code(refactoring.new_code)
            metric_improvements = metrics_before.get_string_improvements(metrics_after)
        except Exception as e:
            metric_improvements = f"Failed to analyze metrics. There might be an issue with the code. Error: {e}"
        return metric_improvements

    def extract_evaluation(self, llm_response: LLMResponse) -> RefactoringEvaluation:
        try:
            if llm_response.text is None:
                raise ValueError("LLM response does not contain text content.")
            data = json.loads(llm_response.text)
        except json.JSONDecodeError:
            raise ValueError("LLM response is not a valid JSON object.")

        if not all(key in data for key in ["commit_message", "correct", "grade"]):
            raise ValueError("LLM response JSON object is missing required fields.")

        return RefactoringEvaluation(
            description=data["commit_message"],
            correct=data["correct"],
            grade=data["grade"]
        )
    
    def load_md_as_string(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()