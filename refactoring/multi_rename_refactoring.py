import os

from dataclasses import dataclass

from refactoring.free_edit_refactoring import FreeEditRefactoring 
from rope.base.project import Project
from rope.base import libutils
from rope.refactor.rename import Rename
from utility.cli import CLI

@dataclass
class RenameArguments:
    line_number: int
    old_name: str
    new_name: str

class MultiRenameRefactoring(FreeEditRefactoring):
    def __init__(self, filepath: str, rename_arguments: list[RenameArguments]):
        old_code = self.read_file(filepath)

        # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
        project = Project(os.path.dirname(filepath), ropefolder=None)

        for argument in rename_arguments:
            resource = libutils.path_to_resource(project, filepath)

            try:
                offset = self.calculate_offset(filepath, argument.line_number, argument.old_name)
            except ValueError as e:
                CLI.print_error(f"Failed to calculate offset for argument {argument}. Error: {e}")
                continue

            rename = Rename(project, resource, offset)

            changes = rename.get_changes(argument.new_name)
            project.do(changes)

        project.close()
        new_code = self.read_file(filepath)
        self.write_file(filepath, old_code)

        super().__init__(filepath, old_code, new_code)

    def revert(self) -> None:
        self.write_file(self.filepath, self.old_code)

    def calculate_offset(self, filepath: str, line_number: int, identifier: str) -> int:
        with open(filepath, "r") as f:
            lines = f.readlines()

        offset = 0
        for i in range(line_number - 1):
            offset += len(lines[i])

        offset += lines[line_number - 1].index(identifier)
        return offset

    def read_file(self, filepath: str) -> str:
        with open(filepath, 'r') as file:
            return file.read()
        
    def write_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'w') as file:
            file.write(content)

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

