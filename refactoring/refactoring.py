from refactoring.refactoring_evaluation import RefactoringEvaluation 

class Refactoring:
    def __init__(self):
        self.evaluation = None

    def get_diff(self) -> str:
        pass

    def execute(self) -> None:
        pass

    def set_evaluation(self, evaluation: RefactoringEvaluation) -> None:
        self.evaluation = evaluation