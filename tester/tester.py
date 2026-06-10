from abc import ABC, abstractmethod
from enum import Enum 

class TestResults(Enum):
    UNCHANGED = "Unchanged"
    CHANGED = "Changed"

class Tester(ABC):
    @abstractmethod
    def test_before(self):
        pass

    @abstractmethod
    def test_changed(self) -> TestResults:
        pass
