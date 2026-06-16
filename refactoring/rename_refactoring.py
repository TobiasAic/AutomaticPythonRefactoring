import os
import logging

from refactoring.refactoring import Refactoring
from rope.base.project import Project
from rope.base import libutils
from rope.refactor.rename import Rename

class RenameRefactoring(Refactoring):
    def __init__(self, filepath: str, offset: int, new_name: str):
        super().__init__(filepath)

        try:
            # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
            self.project = Project(os.path.dirname(filepath), ropefolder=None)
            self.resource = libutils.path_to_resource(self.project, filepath)
            self.rename = Rename(self.project, self.resource, offset)
            self.changes = self.rename.get_changes(new_name)
        except Exception as e:
            logger = logging.getLogger(f"refactoring.{__name__}")
            logger.error(f"Failed to initialize RenameRefactoring for file {filepath} with offset {offset}. Error: {e}")
            return None

    def get_diff(self) -> str:
       return self.changes.get_description()

    def execute(self) -> None:
       self.project.do(self.changes) 
    
    def revert(self) -> None:
        self.project.history.undo()

    def __del__(self):
        self.project.close()

class RenameRefactoringTool:
    @staticmethod
    def get_description() -> dict:
        return {
        "type": "function",
        "function": {
            "name": "rename_refactoring",
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

    def call(filepath: str, line_number: int, old_name: str, new_name: str) -> RenameRefactoring:
        try:
            offset = calculate_offset(filepath, line_number, old_name)
            return RenameRefactoring(filepath, offset, new_name)
        except Exception as e:
            logger = logging.getLogger(f"refactoring.{__name__}")
            logger.error(f"Failed to create RenameRefactoring for file {filepath} at line {line_number} renaming '{old_name}' to '{new_name}'. Error: {e}")
            return None

def calculate_offset(filepath: str, line_number: int, identifier: str) -> int:
    with open(filepath, "r") as f:
        lines = f.readlines()

    offset = 0
    for i in range(line_number - 1):
        offset += len(lines[i])

    offset += lines[line_number - 1].index(identifier)
    return offset