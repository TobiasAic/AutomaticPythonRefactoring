import json
from abc import ABC, abstractmethod
from typing import Optional

from llm.llm_types import LLMResponse
from llm.openai_llm import OpenAILLM
from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from utility.readability_analyzer import ReadabilityAnalyzer


class RefactoringEvaluator(ABC):
    def __init__(self, llm: OpenAILLM):
        self.llm = llm

    @abstractmethod
    def evaluate(self, refactoring: Refactoring) -> Optional[RefactoringEvaluation]:
        """Generate an evaluation for a single refactoring. If the evaluation fails None is returned. 

        Args:
            refactoring (Refactoring): The refactoring to evaluate. 

        Returns:
            Optional[RefactoringEvaluation]: The evaluation of the refactoring.
        """
        pass

    @abstractmethod
    def batch_evaluate(self, refactorings: list[Refactoring]):
        """Generate evaluations for multiple refactorings and set them as the evaluation property of the refactoring.
           If the evaluation fails for a refactoring, the evaluation property is set to None.

        Args:
            refactorings (list[Refactoring]): The list of refactorings to evaluate.
        """
        pass

    def get_metrics(self, refactoring: Refactoring) -> str:
        """Generate a string describing the improvement of code metrics by the refactoring.

        Args:
            refactoring (Refactoring): The refactoring to analyze.

        Returns:
            str: The string describing the improvement of code metrics by the refactoring.
        """
        try: 
            metrics_before = ReadabilityAnalyzer.analyze_code(refactoring.old_code)
            metrics_after = ReadabilityAnalyzer.analyze_code(refactoring.new_code)
            metric_improvements = metrics_before.get_string_improvements(metrics_after)
        except Exception as e:
            metric_improvements = f"Failed to analyze metrics. There might be an issue with the code. Error: {e}"
        return metric_improvements
    
    def extract_json(self, llm_response: LLMResponse) -> dict:
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