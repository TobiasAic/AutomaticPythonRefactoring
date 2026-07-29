""" This file contains the implementation of the Extract Method refactoring and a corresponding tool for an LLM to call. """

from rope.base.project import Project
from rope.base import libutils
from rope.refactor.extract import ExtractMethod
from dataclasses import dataclass

from refactoring.rope_refactoring import RopeRefactoring
from utility.cli import CLI
from refactoring.refactoring_tool import RefactoringTool

@dataclass
class ExtractMethodArguments:
    """ Arguments from the LLM for the Extract Method refactoring. """
    start_line: int
    end_line: int
    new_name: str

class ExtractMethodRefactoring(RopeRefactoring):
    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: ExtractMethodArguments) -> None:
        """Execute the extract method refactoring using Rope.

        Args:
            project (Project): The Rope project instance. 
            filepath (str): The path to the file containing the code to refactor.
            refactoring_arguments (ExtractMethodArguments): The arguments for the extract method refactoring.
        """
        resource = libutils.path_to_resource(project, filepath)
        start_offset = self.__calculate_offset_for_line(filepath, refactoring_arguments.start_line)
        end_offset = self.__calculate_offset_for_line(filepath, refactoring_arguments.end_line, include_line=True)
        extract_method = ExtractMethod(project, resource, start_offset=start_offset, end_offset=end_offset)
        changes = extract_method.get_changes(refactoring_arguments.new_name)
        project.do(changes)

    def tool_name(self) -> str:
        return "Extract Method"

    def __calculate_offset_for_line(self, filepath: str, line_number: int, include_line: bool = False) -> int:
        with open(filepath, "r") as file:
            lines = file.readlines()
        last_included_line = line_number if include_line else line_number - 1
        offset = sum(len(line) for line in lines[:last_included_line])
        return offset

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
                    "start_line": {
                        "type": "integer",
                        "description": "The number of the first line of the code block to extract."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "The number of the last line of the code block to extract."
                    },
                    "new_name": {
                        "type": "string",
                        "description": "The name of the new method."
                    }
                },
                "required": ["start_line", "end_line", "new_name"],
                "additionalProperties": False,
            },
        },
    }

    def call(filepath: str, arguments: dict) -> ExtractMethodRefactoring:
        """ Calls the Extract Method refactoring with the given arguments from the LLM. """
        start_line = int(arguments.get("start_line"))
        end_line = int(arguments.get("end_line"))
        new_name = arguments.get("new_name")
        try:
            return ExtractMethodRefactoring(filepath, ExtractMethodArguments(start_line=start_line, end_line=end_line, new_name=new_name))
        except Exception as e:
            CLI.print_error(f"Failed to create ExtractMethodRefactoring for file {filepath} from line {start_line} to line {end_line} with new method name '{new_name}'. Error: {e}")
            return None

