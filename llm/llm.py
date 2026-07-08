from abc import ABC, abstractmethod

from llm.llm_types import LLMResponse

class LLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        pass
    
    @abstractmethod
    def batch_generate(self, prompts: list[str], tools: list[list[dict]] = None) -> list[LLMResponse]:
        pass