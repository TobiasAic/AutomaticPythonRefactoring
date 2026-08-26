import pytest

from utility.balanced_code_divider import BalancedCodeDivider
from utility.code_divider import CodeSegment


def make_module(function_count: int, lines_per_function: int = 3) -> str:
    functions = []
    for i in range(function_count):
        body = "\n".join(f"    x{j} = {j}" for j in range(lines_per_function))
        functions.append(f"def f{i}():\n{body}\n    return x0\n")
    return "\n".join(functions)


def test_get_code_reconstructs_original_source_exactly():
    code = make_module(6)

    divider = BalancedCodeDivider(code, approximate_lines=10)

    assert divider.get_code() == code


def test_segments_cover_the_code_without_gaps_or_overlap():
    code = make_module(6)

    divider = BalancedCodeDivider(code, approximate_lines=10)

    assert "".join(segment.code for segment in divider.get_segments()) == code


def test_small_code_yields_a_single_segment():
    code = "x = 1\ny = 2\n"

    divider = BalancedCodeDivider(code, approximate_lines=500)

    assert divider.get_number_of_segments() == 1
    assert divider.get_segments()[0].code == code


def test_large_code_is_split_into_multiple_segments_targeting_approximate_lines():
    code = make_module(20, lines_per_function=5)
    total_lines = len(code.splitlines())

    divider = BalancedCodeDivider(code, approximate_lines=20)

    segments = divider.get_segments()
    expected_num_segments = round(total_lines / 20)
    assert len(segments) > 1
    assert divider.get_number_of_segments() == expected_num_segments


def test_no_segment_exceeds_max_lines_even_for_a_single_oversized_function():
    long_body = "\n".join(f"    x{j} = {j}" for j in range(100))
    code = f"def big():\n{long_body}\n    return x0\n"

    divider = BalancedCodeDivider(code, approximate_lines=20)

    for segment in divider.get_segments():
        assert len(segment.code.splitlines()) <= divider.max_lines
    assert divider.get_code() == code


def test_replace_segment_updates_code_and_remembers_by_default():
    code = make_module(2)
    divider = BalancedCodeDivider(code, approximate_lines=500)
    original_id = divider.get_segments()[0].id

    new_code = divider.replace_segment(CodeSegment(id=original_id, code="def f0():\n    return 42\n"))

    assert "return 42" in new_code
    assert divider.get_code() == new_code


def test_replace_segment_without_remember_does_not_persist():
    code = make_module(2)
    divider = BalancedCodeDivider(code, approximate_lines=500)
    original_id = divider.get_segments()[0].id

    divider.replace_segment(CodeSegment(id=original_id, code="def f0():\n    return 42\n"), remember=False)

    assert divider.get_code() == code


def test_replace_segment_rejects_unknown_id():
    code = make_module(1)
    divider = BalancedCodeDivider(code, approximate_lines=500)

    with pytest.raises(ValueError):
        divider.replace_segment(CodeSegment(id=999, code="pass\n"))


def test_replace_segment_ensures_trailing_newline():
    code = make_module(1)
    divider = BalancedCodeDivider(code, approximate_lines=500)
    original_id = divider.get_segments()[0].id

    new_code = divider.replace_segment(CodeSegment(id=original_id, code="def f0():\n    return 1"))

    assert new_code.endswith("return 1\n")
