import pytest

from utility.code_divider import CodeDivider, CodeSegment
from utility.code_file import CodeFile


class FixedDivider(CodeDivider):
    """Splits code into segments of the given line counts, in order. Lets tests
    control segment boundaries precisely instead of depending on the real
    line-labeling/balancing logic."""

    def __init__(self, line_counts: list[int]):
        self.line_counts = line_counts

    def divide(self, code: str) -> list[CodeSegment]:
        lines = code.splitlines(keepends=True)
        segments = []
        pos = 0
        for i, count in enumerate(self.line_counts):
            segments.append(CodeSegment(id=i, code="".join(lines[pos:pos + count])))
            pos += count
        return segments


def make_code() -> str:
    return (
        "def f0():\n"
        "    return 0\n"
        "def f1():\n"
        "    return 1\n"
        "def f2():\n"
        "    return 2\n"
    )


def test_code_reconstructs_the_original_source():
    code = make_code()

    code_file = CodeFile(code, FixedDivider([2, 2, 2]))

    assert code_file.code == code


def test_get_segment_returns_clean_text_for_each_segment():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    assert code_file.get_segment(0).code == "def f0():\n    return 0\n"
    assert code_file.get_segment(1).code == "def f1():\n    return 1\n"
    assert code_file.get_segment(2).code == "def f2():\n    return 2\n"


def test_segment_ids_are_sorted():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    assert code_file.segment_ids() == [0, 1, 2]


def test_markers_never_leak_into_code_or_segments():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    assert "SEG:" not in code_file.code
    for segment_id in code_file.segment_ids():
        assert "SEG:" not in code_file.get_segment(segment_id).code


def test_marked_code_and_offset_points_at_the_segments_own_text():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    marked_code, offset = code_file.marked_code_and_offset(1)

    segment_code = code_file.get_segment(1).code
    assert marked_code[offset:offset + len(segment_code)] == segment_code


def test_with_new_marked_code_rederives_segments_after_an_edit_in_one_segment():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))
    marked_code, offset = code_file.marked_code_and_offset(1)
    segment_1_code = code_file.get_segment(1).code
    edited = marked_code[:offset] + "def f1():\n    return 100\n" + marked_code[offset + len(segment_1_code):]

    new_code_file = code_file.with_new_marked_code(edited)

    assert new_code_file.get_segment(0).code == code_file.get_segment(0).code
    assert new_code_file.get_segment(1).code == "def f1():\n    return 100\n"
    assert new_code_file.get_segment(2).code == code_file.get_segment(2).code
    assert new_code_file.segment_ids() == [0, 1, 2]


def test_with_new_marked_code_handles_edits_scattered_across_multiple_segments():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))
    marked_code, _ = code_file.marked_code_and_offset(0)
    edited = marked_code.replace("return 0", "return 100").replace("return 2", "return 200")

    new_code_file = code_file.with_new_marked_code(edited)

    assert new_code_file.get_segment(0).code == "def f0():\n    return 100\n"
    assert new_code_file.get_segment(1).code == code_file.get_segment(1).code
    assert new_code_file.get_segment(2).code == "def f2():\n    return 200\n"


def test_with_new_marked_code_raises_if_a_marker_was_removed():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))
    marked_code, _ = code_file.marked_code_and_offset(0)
    lines = marked_code.splitlines(keepends=True)
    edited = "".join(line for line in lines if "SEG:1:" not in line)

    with pytest.raises(ValueError):
        code_file.with_new_marked_code(edited)


def test_with_updated_segment_replaces_only_the_target_segment():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    new_code_file = code_file.with_updated_segment(1, "def f1():\n    return 100\n")

    assert new_code_file.get_segment(0).code == code_file.get_segment(0).code
    assert new_code_file.get_segment(1).code == "def f1():\n    return 100\n"
    assert new_code_file.get_segment(2).code == code_file.get_segment(2).code


def test_with_updated_segment_on_the_last_segment():
    code_file = CodeFile(make_code(), FixedDivider([2, 2, 2]))

    new_code_file = code_file.with_updated_segment(2, "def f2():\n    return 200\n")

    assert new_code_file.get_segment(2).code == "def f2():\n    return 200\n"
    assert new_code_file.code.endswith("return 200\n")
