from abc import ABC, abstractmethod
from typing import Self 

class RefactoringTool(ABC):
    @staticmethod
    @abstractmethod
    def get_description() -> dict:
        pass

    @staticmethod
    @abstractmethod
    def call(filepath: str, arguments: dict) -> Self:
        pass
