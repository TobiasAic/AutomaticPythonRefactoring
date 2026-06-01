import json
from typing import Optional
import logging

from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from llm.llm import LLM

class RefactoringEvaluator:
    prompt = """
    Your job is to review a refactoring of a piece of Python code based on the diff provided. 
    Your answer must be a JSON object with the following format:
    {{
        "description": "A brief description of the refactoring and its impact on code quality.",
        "correct": true/false,
        "grade": 0-10,
    }}

    The description should be a fitting commit message explaining what was refactored.
    The correct field should only be true if the refactoring does not alter the behavior of the code.
    The grade should be an integer between 0 and 10, where 0 indicates a poor refactoring that does not improve code quality, and 10 indicates an excellent refactoring that significantly enhances code quality.

    Here is the diff of the refactoring to review:
    {diff}
    """

    def __init__(self, llm: LLM):
        self.llm = llm

    def evaluate(self, refactoring: Refactoring) -> Optional[RefactoringEvaluation]:
        prompt = RefactoringEvaluator.prompt.format(diff=refactoring.get_diff())
        response = self.llm.generate(prompt)

        try: 
            refactoring_evaluation = self.extract_evaluation(response)
            return refactoring_evaluation
        except ValueError as e:
            logger = logging.getLogger(f"refactoring.{__name__}")
            logger.error(f"LLM did not return a valid evaluation: {response}")
            return None

    def extract_evaluation(self, llm_response: str) -> RefactoringEvaluation:
        try:
            data = json.loads(llm_response)
        except json.JSONDecodeError:
            raise ValueError("LLM response is not a valid JSON object.")

        if not all(key in data for key in ["description", "correct", "grade"]):
            raise ValueError("LLM response JSON object is missing required fields.")

        return RefactoringEvaluation(
            description=data["description"],
            correct=data["correct"],
            grade=data["grade"]
        )