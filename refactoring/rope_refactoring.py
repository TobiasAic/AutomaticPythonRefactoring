from pathlib import Path
from tempfile import TemporaryDirectory

from rope.base.project import Project

from refactoring.refactoring import Refactoring
from utility.code_file import CodeFile


class RopeRefactoring[RopeRefactoringArguments](Refactoring):
    def __init__(self, code_file: CodeFile, segment_id: int, refactoring_arguments: RopeRefactoringArguments):
        """Initialize a rope refactoring, execute it against the whole file and store the old and new code.

        The segment is only used to locate what to refactor - rope itself runs
        against the complete (marker-tagged) file, so it has full-file context.

        Args:
            code_file (CodeFile): The file being refactored.
            segment_id (int): The id of the segment the refactoring was generated from.
            refactoring_arguments (RopeRefactoringArguments): The arguments for the refactoring.
        """
        marked_code, _ = code_file.marked_code_and_offset(segment_id)

        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file_path = temp_dir_path / "temp_file.py"
            self.__write_file(temp_file_path, marked_code)

            # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
            project = Project(temp_dir_path, ropefolder=None)
            self.execute_rope_refactoring(project, temp_file_path, code_file, segment_id, refactoring_arguments)
            project.close()

            new_marked_code = self.__read_file(temp_file_path)

        new_code_file = code_file.with_new_marked_code(new_marked_code)
        super().__init__(code_file.code, new_code_file.code)
        self.code_file = new_code_file

    def tool_name(self) -> str:
        return "Rope"

    def execute_rope_refactoring(self, project: Project, filepath: str, code_file: CodeFile, segment_id: int, refactoring_arguments: RopeRefactoringArguments) -> None:
        """Execute the rope refactoring.
           This should be implemented by the subclasses while this class handles the Rope project.

        Args:
            project (Project): The Rope project instance.
            filepath (str): The path to the file containing the code to refactor.
            code_file (CodeFile): The file being refactored, for locating the segment's code and offset.
            segment_id (int): The id of the segment the refactoring was generated from.
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
