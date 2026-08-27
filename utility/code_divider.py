from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CodeSegment:
    id: int
    code: str


class CodeDivider(ABC):
    @abstractmethod
    def divide(self, code: str) -> list[CodeSegment]:
        """Splits code into an ordered list of segments covering it without gaps or overlap."""
