from refactoring.refactoring import Refactoring

from rope.base.project import Project
import os

class RopeRefactoring[RopeRefactoringArguments](Refactoring):
    def __init__(self, filepath: str, refactoring_arguments: RopeRefactoringArguments):
        """Initialize a rope refactoring, execute it and store the old and new code.

        Args:
            filepath (str): The path to the file containing the code to refactor.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.
        """
        old_code = self.__read_file(filepath)

        # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
        project = Project(os.path.dirname(filepath), ropefolder=None)
        self.execute_rope_refactoring(project, filepath, refactoring_arguments)
        project.close()

        new_code = self.__read_file(filepath)
        self.write_file(filepath, old_code)

        super().__init__(filepath, old_code, new_code)

    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: RopeRefactoringArguments) -> None:
        """Execute the rope refactoring.
           This should be implemented by the subclasses while this class handles the Rope project.

        Args:
            project (Project): The Rope project instance.
            filepath (str): The path to the file containing the code to refactor.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.

        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def __read_file(self, filepath: str) -> str:
        with open(filepath, 'r') as file:
            return file.read()