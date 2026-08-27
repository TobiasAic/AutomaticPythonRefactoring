from utility.cli import CLI
from utility.code_divider import CodeDivider, CodeSegment
from utility.code_labeler import CodeLabeler
from utility.code_segmentation import CodeBlock, CodeSegmentation


class BalancedCodeDivider(CodeDivider):
    def __init__(self, approximate_lines: int = 500):
        self.approximate_lines = approximate_lines
        self.labeler = CodeLabeler()
        self.max_lines = None

    def divide(self, code: str) -> list[CodeSegment]:
        lines = code.splitlines(keepends=True)
        num_segments, max_lines = self._compute_target_segmentation(
            len(lines), self.approximate_lines)
        self.max_lines = max_lines

        labels = self.labeler.compute_labels(code)
        segmentation = self.split_in_segments(labels, max_lines, num_segments)
        segments = [
            CodeSegment(id=i, code="".join(
                lines[block.start_line:block.end_line + 1]))
            for i, block in enumerate(segmentation.get_blocks())
        ]

        self.__check_correct_segmentation(code, segments)
        return segments

    def __check_correct_segmentation(self, given_code: str, segments: list[CodeSegment]):
        if "".join(segment.code for segment in segments) != given_code:
            CLI.print_error(
                f"Code was incorrectly divided into {len(segments)} segments.")

    def _compute_target_segmentation(self, total_lines: int, approximate_lines: int) -> tuple[int, int]:
        """Picks a target segment count and a size cap close to approximate_lines.

        num_segments is how many pieces the file would end up in at roughly
        approximate_lines each; max_lines is the resulting even share, used as
        a hard ceiling (e.g. so no single block ever gets subdivided smaller
        than it needs to be). merge_blocks uses num_segments to keep rebalancing
        toward an even split as it goes, rather than just packing greedily up
        to max_lines and leaving whatever's left as a small final segment.
        """
        num_segments = max(1, round(total_lines / approximate_lines))
        # ceil(total_lines / num_segments)
        max_lines = -(-total_lines // num_segments)
        return num_segments, max_lines

    def split_in_segments(self, labels: list[tuple[str]], max_lines: int = 250, num_segments: int = 1) -> CodeSegmentation:
        blocks = self.split_in_blocks(labels)

        for block in blocks.get_blocks():
            if block.length() > max_lines:
                self.subdivide_block(labels, blocks, block, max_lines)

        segments = self.merge_blocks(blocks, max_lines, num_segments)

        return segments

    def split_in_blocks(self, labels: list[tuple[str]]) -> CodeSegmentation:
        """Splits labeled source lines into atomic top-level blocks.

        A block is a maximal run of lines belonging to the same top-level
        statement group, class, or function - identified by the first element
        of each line's label tuple ("s", "c(Name)", or "f(Name)"). Empty lines
        ("e") take on the label of the following non-empty line, so a blank
        line between two blocks is attached to the block that comes after it,
        while a blank line inside a block just stays part of that block.
        """
        segmentation = CodeSegmentation(len(labels))
        self._split_by_depth_key(labels, 0, len(
            labels) - 1, depth=0, segmentation=segmentation)
        return segmentation

    def _split_by_depth_key(self, labels: list, start: int, end: int, depth: int, segmentation: CodeSegmentation):
        """Splits lines [start, end] wherever the label key at `depth` changes.

        Blank lines take on the key of the following non-blank line (or, for
        trailing blanks with nothing after them, the preceding line's key),
        exactly like the top-level split in split_in_blocks - just applied to
        one nesting level at a time.
        """
        n = end - start + 1
        is_blank = [labels[start + i] == "e" for i in range(n)]
        keys = [None if is_blank[i] else self.labeler.key_at_depth(
            labels[start + i], depth) for i in range(n)]

        next_key = None
        for i in reversed(range(n)):
            if is_blank[i]:
                keys[i] = next_key
            else:
                next_key = keys[i]

        prev_key = None
        for i in range(n):
            if is_blank[i]:
                if keys[i] is None:
                    keys[i] = prev_key
            else:
                prev_key = keys[i]

        for i in range(1, n):
            if keys[i] != keys[i - 1]:
                segmentation.split_at(start + i)

    def subdivide_block(self, labels: list[tuple[str]], blocks: CodeSegmentation, block: CodeBlock, max_lines: int, depth: int = 1):
        """Recursively splits an oversized block until every piece fits in max_lines.

        First tries to divide between the block's direct subfunctions/subclasses
        (one nesting level deeper than however this block itself was found).
        If that finds no boundaries - i.e. the block is just statements with no
        nested defs - it falls back to splitting on empty lines, and if there
        are none of those either, to a hard cut every max_lines lines.
        """
        if block.length() <= max_lines:
            return

        original_end_line = block.end_line
        blocks_before = len(blocks.get_blocks())
        self._split_by_depth_key(
            labels, block.start_line, original_end_line, depth, blocks)

        if len(blocks.get_blocks()) == blocks_before:
            self._split_on_empty_lines_or_max_lines(
                labels, blocks, block, max_lines)
            return

        current = block
        while current is not None and current.start_line <= original_end_line:
            if current.length() > max_lines:
                self.subdivide_block(
                    labels, blocks, current, max_lines, depth + 1)
            current = blocks.next(current)

    def _split_on_empty_lines_or_max_lines(self, labels: list, blocks: CodeSegmentation, block: CodeBlock, max_lines: int):
        original_end_line = block.end_line

        for i in range(block.start_line + 1, original_end_line + 1):
            if labels[i] == "e" and labels[i - 1] != "e":
                blocks.split_at(i)

        current = block
        while current is not None and current.start_line <= original_end_line:
            if current.length() > max_lines:
                blocks.split_at(current.start_line + max_lines)
                continue
            current = blocks.next(current)

    def merge_blocks(self, blocks: CodeSegmentation, max_lines: int, num_segments: int = 1) -> CodeSegmentation:
        """Merges adjacent blocks into num_segments roughly-equal segments.

        A plain "pack greedily up to max_lines" pass can overshoot on an early
        segment and strand a small leftover at the end, since it never looks
        back at what's left to fill. Instead, after closing each segment the
        target for the next one is recomputed from what's actually remaining
        (remaining_lines / remaining_segments), so a segment that came out
        smaller than average raises the bar for the ones after it - self
        correcting instead of committing to one static number for the whole
        file. max_lines is still respected everywhere as a hard ceiling.
        """
        remaining_lines = sum(block.length() for block in blocks.get_blocks())
        remaining_segments = num_segments

        current = blocks.first()
        while current is not None:
            target = remaining_lines / remaining_segments

            next_block = blocks.next(current)
            while next_block is not None and current.length() + next_block.length() <= max_lines and (
                remaining_segments <= 1 or current.length() + next_block.length() <= target
            ):
                current = blocks.merge_with_next(current)
                next_block = blocks.next(current)

            remaining_lines -= current.length()
            remaining_segments = max(1, remaining_segments - 1)
            current = blocks.next(current)

        # The block sizes don't always divide evenly under max_lines - e.g. no
        # merge point lands close enough to the target - which can still leave
        # the segmentation with more than num_segments pieces. Rather than
        # strand the excess at the end, repeatedly merge whichever adjacent
        # pair is currently smallest, spreading the necessary overshoot across
        # the file instead of dumping it all into one oversized tail segment.
        while len(blocks.get_blocks()) > num_segments:
            current_blocks = blocks.get_blocks()
            cheapest = min(
                range(len(current_blocks) - 1),
                key=lambda i: current_blocks[i].length(
                ) + current_blocks[i + 1].length(),
            )
            blocks.merge_with_next(current_blocks[cheapest])

        return blocks

    def print_segmented_code(self, source: str, blocks: CodeSegmentation):
        lines = source.splitlines(keepends=True)
        for i, block in enumerate(blocks.get_blocks()):
            print(
                f"Segment {i + 1} (lines {block.start_line + 1}-{block.end_line + 1}):")
            print("".join(lines[block.start_line:block.end_line + 1]))
            print("-" * 40)


if __name__ == "__main__":
    test_files = [
        "/home/tobias/Desktop/code_repositories/PythonRefactoringBenchmark/requests/requests-2.34.2/src/requests/utils.py",
        "/home/tobias/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/matplotlib/backends/backend_agg.py",
        "/home/tobias/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/pandas/core/indexes/multi.py",
        "/home/tobias/.pyenv/versions/3.10.16/envs/pytorch/lib/python3.10/site-packages/torch/fx/passes/pass_manager.py"
    ]

    # test_files = ["tests/test_files/example.py"]

    for test_file in test_files:
        print(f"Processing {test_file}...")

        with open(test_file, "r") as f:
            source_code = f.read()

        divider = BalancedCodeDivider(approximate_lines=500)
        segments = divider.divide(source_code)

        from pathlib import Path
        for segment in segments:
            print(f"Segment {segment.id}: {len(segment.code.splitlines())} lines")
        with open(Path(test_file).name, "w") as f:
            f.write("\n---%---\n".join(segment.code for segment in segments))
