from dataclasses import dataclass
from enum import Enum

class RefactoringGrade(Enum):
    incorrect = 0
    correct = 1
    useful = 2

@dataclass
class RefactoringEvaluation:
    description: str
    grade: RefactoringGrade