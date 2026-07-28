from typing import List
import json
from dataclasses import dataclass
from textwrap import dedent

from refactoring.multi_rename_refactoring import MultiRenameTool
from refactoring.refactoring import Refactoring
from refactoring.rename_refactoring import RenameTool
from refactoring.extract_method_refactoring import ExtractMethodTool
from llm.llm_types import ToolCall
from utility.cli import CLI
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config
from llm.llm import LLM
from tree_of_thoughts.refactoring_category import ControlFlowCategory, MethodStructureCategory, ExpressionCategory, TypeDocumentationCategory, NamingCategory

class RefactoringGenerator:
    prompt = dedent("""
    You are generating a refactoring candidate for a Python file to improve readability.

    This is the Python file to refactor:
    {code_segment}

    Find exactly one small refactoring from the category specified below.

    The refactoring must:
    - Improve readability.
    - Preserve behavior exactly.
    - Avoid changing public APIs.
    - Avoid adding imports.
    - Avoid renaming functions, parameters, or classes.
    - Not repeat a refactoring already performed in the commit history.

    Commit history:
    {commit_history}

    Prefer a real readability improvement over a cosmetic change.

    If there is no refactoring in that category that significantly improves readability, return "NO_REFACTORING".

    If you find a refactoring return the refactored code in a Markdown Python code block (without line numbers).
    You have to return the entire file with your changes.
    ```python
        ...some python code...
    ```
    """).strip()

    tool_instruction = dedent("""
    Some refactorings can be done by calling a tool. 
    If the refactoring can be done by a tool, you MUST use the tool.
    Otherwise, return the refactored code in the Markdown Python code block.
    """).strip()

    def __init__(self, llm: LLM):
        self.llm = llm
        self.categories = [ControlFlowCategory(), MethodStructureCategory(), ExpressionCategory(), TypeDocumentationCategory(), NamingCategory()]

    def generate_refactorings(self, code_segment: str, filepath: str, commit_history: list) -> List[Refactoring]:
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

        tools = [category.get_tools() for category in self.categories]

        prompts = []
        for category in self.categories:
            category_prompt = prompt 
            if len(category.get_tools()) > 0:
                category_prompt += "\n" + self.tool_instruction
            category_prompt += "\n" + category.get_prompt()
            prompts.append(category_prompt)


        llm_responses = self.llm.batch_generate(prompts, tools)

        refactorings = []
        for i, response in enumerate(llm_responses): 
            if response.text == "NO_REFACTORING":
                CLI.print_debug(f"No meaningful refactoring found for {self.categories[i].get_name()}.")
                self.categories.pop(i)
                refactoring = None
            elif response.text is not None:
                refactoring = self.__handle_string_response(response.text, code_segment, filepath)
            elif response.tool_call is not None:
                refactoring = self.__handle_tool_call_response(response.tool_call, filepath)
            else:
                raise ValueError(f"Unexpected response type from LLM: {type(response)}. Response content: {response}")

            if refactoring:
                refactorings.append(refactoring)

        return refactorings
    
    def __handle_string_response(self, response: str, code_segment: str, filepath: str) -> str|None:
        """ Generate a Refactoring object from a string response from the LLM. """
        try:
            refactored_code = self.__extract_python_code(response)
        except ValueError as e:
            CLI.print_debug(f"Failed to extract Python code from LLM response: {response}")
            return None
        return Refactoring(filepath, code_segment, refactored_code)
    
    def __handle_tool_call_response(self, tool_call: ToolCall, filepath: str) -> Refactoring|None:
        """ Generate a Refactoring object from a tool call response from the LLM. """
        arguments = json.loads(tool_call.arguments)
        CLI.print_debug(f"Received tool call for '{tool_call.name}' with arguments: {arguments}")
        try:
            if tool_call.name == "rename":
                    return RenameTool.call(filepath=filepath, arguments=arguments)
            if tool_call.name == "extract_method":
                    return ExtractMethodTool.call(filepath=filepath, arguments=arguments)
            if tool_call.name == "multi_rename":
                    return MultiRenameTool.call(filepath=filepath, arguments=arguments)
            else:
                CLI.print_error(f"Received tool call for unknown tool '{tool_call.name}'. Response content: {tool_call}")
                return None
        except Exception as e:
            CLI.print_error(f"An error occurred while handling the tool call: {e}")
            return None

    
    def extract_python_code(self, text: str) -> str: # Needs to be public for unit tests
        """ Extract Python code from a string that contains a code block wrapped in markdown markers. """
        start_marker = "```python"
        end_marker = "```"

        # there need to be 2 end markers in the text because the start_marker also contains the end_marker
        if text.count(start_marker) != 1 or text.count(end_marker) != 2:
            raise ValueError("Input text does not contain exactly one pair of start and end markers.")
        
        start_index = text.find(start_marker) + len(start_marker)
        end_index = text.find(end_marker, start_index) # have to look after the start_index to find the correct end_marker

        python_code = text[start_index:end_index].strip()

        return python_code
    
    def __add_line_numbers(self, code: str) -> str:
        lines = code.split("\n")
        numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered_lines)