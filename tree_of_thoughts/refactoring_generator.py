from typing import List
import logging
from openai.types.chat import ChatCompletionMessageFunctionToolCall 
import json

from refactoring.refactoring import Refactoring
from refactoring.free_edit_refactoring import FreeEditRefactoring
from refactoring.rename_refactoring import RenameRefactoringTool
from refactoring.extract_method_refactoring import ExtractMethodTool

class RefactoringGenerator:
    prompt = """
    This is a complete Python file which is part of a larger library. Try to improve its readability by applying the following principles (if possible):

    1. Try to reduce the complexity of nested conditions.
    2. Try to shorten methods that are too long by splitting them up into smaller ones.
    3. In case if variables inside methods (that only have impact on the part of code we are editing) are named in a bad way, rename them.
    4. Add a docstring for every method and add a comment to every line of code.
    5. Ensure that code modifications are wrapped in Markdown's python code block syntax:

    ```python
        ...some python code...
    ```

    6. Do not rename the name of the function or method itself. Only rename variables that are defined inside the method or function. If you
    rename anything, make sure that the scope does not extend to other parts of the code.
    7. Most importantly, ensure that these changes do not break integration with the larger library.
    8. Do not add any 'import' statements in your response. This also means that you must not add any new functionalities
    to the code that depend on such 'import' statements.
    9. Do not create new classes or rename old ones. Only edit existing ones if needed.

    Return the complete code with only a single, small refactoring applied that improves readability. 
    Do not apply multiple refactorings at once, only one of the size of a regular commit.
    The code you return needs to be complete and have the same functionality as the original code.

    You also have tools for refactoring available.

    Prioritize the refactorings that have the biggest impact on the readability of the code. 
    If you think that there are multiple applicable refactorings, choose the one that has the biggest impact on readability.
    If a refactoring can be carried out by a tool, always use the tool instead of doing a free edit refactoring.

    {code_segment}
    """

    def __init__(self, llm):
        self.llm = llm

    def generate_refactorings(self, code_segment: str, count: int, filepath: str) -> List[Refactoring]:
        prompt = self.prompt.format(code_segment=self.add_line_numbers(code_segment))

        refactorings = []
        for i in range(count):
            response = self.llm.generate(prompt)

            if type(response) == str:
                refactoring = self.handle_string_response(response, code_segment, filepath)
            elif type(response) == ChatCompletionMessageFunctionToolCall:
                refactoring = self.handle_tool_call_response(response, filepath)
            else:
                raise ValueError(f"Unexpected response type from LLM: {type(response)}. Response content: {response}")

            if refactoring:
                refactorings.append(refactoring)

        return refactorings
    
    def handle_string_response(self, response: str, code_segment: str, filepath: str) -> str|None:
        try:
            refactored_code = self.extract_python_code(response)
        except ValueError as e:
            logger = logging.getLogger(f"refactoring.{__name__}")
            logger.debug(f"Failed to extract Python code from LLM response: {response}")
            return None
        return FreeEditRefactoring(filepath, code_segment, refactored_code)
    
    def handle_tool_call_response(self, tool_call: ChatCompletionMessageFunctionToolCall, filepath: str) -> Refactoring|None:
        logger = logging.getLogger(f"refactoring.{__name__}")
        arguments = json.loads(tool_call.function.arguments)
        if tool_call.function.name == "rename_refactoring":
            logger.debug(f"Received tool call for 'rename_refactoring' with arguments: {arguments}")
            line_number = int(arguments.get("line_number"))
            old_name = arguments.get("old_name")
            new_name = arguments.get("new_name")
            return RenameRefactoringTool.call(filepath=filepath, line_number=line_number, old_name=old_name, new_name=new_name)
        if tool_call.function.name == "extract_method":
            logger.debug(f"Received tool call for 'extract_method' with arguments: {arguments}")
            start_line = int(arguments.get("start_line"))
            end_line = int(arguments.get("end_line"))
            new_name = arguments.get("new_name")
            return ExtractMethodTool.call(filepath=filepath, start_line=start_line, end_line=end_line, new_name=new_name) 
        else:
            logger.debug(f"Received tool call for unknown tool '{tool_call.function.name}'. Response content: {tool_call}")
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