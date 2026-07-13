import os

from refactoring.rope_refactoring import RopeRefactoring
from rope.base import libutils
from rope.refactor.rename import Rename
from utility.cli import CLI
from refactoring.rename_shared import RenameArguments, calculate_offset
from refactoring.refactoring_tool import RefactoringTool

class RenameRefactoring(RopeRefactoring[RenameArguments]):
    def execute_rope_refactoring(self, project, filepath, refactoring_arguments: RenameArguments):

        resource = libutils.path_to_resource(project, filepath)
        offset = calculate_offset(filepath, refactoring_arguments.line_number, refactoring_arguments.old_name)
        rename = Rename(project, resource, offset)
        changes = rename.get_changes(refactoring_arguments.new_name)
        project.do(changes)

class RenameTool(RefactoringTool):
    @staticmethod
    def get_description() -> dict:
        return {
        "type": "function",
        "function": {
            "name": "rename",
            "description": "Rename a local variable or attribute of a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line_number": {
                        "type": "integer",
                        "description": "The line number of the code containing the identifier to rename. For example: 42."
                    },
                    "old_name": {
                        "type": "string",
                        "description": "The current name of the identifier to rename. For example: 'user'."
                    },
                    "new_name": {
                        "type": "string",
                        "description": "The new name for the identifier. For example: 'customer'."
                    }
                },
                "required": ["line_number", "old_name", "new_name"],
                "additionalProperties": False,
            },
        },
    }

    def call(filepath: str, arguments: dict) -> RenameRefactoring:
        line_number = int(arguments.get("line_number"))
        old_name = arguments.get("old_name")
        new_name = arguments.get("new_name")
        try:
            return RenameRefactoring(filepath, RenameArguments(line_number=line_number, old_name=old_name, new_name=new_name))
        except Exception as e:
            CLI.print_error(f"Failed to create RenameRefactoring for file {filepath} at line {line_number} renaming '{old_name}' to '{new_name}'. Error: {e}")
            return None