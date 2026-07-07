from typing import List
from openai.types.chat import ChatCompletionMessageFunctionToolCall 
import json
from tqdm import tqdm
from dataclasses import dataclass

from refactoring.multi_rename_refactoring import RenameArguments, MultiRenameTool
from refactoring.refactoring import Refactoring
from refactoring.rename_refactoring import RenameTool
from refactoring.extract_method_refactoring import ExtractMethodTool
from llm.llm_types import ToolCall
from utility.cli import CLI
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config
from tree_of_thoughts.generator_prompts import header, with_tools_return_instruction, without_tools_return_instruction, control_flow, footer, method_structure, expression, type_documentation, naming

@dataclass
class PromptWithTools:
    prompt: str
    tools: List[dict]


class RefactoringGenerator:
    prompts_with_tools = [
        PromptWithTools(prompt=header.format(return_instruction=without_tools_return_instruction)+control_flow+footer, tools=[]),
        PromptWithTools(prompt=header.format(return_instruction=with_tools_return_instruction)+method_structure+footer, tools=[ExtractMethodTool.get_description()]),
        PromptWithTools(prompt=header.format(return_instruction=without_tools_return_instruction)+expression+footer, tools=[]),
        PromptWithTools(prompt=header.format(return_instruction=without_tools_return_instruction)+type_documentation+footer, tools=[]),
        PromptWithTools(prompt=header.format(return_instruction=with_tools_return_instruction)+naming+footer, tools=[MultiRenameTool.get_description()]),
    ]

    def __init__(self, llm):
        self.llm = llm

    def generate_refactorings(self, code_segment: str, count: int, filepath: str, commit_history: list) -> List[Refactoring]:

        refactorings = []
        for i in tqdm(range(len(self.prompts_with_tools)), desc="Generating refactorings"):
            tools = self.prompts_with_tools[i].tools
            generator_llm = OpenAILLM(config=big_pickle_config, tools=tools)

            prompt = self.prompts_with_tools[i].prompt.format(code_segment=self.add_line_numbers(code_segment), commit_history=commit_history)
            response = generator_llm.generate(prompt)

            if response.text is "NO_REFACTORING":
                CLI.print_debug(f"No meaningful refactoring found for prompt {i + 1}.")
                refactoring = None
            elif response.text is not None:
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
        return Refactoring(filepath, code_segment, refactored_code)
    
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