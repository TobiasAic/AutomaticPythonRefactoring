from abc import ABC, abstractmethod
from typing import Optional
import json

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
        pass

    @abstractmethod
    def batch_evaluate(self, refactorings: list[Refactoring]):
        pass

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