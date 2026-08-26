import json

from llm.llm_types import LLMResponse
from llm.openai_llm import OpenAILLM
from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from tree_of_thoughts.conventional_commits_specification import (
    conventional_commits_specification,
)
from utility.cli import CLI


class RefactoringEvaluator:
    prompt = """
    Your job is to review a refactoring of a piece of Python code based on the code diff provided.
    Your answer must be a JSON object with the following format:
    {{
        "commit_message": "A fitting commit message describing the refactoring",
        "correct": true/false,
        "grade": 1-5,
    }}

    The commit message should adhere to the Conventional Commits specification with a few additions as provided here:
    {conventional_commits_specification}

    The correct field should only be true if the refactoring does not alter the behavior of the code.
    The grade should be an integer between 1 and 5, where 1 indicates a poor refactoring that does not improve code quality, and 5 indicates an excellent refactoring that significantly enhances code quality.

    Here is the diff of the refactoring to review:
    {diff}
    """

    def __init__(self, llm: OpenAILLM):
        self.llm = llm

    def evaluate(self, refactoring: Refactoring) -> RefactoringEvaluation | None:
        """Generate an evaluation for a single refactoring. If the evaluation fails None is returned.

        Args:
            refactoring (Refactoring): The refactoring to evaluate.

        Returns:
            RefactoringEvaluation | None: The evaluation of the refactoring.
        """
        prompt = RefactoringEvaluator.prompt.format(
            diff=refactoring.get_diff(),
            conventional_commits_specification=conventional_commits_specification,
        )
        response = self.llm.generate(prompt)

        try:
            refactoring_evaluation = self.__extract_evaluation(response)
            return refactoring_evaluation
        except ValueError as e:
            CLI.print_error(f"LLM did not return a valid evaluation: {response}")
            return None

    def batch_evaluate(self, refactorings: list[Refactoring]):
        """Generate evaluations for multiple refactorings and set them as the evaluation property of the refactoring.
           If the evaluation fails for a refactoring, the evaluation property is set to None.

        Args:
            refactorings (list[Refactoring]): The list of refactorings to evaluate.
        """
        prompts = []
        for refactoring in refactorings:
            metric_improvements = self.get_metrics(refactoring)

            prompt = RefactoringEvaluator.prompt.format(
                diff=refactoring.get_diff(),
                conventional_commits_specification=conventional_commits_specification,
                metric_improvements=metric_improvements
            )
            prompts.append(prompt)

        llm_responses = self.llm.batch_generate(prompts)

        for refactoring, response in zip(refactorings, llm_responses):
            try:
                refactoring_evaluation = self.__extract_evaluation(response)
                refactoring.evaluation = refactoring_evaluation
            except ValueError as e:
                CLI.print_error(f"LLM did not return a valid evaluation: {response}")

    def __extract_json(self, llm_response: LLMResponse) -> dict:
        """Extract the JSON object from the LLM response.

        Args:
            llm_response (LLMResponse): The response from the LLM containing the JSON object.

        Raises:
            ValueError: If the LLM response does not contain text.
            ValueError: If the LLM response is not a valid JSON object.

        Returns:
            dict: The extracted JSON object.
        """
        if llm_response.text is None:
            raise ValueError("LLM response does not contain text content.")

        if "```json" in llm_response.text:
            json_start = llm_response.text.index("```json") + len("```json")
            json_end = llm_response.text.index("```", json_start)
            json_str = llm_response.text[json_start:json_end].strip()
        else:
            json_str = llm_response.text.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM response is not a valid JSON object. Error: {e}")

    def __extract_evaluation(self, llm_response: LLMResponse) -> RefactoringEvaluation | None:
        """Extract an evaluation from the LLM response.

        Args:
            llm_response (LLMResponse): The response from the LLM containing the evaluation in JSON format.

        Raises:
            ValueError: If the LLM response does not contain text.
            ValueError: If the LLM response is not a valid JSON object.
            ValueError: If the LLM response JSON object is missing required fields.

        Returns:
            RefactoringEvaluation | None: The extracted evaluation or None if the evaluation extraction fails.
        """
        data = self.__extract_json(llm_response)

        if not all(key in data for key in ["commit_message", "correct", "grade"]):
            raise ValueError(
                "LLM response JSON object is missing required fields.")
        return RefactoringEvaluation(
            description=data["commit_message"],
            correct=data["correct"],
            grade=data["grade"]
        )
