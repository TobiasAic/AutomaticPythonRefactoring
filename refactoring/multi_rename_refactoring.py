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
                    "description": "Rename multiple local variables or attributes, especially when several weak names appear in the same nearby block, function, or scope. Use one entry per identifier: for each change, provide one line number where the identifier appears, the exact old name, and the new name. Do not add separate entries for every occurrence in the same scope. For example, if the code is number: 1: def build_path():\nnumber: 2:     base_dir = \"/tmp\"\nnumber: 3:     return base_dir, then call the tool with changes containing line_number 2, old_name base_dir, and new_name renamed_base_dir.",
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

    def call(filepath: str, rename_arguments: list[RenameArguments]) -> MultiRenameRefactoring:
        try:
            return MultiRenameRefactoring(filepath, rename_arguments)
        except Exception as e:
            CLI.print_error(f"Failed to create MultiRenameRefactoring for file {filepath} with rename arguments {rename_arguments}. Error: {e}")
            return None

