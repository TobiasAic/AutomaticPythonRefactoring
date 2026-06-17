from rope.base.project import Project
from rope.base import libutils
from rope.refactor.extract import ExtractMethod
import os

from refactoring.refactoring import Refactoring
from utility.cli import CLI

class ExtractMethodRefactoring(Refactoring):
    def __init__(self, filepath: str, start_offset: int, end_offset: int, new_method_name: str):
        super().__init__(filepath)

        try: 
            # ropefolder=None stops rope from creating a .ropeproject folder, which helps to keep the project directory clean
            self.project = Project(os.path.dirname(filepath), ropefolder=None)
            self.resource = libutils.path_to_resource(self.project, filepath)
            self.extract_method = ExtractMethod(self.project, self.resource, start_offset=start_offset, end_offset=end_offset)
            self.changes = self.extract_method.get_changes(new_method_name)
        except Exception as e:
            CLI.print_error(f"Failed to initialize ExtractMethodRefactoring for file {filepath} with start offset {start_offset} and end offset {end_offset}. Error: {e}")
            return None

    def get_diff(self) -> str:
       return self.changes.get_description()

    def execute(self) -> None:
       self.project.do(self.changes) 
    
    def revert(self) -> None:
        self.project.history.undo()

    def __del__(self):
        self.project.close()

class ExtractMethodTool:
    @staticmethod
    def get_description() -> dict:
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

    def call(filepath: str, start_line: int, end_line: int, new_name: str) -> ExtractMethodRefactoring:
        try:
            start_offset = calculate_offset_for_line(filepath, start_line)
            end_offset = calculate_offset_for_line(filepath, end_line, include_line=True)
            return ExtractMethodRefactoring(filepath=filepath, start_offset=start_offset, end_offset=end_offset, new_method_name=new_name)
        except Exception as e:
            CLI.print_error(f"Failed to create ExtractMethodRefactoring for file {filepath} from line {start_line} to line {end_line} with new method name '{new_name}'. Error: {e}")
            return None

def calculate_offset_for_line(filepath: str, line_number: int, include_line: bool = False) -> int:
    with open(filepath, "r") as file:
        lines = file.readlines()
    last_included_line = line_number if include_line else line_number - 1
    offset = sum(len(line) for line in lines[:last_included_line])
    return offset