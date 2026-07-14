import difflib

from refactoring.refactoring_evaluation import RefactoringEvaluation 

class Refactoring:
    """ Base class representing a refactoring operation."""
    def __init__(self, filepath: str, old_code: str, new_code: str):
        self.filepath = filepath
        self.old_code = old_code
        self.new_code = new_code
        self.evaluation = None
        self.commit_hash: str = None

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

    def execute(self) -> None:
        """ Execute the refactoring on the Python file. """
        self.__write_file(self.filepath, self.new_code)

    def revert(self) -> None:
        """ Revert the refactoring on the Python file. """
        self.__write_file(self.filepath, self.old_code)

    def set_evaluation(self, evaluation: RefactoringEvaluation) -> None:
        """ Set the evaluation for the refactoring. """
        self.evaluation = evaluation

    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "old_code": self.old_code,
            "new_code": self.new_code,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "commit_hash": self.commit_hash
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Refactoring':
        refactoring = cls(
            filepath=data["filepath"],
            old_code=data["old_code"],
            new_code=data["new_code"]
        )
        if data.get("evaluation"):
            refactoring.evaluation = RefactoringEvaluation.from_dict(data["evaluation"])
        refactoring.commit_hash = data.get("commit_hash")
        return refactoring
    
    def __write_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'w') as file:
            file.write(content)

