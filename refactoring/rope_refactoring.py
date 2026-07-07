from refactoring.refactoring import Refactoring

from rope.base.project import Project
import os

class RopeRefactoring[RopeRefactoringArguments](Refactoring):
    def __init__(self, filepath: str, refactoring_arguments: RopeRefactoringArguments):
        old_code = self.read_file(filepath)

        # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
        project = Project(os.path.dirname(filepath), ropefolder=None)
        self.execute_rope_refactoring(project, filepath, refactoring_arguments)
        project.close()

        new_code = self.read_file(filepath)
        self.write_file(filepath, old_code)

        super().__init__(filepath, old_code, new_code)

    def read_file(self, filepath: str) -> str:
        with open(filepath, 'r') as file:
            return file.read()
        
    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: RopeRefactoringArguments) -> None:
        raise NotImplementedError("This method should be implemented in subclasses.")