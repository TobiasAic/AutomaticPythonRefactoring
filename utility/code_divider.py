import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider
import re

class CodeDivider:
    def __init__(self, code: str):
        self.code = code
        self.segments = self.divide_code(code)

    def get_segments(self) -> list[str]:
        """Get the code in segments of single functions, classes and the code in-between.

        Returns:
            list[str]: A list of code segments, each representing a function, class, or intermediate code snippet. 
        """
        return self.segments

    def get_code(self) -> str:
        return self.code

    def replace_segment(self, old_segment: str, new_segment: str) -> None:
        """Replace a specific code segment with a new segment in the original code.

        Args:
            old_segment (str): The code segment to be replaced. 
            new_segment (str): The new code segment to replace the old one. 
        """
       # Escape special characters in the old code segment to create a safe regex pattern
        pattern = re.escape(old_segment)

        # Prepare the new segment for replacement, escaping backslashes and other potential escape sequences
        # This step might need adjustment based on how new_segment is provided
        safe_new_segment = new_segment.replace('\\', '\\\\')

        # Replace the old segment with the new, safe segment using regex
        replaced_code = re.sub(pattern, safe_new_segment, self.code, flags=re.DOTALL)
        self.code = replaced_code

    def divide_code(self, code: str) -> list: # This function is from Siegwardt's system
        """Divides the given code into functions, classes, and intermediate code snippets.

        Args:
            code (str): The code to be divided. 

        Returns:
            list: A list containing the divided functions, classes, and intermediate code snippets.
        """
        cst_tree = cst.parse_module(code)
        wrapper = MetadataWrapper(cst_tree)
        wrapper.resolve(PositionProvider)

        functions = []
        classes = []
        intermediate_code = []
        last_line = 0
        function_depth = 0  # Track the depth of nested functions
        current_indentation = 0  # Track the current indentation level

        class FunctionClassVisitor(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (PositionProvider,)

            def visit_IndentedBlock(self, node: cst.IndentedBlock) -> bool:
                nonlocal current_indentation
                current_indentation += 1
                return True  # Continue visiting children

            def leave_IndentedBlock(self, original_node: cst.IndentedBlock) -> None:
                nonlocal current_indentation
                current_indentation -= 1

            def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
                nonlocal last_line, function_depth
                function_depth += 1

                # Process only top-level functions (not inside classes)
                if function_depth == 1 and current_indentation == 0:
                    start_line = self.get_metadata(PositionProvider, node).start.line
                    end_line = self.get_metadata(PositionProvider, node).end.line

                    # Adjust start_line to include decorators
                    while start_line > 1 and code.splitlines()[start_line - 2].strip().startswith('@'):
                        start_line -= 1

                    if start_line > last_line + 1:
                        intermediate_snippet = '\n'.join(code.splitlines()[last_line:start_line - 1]).strip()
                        if intermediate_snippet:
                            intermediate_code.append(intermediate_snippet)

                    function_code = '\n'.join(code.splitlines()[start_line - 1:end_line]).strip()
                    functions.append(function_code)
                    last_line = end_line

                # Do not descend into nested functions
                return function_depth == 1

            def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
                nonlocal function_depth
                function_depth -= 1

            def visit_ClassDef(self, node: cst.ClassDef) -> None:
                nonlocal last_line
                start_line = self.get_metadata(PositionProvider, node).start.line
                end_line = self.get_metadata(PositionProvider, node).end.line

                # Adjust start_line to include decorators
                while start_line > 1 and code.splitlines()[start_line - 2].strip().startswith('@'):
                    start_line -= 1

                if start_line > last_line + 1:
                    intermediate_snippet = '\n'.join(code.splitlines()[last_line:start_line - 1]).strip()
                    if intermediate_snippet:
                        intermediate_code.append(intermediate_snippet)

                class_code = '\n'.join(code.splitlines()[start_line - 1:end_line]).strip()
                classes.append(class_code)
                last_line = end_line

        visitor = FunctionClassVisitor()
        wrapper.visit(visitor)

        # Capture any remaining code after the last function/class
        lines = code.splitlines()
        if last_line < len(lines):
            remaining_code = '\n'.join(lines[last_line:]).strip()
            if remaining_code:
                intermediate_code.append(remaining_code)

        return functions + classes + intermediate_code 