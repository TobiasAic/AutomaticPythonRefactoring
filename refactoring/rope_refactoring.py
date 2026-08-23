from pathlib import Path
from tempfile import TemporaryDirectory

from rope.base.project import Project

from refactoring.refactoring import Refactoring


class RopeRefactoring[RopeRefactoringArguments](Refactoring):
    def __init__(self, code_segment: str, refactoring_arguments: RopeRefactoringArguments):
        """Initialize a rope refactoring, execute it and store the old and new code.

        Args:
            code_segment (str): The code segment to refactor.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.
        """

        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file_path = temp_dir_path / "temp_file.py"
            self.__write_file(temp_file_path, code_segment)

            # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
            project = Project(temp_dir_path, ropefolder=None)
            self.execute_rope_refactoring(project, temp_file_path, refactoring_arguments)
            project.close()

            new_code = self.__read_file(temp_file_path)

        super().__init__(code_segment, new_code)

    def tool_name(self) -> str:
        return "Rope"

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

    def __write_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'w') as file:
            file.write(content)