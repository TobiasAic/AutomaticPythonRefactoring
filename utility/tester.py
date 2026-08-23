from abc import ABC, abstractmethod


class Tester(ABC):
    @abstractmethod
    def test_before(self) -> str:
        """Run tests and record which passed and which failed.

        Returns:
            str: The summary line of the pytest output.
        """

    @abstractmethod
    def test_changed(self) -> bool:
        """Run tests and check if the same tests pass and fail as recorded.

        Returns:
            bool: True if the test results have changed, False otherwise.
        """
        