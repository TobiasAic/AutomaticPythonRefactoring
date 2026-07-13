from abc import ABC, abstractmethod

class Tester(ABC):
    @abstractmethod
    def test_before(self) -> str:
        pass

    @abstractmethod
    def test_changed(self) -> bool:
        pass
