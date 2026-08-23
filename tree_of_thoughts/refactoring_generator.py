import json
import random
from textwrap import dedent

from llm.llm import LLM
from llm.llm_types import ToolCall
from refactoring.extract_method_refactoring import ExtractMethodTool
from refactoring.multi_rename_refactoring import MultiRenameTool
from refactoring.refactoring import Refactoring
from refactoring.rename_refactoring import RenameTool
from tree_of_thoughts.refactoring_category import (
    CLASS_STRUCTURE,
    CODE_QUALITY,
    CONDITIONAL_LOGIC,
    CONTROL_FLOW,
    EXPRESSION,
    METHOD_STRUCTURE,
)
from utility.cli import CLI


class RefactoringGenerator:
    prompt = dedent("""
    You are generating a refactoring candidate for a Python file to improve readability.

    This is the Python file to refactor:
    {code_segment}

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

    If there is no refactoring in that category that significantly improves readability, return "NO_REFACTORING".

    If you find a refactoring, return the refactored code in exactly one Markdown Python code block containing the complete refactored file following these requirements.
    Requirements:
    1. Output exactly ONE ```python ... ``` code block.
    2. The code block must contain the ENTIRE file from the first line to the last line.
    3. Include all unchanged code; do not omit anything.
    4. Do not include line numbers.
    5. Do not output diffs, patches, snippets, excerpts, or partial code.
    6. Do not output any other code block.
    7. Do not output Python code outside the single code block.
    8. Do not provide a second code block containing unchanged or partial code.
    The single code block is the authoritative and complete version of the file. 
    """).strip()

    tool_instruction = dedent("""
    Some refactorings can be done by calling a tool. 
    If the refactoring can be done by a tool, you MUST use the tool.
    Otherwise, return the refactored code in the Markdown Python code block.
    """).strip()

    def __init__(self, llm: LLM, count: int = 1):
        self.llm = llm
        self.categories = [
            CONDITIONAL_LOGIC,
            CONTROL_FLOW,
            EXPRESSION,
            METHOD_STRUCTURE,
            CLASS_STRUCTURE,
            CODE_QUALITY,
        ]
        if count > len(self.categories) and count > 0:
            raise ValueError(
                f"Count {count} exceeds the number of available categories {len(self.categories)} or is not positive.")
        self.count = count

    def generate_refactorings(self, code_segment: str, commit_history: list) -> list[Refactoring]:
        """Generate refactorings from different categories for a given code segment using the LLM.

        Args:
            code_segment (str): The code segment to be refactored. 
            filepath (str): The path to the file containing the code segment.
            commit_history (list): A list of previous commits. (This is given to the LLM to prevent repeated refactorings.)

        Raises:
            ValueError: If an unexpected response type is received from the LLM.

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

        tools = [category.get_tools() for category in round_categories]

        prompts = []
        for category in round_categories:
            category_prompt = prompt
            if len(category.get_tools()) > 0:
                category_prompt += "\n" + self.tool_instruction
            category_prompt += "\n" + category.get_prompt()
            prompts.append(category_prompt)

        llm_responses = self.llm.batch_generate(prompts, tools)

        refactorings = []
        for i, response in enumerate(llm_responses):
            if response.text is not None and response.text.strip().endswith("NO_REFACTORING"):
                CLI.print_debug(
                    f"No meaningful refactoring found for {round_categories[i].get_name()}.")
                # Remove the category from future consideration
                self.categories.remove(round_categories[i])
                refactoring = None
            elif response.text is not None:
                refactoring = self.__handle_string_response(
                    response.text, code_segment)
            elif response.tool_call is not None:
                refactoring = self.__handle_tool_call_response(
                    response.tool_call, code_segment)
            else:
                raise ValueError(
                    f"Unexpected response type from LLM: {type(response)}. Response content: {response}")

            if refactoring:
                refactorings.append(refactoring)

        return refactorings

    def __handle_string_response(self, response: str, code_segment: str) -> str | None:
        """ Generate a Refactoring object from a string response from the LLM. """
        try:
            refactored_code = self.extract_python_code(response)
        except ValueError as e:
            CLI.print_debug(
                f"Failed to extract Python code from LLM response: {e}")
            return None
        return Refactoring(code_segment, refactored_code)

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
            else:
                CLI.print_error(
                    f"Received tool call for unknown tool '{tool_call.name}'. Response content: {tool_call}")
                return None
        except Exception as e:
            CLI.print_error(
                f"An error occurred while handling the tool call: {e}")
            return None

    # Needs to be public for unit tests
    def extract_python_code(self, text: str) -> str:
        """ Extract Python code from a string that contains a code block wrapped in markdown markers. """
        start_marker = "```python"
        end_marker = "```"

        # there need to be 2 end markers in the text because the start_marker also contains the end_marker
        if text.count(start_marker) != 1 or text.count(end_marker) != 2:
            raise ValueError(
                f"Input text contains {text.count(start_marker)} start markers and {text.count(end_marker)} end markers. Expected exactly 1 start marker and 2 end markers.")

        start_index = text.find(start_marker) + len(start_marker)
        # have to look after the start_index to find the correct end_marker
        end_index = text.find(end_marker, start_index)

        python_code = text[start_index:end_index].strip()

        return python_code

    def __add_line_numbers(self, code: str) -> str:
        lines = code.split("\n")
        numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered_lines)
