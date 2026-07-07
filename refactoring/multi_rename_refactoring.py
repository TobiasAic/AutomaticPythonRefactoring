from rope.base.project import Project
from rope.base import libutils
from rope.refactor.rename import Rename

from utility.cli import CLI
from refactoring.rope_refactoring import RopeRefactoring
from refactoring.rename_shared import RenameArguments, calculate_offset

class MultiRenameRefactoring(RopeRefactoring[list[RenameArguments]]):
    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: list[RenameArguments]) -> None:
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

class MultiRenameTool:
    @staticmethod
    def get_description() -> dict:
        return {
                "type": "function",
                "function": {
                    "name": "multi_rename",
                    "description": "Rename multiple local variables or attributes across one or more lines. Per rename operation give only one line number, the old name, and the new name. The tool will find all occurrences of the old name in the specified line and rename them to the new name.",
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
                                "description": "Line number containing the identifier."
                            },
                            "old_name": {
                                "type": "string",
                                "description": "Current identifier name."
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

    def call(filepath: str, rename_arguments: list[RenameArguments]) -> MultiRenameRefactoring:
        try:
            return MultiRenameRefactoring(filepath, rename_arguments)
        except Exception as e:
            CLI.print_error(f"Failed to create MultiRenameRefactoring for file {filepath} with rename arguments {rename_arguments}. Error: {e}")
            return None

