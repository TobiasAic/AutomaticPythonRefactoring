from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory

from rope.base.project import Project

from refactoring.refactoring import Refactoring


class RopeRefactoring[RopeRefactoringArguments](Refactoring, ABC):
    def __init__(self, code: str, refactoring_arguments: RopeRefactoringArguments):
        """Initialize a rope refactoring, execute it against the whole file and store the old and new code.

        The segment is only used to locate what to refactor - rope itself runs
        against the complete (marker-tagged) file, so it has full-file context.

        Args:
            code_file (CodeFile): The file being refactored.
            segment_id (int): The id of the segment the refactoring was generated from.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.
        """
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file_path = temp_dir_path / "temp_file.py"
            self.__write_file(temp_file_path, code)

            # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
            project = Project(temp_dir_path, ropefolder=None)
            self.execute_rope_refactoring(project, temp_file_path, code, refactoring_arguments)
            project.close()

            new_code = self.__read_file(temp_file_path)

        super().__init__(code, new_code)

    def tool_name(self) -> str:
        return "Rope"

    @abstractmethod
    def execute_rope_refactoring(self, project: Project, filepath: str, code: str, refactoring_arguments: RopeRefactoringArguments) -> None:
        """Execute the rope refactoring.
           This should be implemented by the subclasses while this class handles the Rope project.

        Args:
            project (Project): The Rope project instance.
            filepath (str): The path to the file containing the code to refactor.
            code_file (CodeFile): The file being refactored, for locating the segment's code and offset.
            segment_id (int): The id of the segment the refactoring was generated from.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.
        """

    def __read_file(self, filepath: str) -> str:
        with open(filepath, 'r') as file:
            return file.read()

    def __write_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'w') as file:
            file.write(content)
