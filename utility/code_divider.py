import difflib

import libcst as cst
from libcst.metadata import CodePosition, CodeRange, PositionProvider


class CodeDivider:
    def __init__(self, code: str, max_lines: int = 250):
        self.segments = self.__divide_code(code, max_lines)

    def get_segments_with_id(self) -> dict[int, str]:
        """Returns a dictionary mapping segment IDs to code segments."""
        return {i: segment for i, segment in enumerate(self.segments)}

    def get_number_of_segments(self) -> int:
        """Returns the number of code segments."""
        return len(self.segments)

    def get_code(self) -> str:
        """ Returns the complete code reconstructed from the segments. """
        return ''.join(self.segments)

    def __count_trailing_newlines(self, code: str) -> int:
        """Counts the number of trailing newline characters in a string."""
        count = 0
        for char in reversed(code):
            if char == '\n':
                count += 1
            else:
                break
        return count

    def replace_segment(self, segment_id: int, new_segment: str, remember: bool = True) -> str:
        """Replaces a code segment at the specified index with a new segment and returns the complete code.

        Args:
            segment_id: The index of the segment to replace.
            new_segment: The new code segment.
            remember: If True, persist the replacement in self.segments.

        Returns:
            The complete code reconstructed from the updated segments.
        """
        if segment_id < 0 or segment_id >= len(self.segments):
            raise IndexError(
                f"Segment ID {segment_id} is out of range. Valid range is 0 to {len(self.segments) - 1}.")

        old_trailing_newline = self.__count_trailing_newlines(self.segments[segment_id])
        new_segment = new_segment.rstrip("\n") + "\n" * old_trailing_newline 

        updated_segments = self.segments.copy()
        updated_segments[segment_id] = new_segment

        if remember:
            self.segments = updated_segments

        return "".join(updated_segments)

    def __divide_code(self, code: str, max_lines: int = 250) -> list:
        atomic_blocks = self.__divide_into_atomic_blocks(code)
        merged_atomic_blocks = self.__merge_empty_blocks(atomic_blocks)
        return self.__merge_to_aproximate_size(merged_atomic_blocks, max_lines)

    def __merge_to_aproximate_size(self, blocks: list[str], max_lines: int) -> list[str]:
        """ Merges blocks to ensure that each block has approximately max_lines lines. """
        merged_blocks = []
        current_block = ""

        for block in blocks:
            if len(current_block.splitlines()) + len(block.splitlines()) <= max_lines:
                current_block += block
            else:
                if current_block:
                    merged_blocks.append(current_block)
                current_block = block

        if current_block:
            merged_blocks.append(current_block)

        return merged_blocks

    def __merge_empty_blocks(self, blocks: list[str]) -> list[str]:
        """ Merges empty blocks with their preceding non-empty block. """
        merged_blocks = []
        for block in blocks:
            if block.strip() == "":
                if merged_blocks:
                    merged_blocks[-1] += block  # Merge with the last non-empty block
                else:
                    merged_blocks.append(block)  # If it's the first block, just add it
            else:
                merged_blocks.append(block)
        return merged_blocks

    def __divide_into_atomic_blocks(self, code: str) -> list[str]:
        definition_ranges = self.__find_function_and_class_positions(code)
        lines = code.splitlines(keepends=True)

        atomic_blocks = []
        start_line = 1
        for definition_range in definition_ranges:
            # Add the code before the definition as a separate block
            if start_line < definition_range.start.line:
                atomic_blocks.append("".join(lines[start_line - 1:definition_range.start.line - 1]))

            # Add the definition itself as a separate block
            atomic_blocks.append("".join(lines[definition_range.start.line - 1:definition_range.end.line]))

            start_line = definition_range.end.line + 1

        # Add any remaining code after the last definition as a separate block
        if start_line <= len(lines):
            atomic_blocks.append("".join(lines[start_line - 1:len(lines)]))

        return atomic_blocks 

    def __find_function_and_class_positions(self, code: str) -> list[CodeRange]:
        """ Finds the start and end positions of function and class definitions in the code, including decorators, leading and trailing comments. """
        tree = cst.parse_module(code)
        wrapper = cst.MetadataWrapper(tree, unsafe_skip_copy=True)
        positions = wrapper.resolve(PositionProvider)

        lines = code.splitlines(keepends=True)

        definition_ranges: list[CodeRange] = []

        for statement in tree.body:
            if isinstance(statement, (cst.ClassDef, cst.FunctionDef)):
                position = positions[statement]
                start = position.start
                end = position.end

                # adjust start_line if there are decorators, to include them in the definition.
                if statement.decorators:
                    start = positions[statement.decorators[0]].start

                # adjust start_line to include preceding comments, if any.
                start_line = start.line - 1
                while start_line > 0:
                    previous_line = lines[start_line - 1]

                    if previous_line.lstrip().startswith("#"):
                        start = CodePosition(line=start_line, column=0)
                        start_line -= 1
                    else:
                        break

                # If the end line has a comment, include it in the definition.
                current_end_line = lines[end.line - 1] 
                if current_end_line[end.column:].strip().startswith("#"):
                    end = CodePosition(line=end.line, column=len(current_end_line.rstrip("\r\n")))

                definition_ranges.append(CodeRange(start=start, end=end))

        return definition_ranges

    def print_segments(self):
        """Prints the code segments with their corresponding IDs."""
        for i, segment in enumerate(self.segments):
            print(f"Segment {i}:\n{segment}{'-'*40}")


if __name__ == "__main__":
    # /home/tobias/Desktop/requests/requests-2.34.2/src/requests/utils.py
    # tests/test_files/example.py
    with open("/home/tobias/Desktop/requests/requests-2.34.2/src/requests/utils.py", "r") as f:
        code_file = f.read()

    code_divider = CodeDivider(code_file, max_lines=250)

    code_divider.print_segments()

    new_code = code_divider.get_code()
    print(len(code_file.splitlines()), "lines in original code")
    print(len(new_code.splitlines()), "lines in new code")

    import difflib

    print(
        "".join(
            difflib.unified_diff(code_file.splitlines(1), code_divider.get_code().splitlines(1))
        )
    )

    """
    with open("test1.txt", "r") as f:
       old_code = f.read() 

    old_code  = code_divider.get_segments()[0]  # Get the first segment for testing
    
    with open("test2.txt", "r") as f:
       new_code = f.read()

    code_divider.replace_segment(old_code, new_code)

    import difflib

    print(
        "".join(
            difflib.unified_diff(code_file.splitlines(1), code_divider.get_code().splitlines(1))
        )
    )
    """
