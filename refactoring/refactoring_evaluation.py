from dataclasses import dataclass

@dataclass
class RefactoringEvaluation:
    description: str
    correct: bool
    grade: int

    def __post_init__(self):
        if not (0 <= self.grade <= 10):
            raise ValueError("Grade must be an integer between 0 and 10.")
        
    def sorting_value(self) -> int:
        if not self.correct:
            return 0
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