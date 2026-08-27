import json
import random
from textwrap import dedent

from llm.llm import LLM
from llm.llm_types import ToolCall
from refactoring.apply_edits_refactoring import ApplyEditsTool
from refactoring.extract_method_refactoring import ExtractMethodTool
from refactoring.multi_rename_refactoring import MultiRenameTool
from refactoring.refactoring import Refactoring
from tree_of_thoughts.refactoring_category import RefactoringCategory
from utility.cli import CLI
from collections.abc import Callable


class RefactoringGenerator:
    prompt = dedent("""
    You are generating a refactoring candidate for a Python file or a part of it to improve readability.

    {category_prompt}

    Find exactly one small refactoring in this category for the code below.

    This is the Python file or segment to refactor:
    {code_segment}
    This segment could be part of a larger file, so you should not assume that it is the entire file.
    It could be part of a larger class or function.

    The refactoring must:
    - Improve readability.
    - Preserve behavior exactly.
    - Not change public APIs.
    - Not add imports.
    - Not rename functions, parameters, or classes.
    - Not change the indentation of any code you keep.
    - Not repeat a refactoring already performed in the commit history below.

    Commit history (most recent first):
    {commit_history}

    Prefer a real readability improvement over a cosmetic change.

    You must express your answer by calling exactly one tool - never as text, and never more than one call.
    Some refactorings have a dedicated tool (e.g. extract_method, multi_rename) - use it instead of the generic `apply_edits` tool whenever it applies.
    Otherwise use `apply_edits`, which lets you return only the changed code instead of rewriting the whole segment.
    Each edit's old_code must match the segment exactly once, verbatim.
    If you can't find a refactoring in this category that significantly improves readability, call the `no_refactoring` tool.
    """).strip()

    no_refactoring_tool = {
        "type": "function",
        "function": {
            "name": "no_refactoring",
            "description": "Call this when there is no refactoring in this category that significantly improves readability.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    }

    def __init__(self, llm: LLM, count: int, remove_category: Callable[[RefactoringCategory], None]):
        self.llm = llm
        if count <= 0:
            raise ValueError(f"Count must be a positive integer, got {count}.")
        self.count = count
        self.remove_category = remove_category

    def generate_refactorings(self, code: str, commit_history: list, categories: list[RefactoringCategory]) -> list[Refactoring]:
        """Generate refactorings from different categories for a given code segment using the LLM.

        Args:
            code(str): The code to generate refactorings for
            commit_history (list): A list of previous commits. (This is given to the LLM to prevent repeated refactorings.)
            categories (list[RefactoringCategory]): The categories still available for this segment. Categories
                for which the LLM finds no meaningful refactoring are removed from this list in place.

        Returns:
            List[Refactoring]: A list of generated refactoring candidates.
        """
        commit_history_text = self.__format_commit_history(commit_history)

        round_categories = random.sample(
            categories, min(self.count, len(categories)))

        if len(round_categories) != len(categories):
            CLI.print_debug(
                f"Selected categories for this round: {', '.join([category.get_name() for category in round_categories])}")

        tools = [
            category.get_tools() + [ApplyEditsTool.get_description(), self.no_refactoring_tool]
            for category in round_categories
        ]

        prompts = [
            self.prompt.format(
                code_segment=code,
                commit_history=commit_history_text,
                category_prompt=category.get_prompt(),
            )
            for category in round_categories
        ]

        llm_responses = self.llm.batch_generate(prompts, tools, require_tool_call=True)

        refactorings = []
        for i, response in enumerate(llm_responses):
            if response.tool_call is None:
                CLI.print_error(f"Expected a tool call from the LLM but got none. Response content: {response}")
                continue

            if response.tool_call.name == "no_refactoring":
                CLI.print_debug(f"No meaningful refactoring found for {round_categories[i].get_name()}.")
                self.remove_category(round_categories[i])
                continue

            refactoring: Refactoring | None = self.__handle_tool_call_response(response.tool_call, code)
            if refactoring:
                refactoring.category = round_categories[i]
                refactorings.append(refactoring)

        return refactorings

    @staticmethod
    def __format_commit_history(commit_history: list) -> str:
        """ Render commit messages as a readable bullet list instead of a raw Python list. """
        if not commit_history:
            return "(no commits yet)"
        return "\n".join(f"- {message.strip()}" for message in commit_history)

    def __handle_tool_call_response(self, tool_call: ToolCall, code: str) -> Refactoring | None:
        """ Generate a Refactoring object from a tool call response from the LLM. """
        arguments = json.loads(tool_call.arguments)
        CLI.print_debug(f"Received tool call for '{tool_call.name}'")
        try:
            if tool_call.name == "extract_method":
                return ExtractMethodTool.call(code=code, arguments=arguments)
            if tool_call.name == "multi_rename":
                return MultiRenameTool.call(code=code, arguments=arguments)
            if tool_call.name == "apply_edits":
                return ApplyEditsTool.call(code=code, arguments=arguments)
            else:
                CLI.print_error(
                    f"Received tool call for unknown tool '{tool_call.name}'. Response content: {tool_call}")
                return None
        except Exception as e:
            CLI.print_error(
                f"An error occurred while handling the tool call: {e}")
            return None