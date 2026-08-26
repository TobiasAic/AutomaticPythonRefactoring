import difflib

from refactoring.refactoring_evaluation import RefactoringEvaluation


class Refactoring:
    """ Base class representing a refactoring operation."""
    def __init__(self, old_code: str, new_code: str):
        self.old_code = old_code
        self.new_code = new_code
        self.evaluation = None

    def get_diff(self) -> str:
        """Returns a unified diff between the old and new code.

        Returns:
            str: A string representing the diff between the old and new code. 
        """        
        diff = difflib.unified_diff(
            self.old_code.splitlines(),
            self.new_code.splitlines(),
            fromfile='before refactoring',
            tofile='after refactoring',
            lineterm=''
        )
        return '\n'.join(diff)

    def tool_name(self) -> str:
        """ The name of the tool that produced this refactoring, or "no tool" for the free-text path. """
        return "no tool"

    def set_evaluation(self, evaluation: RefactoringEvaluation) -> None:
        """ Set the evaluation for the refactoring. """
        self.evaluation = evaluation

    def to_dict(self) -> dict:
        return {
            "old_code": self.old_code,
            "new_code": self.new_code,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Refactoring':
        refactoring = cls(
            old_code=data["old_code"],
            new_code=data["new_code"]
        )
        if data.get("evaluation"):
            refactoring.evaluation = RefactoringEvaluation.from_dict(data["evaluation"])
        return refactoring
    