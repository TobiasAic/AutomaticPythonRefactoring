import json
import random
from textwrap import dedent

from llm.llm import LLM
from llm.llm_types import ToolCall
from refactoring.apply_edits_refactoring import ApplyEditsTool
from refactoring.extract_method_refactoring import ExtractMethodTool
from refactoring.multi_rename_refactoring import MultiRenameTool
from refactoring.refactoring import Refactoring
from refactoring.rename_refactoring import RenameTool
from tree_of_thoughts.refactoring_category import ALL_CATEGORIES, RefactoringCategory
from utility.cli import CLI


class RefactoringGenerator:
    prompt = dedent("""
    You are generating a refactoring candidate for a Python file or a part of it to improve readability.

    This is the Python file or segment to refactor:
    {code_segment}
    This segment could be part of a larger file, so you should not assume that it is the entire file.
    It could be part of a larger class or function. 
    Do not change the indentation.

    Find exactly one small refactoring from the category specified below.

    The refactoring must:
    - Improve readability.
    - Preserve behavior exactly.
    - Not change public APIs.
    - Not add imports.
    - Not rename functions, parameters, or classes.
    - Not repeat a refactoring already performed in the commit history.

    Commit history:
    {commit_history}

    Prefer a real readability improvement over a cosmetic change.
    """).strip()

    tool_instruction = dedent("""
    You must express your answer only by calling one of the tools listed below - never as text.
    There are specific tools for some refactorings.
    If you can use a specific tool for the refactoring you want to perform, use it instead of the generic `apply_edits` tool.
    If you can't find a specific tool for the refactoring you want to perform, use the `apply_edits` tool.
    It lets you return only the changed code instead of the entire segment.
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

    def __init__(self, llm: LLM, count: int = 1, categories: list[RefactoringCategory] | None = None):
        """
        Args:
            categories: The categories still available to this generator. Defaults to all
                categories; pass a subset when resuming a segment whose categories were
                already partially exhausted (i.e. the LLM called the no_refactoring tool for them).
        """
        self.llm = llm
        self.categories = list(categories) if categories is not None else list(ALL_CATEGORIES)
        if count > len(ALL_CATEGORIES) and count > 0:
            raise ValueError(
                f"Count {count} exceeds the number of available categories {len(ALL_CATEGORIES)} or is not positive.")
        self.count = count

    def generate_refactorings(self, code_segment: str, commit_history: list) -> list[Refactoring]:
        """Generate refactorings from different categories for a given code segment using the LLM.

        Args:
            code_segment (str): The code segment to be refactored. 
            filepath (str): The path to the file containing the code segment.
            commit_history (list): A list of previous commits. (This is given to the LLM to prevent repeated refactorings.)

        Returns:
            List[Refactoring]: A list of generated refactoring candidates.
        """
        prompt = self.prompt.format(
            code_segment=self.__add_line_numbers(code_segment),
            commit_history=commit_history
        )

        round_categories = random.sample(
            self.categories, min(self.count, len(self.categories)))

        if len(round_categories) != len(self.categories):
            CLI.print_debug(
                f"Selected categories for this round: {', '.join([category.get_name() for category in round_categories])}")

        tools = [
            category.get_tools() + [ApplyEditsTool.get_description(), self.no_refactoring_tool]
            for category in round_categories
        ]

        prompts = []
        for category in round_categories:
            category_prompt = prompt
            category_prompt += "\n" + self.tool_instruction
            category_prompt += "\n" + category.get_prompt()
            prompts.append(category_prompt)

        llm_responses = self.llm.batch_generate(prompts, tools)

        refactorings = []
        for i, response in enumerate(llm_responses):
            if response.tool_call is None:
                CLI.print_error(
                    f"Expected a tool call from the LLM but got none. Response content: {response}")
                continue

            if response.tool_call.name == "no_refactoring":
                CLI.print_debug(
                    f"No meaningful refactoring found for {round_categories[i].get_name()}.")
                # Remove the category from future consideration
                self.categories.remove(round_categories[i])
                continue

            refactoring = self.__handle_tool_call_response(
                response.tool_call, code_segment)
            if refactoring:
                refactoring.category = round_categories[i]
                refactorings.append(refactoring)

        return refactorings

    def __handle_tool_call_response(self, tool_call: ToolCall, code_segment: str) -> Refactoring | None:
        """ Generate a Refactoring object from a tool call response from the LLM. """
        arguments = json.loads(tool_call.arguments)
        CLI.print_debug(
            f"Received tool call for '{tool_call.name}' with arguments: {arguments}")
        try:
            if tool_call.name == "rename":
                return RenameTool.call(code_segment=code_segment, arguments=arguments)
            if tool_call.name == "extract_method":
                return ExtractMethodTool.call(code_segment=code_segment, arguments=arguments)
            if tool_call.name == "multi_rename":
                return MultiRenameTool.call(code_segment=code_segment, arguments=arguments)
            if tool_call.name == "apply_edits":
                return ApplyEditsTool.call(code_segment=code_segment, arguments=arguments)
            else:
                CLI.print_error(
                    f"Received tool call for unknown tool '{tool_call.name}'. Response content: {tool_call}")
                return None
        except Exception as e:
            CLI.print_error(
                f"An error occurred while handling the tool call: {e}")
            return None

    def __add_line_numbers(self, code: str) -> str:
        lines = code.split("\n")
        numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered_lines)
