""" This file contains CodeFile, which tracks a file's current segments across edits. """

import re
import uuid

from utility.code_divider import CodeDivider, CodeSegment


class CodeFile:
    """Owns the current state of one file being refactored: the live text plus
    a stable partition into segments that survives arbitrary edits.

    The file is divided into segments exactly once, at construction time. Each
    segment boundary is marked with a unique comment embedded in the text, so
    that after any edit - however it was made, and however much of the file it
    touched - the current segments can be recovered by splitting on the markers,
    without re-running the divider or tracking offsets. Markers are stripped
    from every value that leaves this class (`code`, `get_segment`), so nothing
    outside of `CodeFile` and the refactoring tools that call
    `marked_code_and_offset` ever sees them.
    """

    def __init__(self, code: str, divider: CodeDivider):
        self._token = uuid.uuid4().hex[:8]
        self._marked_code = self.__insert_markers(code, divider.divide(code))

    @property
    def code(self) -> str:
        """The current full file, markers stripped. Safe to write to disk or show an LLM."""
        return self.__marker_pattern().sub("", self._marked_code)

    def get_segment(self, segment_id: int) -> CodeSegment:
        """The current, clean text of one segment."""
        return self.__segments_by_id()[segment_id]

    def segment_ids(self) -> list[int]:
        return sorted(self.__segments_by_id())

    def marked_code_and_offset(self, segment_id: int) -> tuple[str, int]:
        """The raw marked-up full text, plus this segment's start offset within it.

        For tools (e.g. rope) that need a real character offset into a real file.
        """
        marker = self.__marker_text(segment_id)
        marker_start = self._marked_code.index(marker)
        return self._marked_code, marker_start + len(marker) + 1

    def with_new_marked_code(self, new_marked_code: str) -> "CodeFile":
        """Result of a tool editing the marked text (e.g. rope's output).

        Re-derives segments by splitting on markers - no diffing, no offset
        tracking, no re-running the divider.

        Raises:
            ValueError: If the number of markers changed, meaning the edit
                touched or removed a segment boundary marker.
        """
        expected = len(self.segment_ids())
        new_file = CodeFile.__new__(CodeFile)
        new_file._token = self._token
        new_file._marked_code = new_marked_code
        actual = len(new_file.segment_ids())
        if actual != expected:
            raise ValueError(
                f"Expected {expected} segment markers after the edit, found {actual}. "
                "A refactoring likely altered a segment boundary marker.")
        return new_file

    def with_updated_segment(self, segment_id: int, new_code: str) -> "CodeFile":
        """For edits confined to one segment's clean text (e.g. ApplyEdits) -
        replaces just that segment's content, leaving markers and every other
        segment's text untouched.
        """
        marker = self.__marker_text(segment_id)
        start = self._marked_code.index(marker) + len(marker) + 1
        next_marker_match = self.__marker_pattern().search(self._marked_code, start)
        end = next_marker_match.start() if next_marker_match else len(self._marked_code)
        new_marked_code = self._marked_code[:start] + new_code + self._marked_code[end:]
        return self.with_new_marked_code(new_marked_code)

    def print_segment_lengths(self) -> None:
        for segment_id in self.segment_ids():
            print(f"Segment {segment_id}: {len(self.get_segment(segment_id).code.splitlines())} lines")

    def __marker_text(self, segment_id: int) -> str:
        return f"# <<<SEG:{segment_id}:{self._token}>>>"

    def __marker_pattern(self) -> re.Pattern:
        return re.compile(rf"# <<<SEG:(\d+):{re.escape(self._token)}>>>\n")

    def __insert_markers(self, code: str, segments: list[CodeSegment]) -> str:
        return "".join(f"{self.__marker_text(segment.id)}\n{segment.code}" for segment in segments)

    def __segments_by_id(self) -> dict[int, CodeSegment]:
        parts = self.__marker_pattern().split(self._marked_code)
        # parts[0] is text before the first marker (always empty); then alternating id, code.
        return {
            int(parts[i]): CodeSegment(id=int(parts[i]), code=parts[i + 1])
            for i in range(1, len(parts), 2)
        }
