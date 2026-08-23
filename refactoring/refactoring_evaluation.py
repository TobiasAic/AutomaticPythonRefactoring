from dataclasses import dataclass


@dataclass
class RefactoringEvaluation:
    """ Represents the evaluation given by the LLM for a refactoring operation. """
    description: str
    correct: bool
    grade: int

    def __post_init__(self):
        """ Ensure that the grade is an integer between 1 and 5."""
        if not (1 <= self.grade <= 5):
            raise ValueError("Grade must be an integer between 1 and 5.")

    def sorting_value(self) -> int:
        """ Sort incorrect evaluations to the end of the list, and correct evaluations by their grade. """
        if not self.correct:
            return -1
        return self.grade
    
    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "correct": self.correct,
            "grade": self.grade
        }

    @classmethod 
    def from_dict(cls, data: dict) -> 'RefactoringEvaluation':
        return cls(
            description=data["description"],
            correct=data["correct"],
            grade=data["grade"]
        )