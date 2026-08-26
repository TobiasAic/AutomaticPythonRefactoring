""" This file contains the implementation of the Multi Rename refactoring and a corresponding tool for an LLM to call. """
from dataclasses import dataclass

from rope.base import libutils
from rope.base.project import Project
from rope.refactor.rename import Rename

from refactoring.refactoring_tool import RefactoringTool
from refactoring.rope_refactoring import RopeRefactoring
from utility.cli import CLI


@dataclass
class RenameArguments:
    """ Arguments from the LLM for the Rename and MultiRename refactoring. """
    line_number: int
    old_name: str
    new_name: str

def calculate_offset(filepath: str, line_number: int, identifier: str) -> int:
    """ Calculates the offset of an identifier in a file.

    Args:
        filepath (str): The path to the file containing the code.
        line_number (int): The line number of the identifier to rename.
        identifier (str): The identifier to rename.

    Returns:
        int: The offset of the identifier in the file.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    offset = 0
    for i in range(line_number - 1):
        offset += len(lines[i])

    offset += lines[line_number - 1].index(identifier)
    return offset


class MultiRenameRefactoring(RopeRefactoring[list[RenameArguments]]):
    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: list[RenameArguments]) -> None:
        """Execute the multi rename refactoring using Rope.

        Args:
            project (Project): The Rope project instance. 
            filepath (str): The path to the file containing the code to refactor.
            refactoring_arguments (list[RenameArguments]): The arguments for the multi rename refactoring.
        """
        for argument in refactoring_arguments:
            resource = libutils.path_to_resource(project, filepath)

            try:
                offset = calculate_offset(filepath, argument.line_number, argument.old_name)
            except ValueError as e:
                CLI.print_error(f"Failed to calculate offset for argument {argument}. Error: {e}")
                continue

            rename = Rename(project, resource, offset)

            changes = rename.get_changes(argument.new_name)
            project.do(changes)

    def tool_name(self) -> str:
        return "Multi Rename"

class MultiRenameTool(RefactoringTool):
    @staticmethod
    def get_description() -> dict:
        """ Returns the description of the Multi Rename tool for the LLM. """
        return {
                "type": "function",
                "function": {
                    "name": "multi_rename",
                    "description": "Rename multiple local variables or attributes, especially when several weak names appear in the same nearby block, function, or scope. Use one entry per identifier: for each change, provide one line number where the identifier appears, the exact old name, and the new name. Do not add separate entries for every occurrence in the same scope. For example, if the code is number: 1: def build_path():\nnumber: 2:     base_dir = \"/tmp\"\nnumber: 3:     return base_dir, then call the tool with changes containing line_number 2, old_name base_dir, and new_name renamed_base_dir.\n Only use this tool for renaming. You are not allowed to use it for adding types or doing any other refactorings.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "changes": {
                        "type": "array",
                        "description": "List of rename operations to apply.",
                        "items": {
                            "type": "object",
                            "properties": {
                            "line_number": {
                                "type": "integer",
                                "description": "Line number of one occurrence used to locate the scope."
                            },
                            "old_name": {
                                "type": "string",
                                "description": "Exact current identifier name."
                            },
                            "new_name": {
                                "type": "string",
                                "description": "New identifier name."
                            }
                            },
                            "required": ["line_number", "old_name", "new_name"],
                            "additionalProperties": False
                        }
                        }
                    },
                    "required": ["changes"],
                    "additionalProperties": False
                    }
                }
                }

    def call(code_segment: str, arguments: dict) -> MultiRenameRefactoring:
        """ Calls the Multi Rename refactoring with the given arguments from the LLM. """
        changes = arguments.get("changes", [])
        rename_arguments = []
        for change in changes:
            line_number = int(change.get("line_number"))
            old_name = change.get("old_name")
            new_name = change.get("new_name")
            rename_arguments.append(RenameArguments(line_number=line_number, old_name=old_name, new_name=new_name))
        try:
            return MultiRenameRefactoring(code_segment, rename_arguments)
        except Exception as e:
            CLI.print_error(f"Failed to create MultiRenameRefactoring for code_segment with rename arguments {rename_arguments}. Error: {e}")
            return None

