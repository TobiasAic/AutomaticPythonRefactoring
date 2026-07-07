from typing import List
from openai.types.chat import ChatCompletionMessageFunctionToolCall 
import json
from tqdm import tqdm

from refactoring.multi_rename_refactoring import RenameArguments, MultiRenameTool
from refactoring.refactoring import Refactoring
from refactoring.free_edit_refactoring import FreeEditRefactoring
from refactoring.rename_refactoring import RenameTool
from refactoring.extract_method_refactoring import ExtractMethodTool
from llm.llm_types import ToolCall
from utility.cli import CLI
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config

class RefactoringGenerator:
    prompt = """
    This is a complete Python file which is part of a larger library. Try to improve its readability by applying a single, small refactoring. 

    Here are some of the refactorings you can do ranked by priority:
    1. Try to reduce the complexity of nested conditions.
    2. Try to shorten methods that are too long by splitting them up into smaller ones
    3. Add type hints to function signatures if they are missing
    4. Rename local variables to more descriptive names if they are not clear
    5. Add a descriptive docstring for every method if missing or incomplete

    You MUST NOT:
    - Change the functionality of the code in any way. The code must behave exactly the same after your changes.
    - Rename functions, their parameters, or class names. 
    - Add any import statements.

    {return_message}

    Here are the refactorings you have already done in the past:
    {commit_history}
    Do not repeat the same or similar refactorings in the same places again.

    {code_segment}
    """

    return_with_tools = """
    Some refactorings can be done by calling a tool. If the refactoring can be done by a tool, you MUST use the tool.
    If the refactoring can't be done by a tool, return the refactored in a Markdown Python code block (without line numbers):
    ```python
        ...some python code...
    ```
    """

    return_without_tools = """
    Return the refactored code in a Markdown Python code block (without line numbers):
    ```python
        ...some python code...
    ```
    """

    def __init__(self, llm):
        self.llm = llm

    def generate_refactorings(self, code_segment: str, count: int, filepath: str, commit_history: list) -> List[Refactoring]:

        refactorings = []
        for i in tqdm(range(count), desc="Generating refactorings"):
            tools = [RenameTool.get_description(), ExtractMethodTool.get_description(), MultiRenameTool.get_description()] if i % 2 == 0 else []

            generator_llm = OpenAILLM(config=big_pickle_config, tools=tools)
            return_message = self.return_with_tools if len(tools) > 0 else self.return_without_tools
            prompt = self.prompt.format(code_segment=self.add_line_numbers(code_segment), commit_history=commit_history, return_message=return_message)
            print(f"Generating with {len(tools)} tools. Prompt length: {len(prompt)} characters.")
            response = generator_llm.generate(prompt)

            if response.text is not None:
                refactoring = self.handle_string_response(response.text, code_segment, filepath)
            elif response.tool_call is not None:
                refactoring = self.handle_tool_call_response(response.tool_call, filepath)
            else:
                raise ValueError(f"Unexpected response type from LLM: {type(response)}. Response content: {response}")

            if refactoring:
                refactorings.append(refactoring)

        return refactorings
    
    def handle_string_response(self, response: str, code_segment: str, filepath: str) -> str|None:
        try:
            refactored_code = self.extract_python_code(response)
        except ValueError as e:
            CLI.print_debug(f"Failed to extract Python code from LLM response: {response}")
            return None
        return FreeEditRefactoring(filepath, code_segment, refactored_code)
    
    def handle_tool_call_response(self, tool_call: ToolCall, filepath: str) -> Refactoring|None:
        arguments = json.loads(tool_call.arguments)
        if tool_call.name == "rename":
            CLI.print_debug(f"Received tool call for 'rename' with arguments: {arguments}")
            line_number = int(arguments.get("line_number"))
            old_name = arguments.get("old_name")
            new_name = arguments.get("new_name")
            try:
                return RenameTool.call(filepath=filepath, line_number=line_number, old_name=old_name, new_name=new_name)
            except Exception as e:
                return None
        if tool_call.name == "extract_method":
            CLI.print_debug(f"Received tool call for 'extract_method' with arguments: {arguments}")
            start_line = int(arguments.get("start_line"))
            end_line = int(arguments.get("end_line"))
            new_name = arguments.get("new_name")
            try:
                return ExtractMethodTool.call(filepath=filepath, start_line=start_line, end_line=end_line, new_name=new_name)
            except Exception as e:
                return None
        if tool_call.name == "multi_rename":
            CLI.print_debug(f"Received tool call for 'multi_rename' with arguments: {arguments}")
            changes = arguments.get("changes", [])
            rename_arguments = []
            for change in changes:
                line_number = int(change.get("line_number"))
                old_name = change.get("old_name")
                new_name = change.get("new_name")
                rename_arguments.append(RenameArguments(line_number=line_number, old_name=old_name, new_name=new_name))
            try:
                return MultiRenameTool.call(filepath=filepath, rename_arguments=rename_arguments)
            except Exception as e:
                return None
        else:
            CLI.print_error(f"Received tool call for unknown tool '{tool_call.name}'. Response content: {tool_call}")
            return None
    
    def extract_python_code(self, text: str) -> str:
        start_marker = "```python"
        end_marker = "```"

        # there need to be 2 end markers in the text because the start_marker also contains the end_marker
        if text.count(start_marker) != 1 or text.count(end_marker) != 2:
            raise ValueError("Input text does not contain exactly one pair of start and end markers.")
        
        start_index = text.find(start_marker) + len(start_marker)
        end_index = text.find(end_marker, start_index) # have to look after the start_index to find the correct end_marker

        python_code = text[start_index:end_index].strip()

        return python_code
    
    def add_line_numbers(self, code: str) -> str:
        lines = code.split("\n")
        numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered_lines)