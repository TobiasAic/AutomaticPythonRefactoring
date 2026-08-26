""" This file contains the implementation of the Apply Edits refactoring and a corresponding tool for an LLM to call. """

from dataclasses import dataclass

from refactoring.refactoring import Refactoring
from refactoring.refactoring_tool import RefactoringTool
from utility.cli import CLI


@dataclass
class EditArguments:
    """ A single verbatim search-and-replace edit from the LLM for the Apply Edits refactoring. """
    old_code: str
    new_code: str


class ApplyEditsRefactoring(Refactoring):
    def __init__(self, code_segment: str, edits: list[EditArguments]):
        """Apply a sequence of verbatim search-and-replace edits to a code segment.

        Each edit is applied in order against the result of the previous one, so a later
        edit's old_code is matched against the already-edited text.

        Args:
            code_segment (str): The code segment to refactor.
            edits (list[EditArguments]): The edits to apply, each identifying the code to
                replace by exact, unique text rather than by line number.

        Raises:
            ValueError: If an edit's old_code does not appear in the current text exactly once.
        """
        new_code = code_segment
        for edit in edits:
            occurrences = new_code.count(edit.old_code)
            if occurrences != 1:
                raise ValueError(
                    f"old_code must match exactly once in the code segment, found {occurrences} occurrences: {edit.old_code!r}")
            new_code = new_code.replace(edit.old_code, edit.new_code, 1)

        super().__init__(code_segment, new_code)

    def tool_name(self) -> str:
        return "Apply Edits"


class ApplyEditsTool(RefactoringTool):
    @staticmethod
    def get_description() -> dict:
        """ Returns the description of the Apply Edits tool for the LLM. """
        return {
            "type": "function",
            "function": {
                "name": "apply_edits",
                "description": "Apply one or more small, precise edits to the code segment without repeating unchanged code. Prefer this over rewriting the whole segment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "edits": {
                            "type": "array",
                            "description": "The edits to apply, in order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "old_code": {
                                        "type": "string",
                                        "description": "The exact original code being replaced, verbatim, including whitespace and indentation. Must appear exactly once in the code segment."
                                    },
                                    "new_code": {
                                        "type": "string",
                                        "description": "The replacement code."
                                    }
                                },
                                "required": ["old_code", "new_code"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["edits"],
                    "additionalProperties": False,
                },
            },
        }

    def call(code_segment: str, arguments: dict) -> ApplyEditsRefactoring:
        """ Calls the Apply Edits refactoring with the given arguments from the LLM. """
        edits = [
            EditArguments(old_code=edit.get("old_code"), new_code=edit.get("new_code"))
            for edit in arguments.get("edits", [])
        ]
        try:
            return ApplyEditsRefactoring(code_segment, edits)
        except Exception as e:
            CLI.print_error(f"Failed to create ApplyEditsRefactoring with edits {edits}. Error: {e}")
            return None
