from rope.base.project import Project
from rope.base import libutils
from rope.refactor.extract import ExtractMethod
from dataclasses import dataclass

from refactoring.rope_refactoring import RopeRefactoring
from utility.cli import CLI

@dataclass
class ExtractMethodArguments:
    start_line: int
    end_line: int
    new_name: str

class ExtractMethodRefactoring(RopeRefactoring):
    def execute_rope_refactoring(self, project: Project, filepath: str, refactoring_arguments: ExtractMethodArguments) -> None:
        resource = libutils.path_to_resource(project, filepath)
        start_offset = calculate_offset_for_line(filepath, refactoring_arguments.start_line)
        end_offset = calculate_offset_for_line(filepath, refactoring_arguments.end_line, include_line=True)
        extract_method = ExtractMethod(project, resource, start_offset=start_offset, end_offset=end_offset)
        changes = extract_method.get_changes(refactoring_arguments.new_name)
        project.do(changes)

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
            return ExtractMethodRefactoring(filepath, ExtractMethodArguments(start_line=start_line, end_line=end_line, new_name=new_name))
        except Exception as e:
            CLI.print_error(f"Failed to create ExtractMethodRefactoring for file {filepath} from line {start_line} to line {end_line} with new method name '{new_name}'. Error: {e}")
            return None

def calculate_offset_for_line(filepath: str, line_number: int, include_line: bool = False) -> int:
    with open(filepath, "r") as file:
        lines = file.readlines()
    last_included_line = line_number if include_line else line_number - 1
    offset = sum(len(line) for line in lines[:last_included_line])
    return offset