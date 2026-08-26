""" This file contains the implementation of the Multi Rename refactoring and a corresponding tool for an LLM to call. """
import re
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
    context_code: str
    old_name: str
    new_name: str

def calculate_offset(filepath: str, context_code: str, identifier: str) -> int:
    """ Calculates the offset of an identifier within a unique snippet of code in a file.

    Args:
        filepath (str): The path to the file containing the code.
        context_code (str): A snippet of code, unique in the file, containing exactly one
            occurrence of identifier.
        identifier (str): The identifier to rename.

    Returns:
        int: The offset of the identifier in the file.

    Raises:
        ValueError: If context_code does not appear in the file exactly once, or identifier
            does not appear in context_code exactly once.
    """
    with open(filepath, "r") as f:
        content = f.read()

    context_occurrences = content.count(context_code)
    if context_occurrences != 1:
        raise ValueError(
            f"context_code must match exactly once in the code segment, found {context_occurrences} occurrences: {context_code!r}")

    identifier_pattern = re.compile(rf"\b{re.escape(identifier)}\b")
    identifier_matches = list(identifier_pattern.finditer(context_code))
    if len(identifier_matches) != 1:
        raise ValueError(
            f"old_name must match exactly once as a whole identifier within context_code, found {len(identifier_matches)} occurrences: {identifier!r}")

    context_offset = content.index(context_code)
    return context_offset + identifier_matches[0].start()


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
                offset = calculate_offset(filepath, argument.context_code, argument.old_name)
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
                    "description": "Rename multiple local variables or attributes, especially when several weak names appear in the same nearby block, function, or scope. Use one entry per identifier: for each change, provide a short snippet of code containing exactly one occurrence of the identifier (context_code), the exact old name, and the new name. Do not add separate entries for every occurrence in the same scope. For example, if the code is:\ndef build_path():\n    base_dir = \"/tmp\"\n    return base_dir\nthen call the tool with changes containing context_code 'base_dir = \"/tmp\"', old_name 'base_dir', and new_name 'renamed_base_dir'.\n Only use this tool for renaming. You are not allowed to use it for adding types or doing any other refactorings.",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "changes": {
                        "type": "array",
                        "description": "List of rename operations to apply.",
                        "items": {
                            "type": "object",
                            "properties": {
                            "context_code": {
                                "type": "string",
                                "description": "A short snippet of code, verbatim, that appears exactly once in the code segment and contains exactly one occurrence of old_name. Used to locate which occurrence to rename."
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
                            "required": ["context_code", "old_name", "new_name"],
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
            context_code = change.get("context_code")
            old_name = change.get("old_name")
            new_name = change.get("new_name")
            rename_arguments.append(RenameArguments(context_code=context_code, old_name=old_name, new_name=new_name))
        try:
            return MultiRenameRefactoring(code_segment, rename_arguments)
        except Exception as e:
            CLI.print_error(f"Failed to create MultiRenameRefactoring for code_segment with rename arguments {rename_arguments}. Error: {e}")
            return None

