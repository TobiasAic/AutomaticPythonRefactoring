from dataclasses import dataclass


@dataclass
class CodeBlock:
    start_line: int # inclusive
    end_line: int # inclusive

    def length(self) -> int:
        return self.end_line - self.start_line + 1


class CodeSegmentation:
    """A mutable partition of `code_line_count` lines into adjacent, gapless CodeBlocks.

    Starts as a single block spanning every line. `split_at` and
    `merge_with_next` carve it up or recombine it; `__ensure_valid_segments`
    runs after every mutation to guarantee the blocks always stay contiguous
    and in order, with no gaps or overlaps.
    """

    def __init__(self, code_line_count: int):
        self.code_line_count = code_line_count
        self.code_blocks = [CodeBlock(0, code_line_count - 1)]
        self.__ensure_valid_segments()

    def first(self) -> CodeBlock | None:
        """Returns the first block, or None if there are no blocks."""
        return self.code_blocks[0] if self.code_blocks else None

    def next(self, block: CodeBlock) -> CodeBlock | None:
        """Returns the block immediately after `block`, or None if it is the last one."""
        i = self.__index_of(block)
        return self.code_blocks[i + 1] if i + 1 < len(self.code_blocks) else None

    def prev(self, block: CodeBlock) -> CodeBlock | None:
        """Returns the block immediately before `block`, or None if it is the first one."""
        i = self.__index_of(block)
        return self.code_blocks[i - 1] if i > 0 else None

    def split_at(self, line: int):
        if line <= 0 or line >= self.code_line_count:
            raise ValueError(f"Line {line} is out of bounds for code with {self.code_line_count} lines.")

        for i, block in enumerate(self.code_blocks):
            if block.start_line < line <= block.end_line:
                new_block = CodeBlock(line, block.end_line)
                self.code_blocks[i].end_line = line - 1
                self.code_blocks.insert(i + 1, new_block)
                break

        self.__ensure_valid_segments()

    def merge_with_next(self, block: CodeBlock) -> CodeBlock:
        """Merges `block` with its successor and returns `block` (now spanning both).

        Operates on block identity rather than a positional index, so it stays
        correct even while you're walking the segmentation and merging as you go.
        """
        i = self.__index_of(block)
        if i + 1 >= len(self.code_blocks):
            raise ValueError("Block has no next block to merge with.")

        block.end_line = self.code_blocks[i + 1].end_line
        del self.code_blocks[i + 1]

        self.__ensure_valid_segments()
        return block

    def get_blocks(self) -> list[CodeBlock]:
        return list(self.code_blocks)

    def __index_of(self, block: CodeBlock) -> int:
        for i, b in enumerate(self.code_blocks):
            if b is block:
                return i
        raise ValueError("Block is not part of this segmentation.")

    def __ensure_valid_segments(self):
        for i in range(len(self.code_blocks) - 1):
            if self.code_blocks[i].end_line != self.code_blocks[i + 1].start_line - 1:
                raise ValueError(f"Segments {i} and {i + 1} are not properly adjacent.")
