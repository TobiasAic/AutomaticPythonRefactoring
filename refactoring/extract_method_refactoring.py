""" This file contains the implementation of the Extract Method refactoring and a corresponding tool for an LLM to call. """

from dataclasses import dataclass

from rope.base import libutils
from rope.base.project import Project
from rope.refactor.extract import ExtractMethod

from refactoring.refactoring_tool import RefactoringTool
from refactoring.rope_refactoring import RopeRefactoring
from utility.cli import CLI
from utility.code_file import CodeFile


@dataclass
class ExtractMethodArguments:
    """ Arguments from the LLM for the Extract Method refactoring. """
    code_to_extract: str
    new_name: str

class ExtractMethodRefactoring(RopeRefactoring):
    def execute_rope_refactoring(self, project: Project, filepath: str, code_file: CodeFile, segment_id: int, refactoring_arguments: ExtractMethodArguments) -> None:
        """Execute the extract method refactoring using Rope.

        Args:
            project (Project): The Rope project instance.
            filepath (str): The path to the file containing the code to refactor.
            code_file (CodeFile): The file being refactored.
            segment_id (int): The id of the segment the refactoring was generated from.
            refactoring_arguments (ExtractMethodArguments): The arguments for the extract method refactoring.

        Raises:
            ValueError: If code_to_extract does not appear in the segment exactly once.
        """
        resource = libutils.path_to_resource(project, filepath)
        start_offset, end_offset = self.__calculate_offsets(code_file, segment_id, refactoring_arguments.code_to_extract)
        extract_method = ExtractMethod(project, resource, start_offset=start_offset, end_offset=end_offset)
        changes = extract_method.get_changes(refactoring_arguments.new_name)
        project.do(changes)

    def tool_name(self) -> str:
        return "Extract Method"

    def __calculate_offsets(self, code_file: CodeFile, segment_id: int, code_to_extract: str) -> tuple[int, int]:
        segment_code = code_file.get_segment(segment_id).code
        occurrences = segment_code.count(code_to_extract)
        if occurrences != 1:
            raise ValueError(
                f"code_to_extract must match exactly once in the code segment, found {occurrences} occurrences: {code_to_extract!r}")
        _, segment_offset = code_file.marked_code_and_offset(segment_id)
        start_offset = segment_offset + segment_code.index(code_to_extract)
        end_offset = start_offset + len(code_to_extract)
        return start_offset, end_offset

class ExtractMethodTool(RefactoringTool):
    @staticmethod
    def get_description() -> dict:
        """ Returns the description of the Extract Method tool for the LLM. """
        return {
        "type": "function",
        "function": {
            "name": "extract_method",
            "description": "Extract a method from a block of code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_to_extract": {
                        "type": "string",
                        "description": "The exact code to extract into a new method, verbatim, including whitespace and indentation. Must appear exactly once in the code segment."
                    },
                    "new_name": {
                        "type": "string",
                        "description": "The name of the new method."
                    }
                },
                "required": ["code_to_extract", "new_name"],
                "additionalProperties": False,
            },
        },
    }

    def call(code_file: CodeFile, segment_id: int, arguments: dict) -> ExtractMethodRefactoring:
        """ Calls the Extract Method refactoring with the given arguments from the LLM. """
        code_to_extract = arguments.get("code_to_extract")
        new_name = arguments.get("new_name")
        try:
            return ExtractMethodRefactoring(code_file, segment_id, ExtractMethodArguments(code_to_extract=code_to_extract, new_name=new_name))
        except Exception as e:
            CLI.print_error(f"Failed to create ExtractMethodRefactoring for code_to_extract {code_to_extract!r} with new method name '{new_name}'. Error: {e}")
            return None

