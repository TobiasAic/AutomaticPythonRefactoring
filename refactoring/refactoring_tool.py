from abc import ABC, abstractmethod
from typing import Self


class RefactoringTool(ABC):
    """ Abstract base class for refactoring tools to be used by an LLM. """
    @staticmethod
    @abstractmethod
    def get_description() -> dict:
        """ Returns the description of the refactoring tool for the LLM. """

    @staticmethod
    @abstractmethod
    def call(code_segment: str, arguments: dict) -> Self:
        """ Calls the refactoring with the given arguments from the LLM. """
