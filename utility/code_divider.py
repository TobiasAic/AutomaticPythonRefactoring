from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CodeSegment:
    id: int
    code: str


class CodeDivider(ABC):
    @abstractmethod
    def get_segments(self) -> list[CodeSegment]:
        """Returns a list of code segments."""

    @abstractmethod
    def get_number_of_segments(self) -> int:
        """Returns the number of code segments."""

    @abstractmethod
    def get_code(self) -> str:
        """ Returns the complete code reconstructed from the segments. """

    @abstractmethod
    def replace_segment(self, new_segment: CodeSegment, remember: bool = True) -> str:
        """Replaces a code segment at the specified index with a new segment and returns the complete code.

        Args:
            new_segment: A segment object containing the segment ID to replace and the new code.
            remember: If True, persist the replacement in self.segments.

        Returns:
            The complete code reconstructed from the updated segments.
        """

    @abstractmethod
    def print_segment_lengths(self):
        """Prints the lengths of each code segment."""

    @abstractmethod
    def show_segments(self, filepath: str):
        """Save a copy of the file with the segments indicated by ---

        Args:
            filepath: The path to the file where the segments will be saved.
        """
