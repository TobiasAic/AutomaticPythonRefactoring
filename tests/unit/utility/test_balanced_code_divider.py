from utility.balanced_code_divider import BalancedCodeDivider


def make_module(function_count: int, lines_per_function: int = 3) -> str:
    functions = []
    for i in range(function_count):
        body = "\n".join(f"    x{j} = {j}" for j in range(lines_per_function))
        functions.append(f"def f{i}():\n{body}\n    return x0\n")
    return "\n".join(functions)


def test_segments_reconstruct_original_source_exactly():
    code = make_module(6)

    segments = BalancedCodeDivider(approximate_lines=10).divide(code)

    assert "".join(segment.code for segment in segments) == code


def test_segments_cover_the_code_without_gaps_or_overlap():
    code = make_module(6)

    segments = BalancedCodeDivider(approximate_lines=10).divide(code)

    assert "".join(segment.code for segment in segments) == code


def test_small_code_yields_a_single_segment():
    code = "x = 1\ny = 2\n"

    segments = BalancedCodeDivider(approximate_lines=500).divide(code)

    assert len(segments) == 1
    assert segments[0].code == code


def test_large_code_is_split_into_multiple_segments_targeting_approximate_lines():
    code = make_module(20, lines_per_function=5)
    total_lines = len(code.splitlines())

    segments = BalancedCodeDivider(approximate_lines=20).divide(code)

    expected_num_segments = round(total_lines / 20)
    assert len(segments) > 1
    assert len(segments) == expected_num_segments


def test_an_oversized_function_is_kept_atomic_even_though_it_exceeds_max_lines():
    long_body = "\n".join(f"    x{j} = {j}" for j in range(100))
    code = f"def big():\n{long_body}\n    return x0\n"

    divider = BalancedCodeDivider(approximate_lines=20)
    segments = divider.divide(code)

    assert len(segments) == 1
    assert len(segments[0].code.splitlines()) > divider.max_lines
    assert segments[0].code == code


def test_an_oversized_statement_block_is_kept_atomic_even_though_it_exceeds_max_lines():
    code = "\n".join(f"x{j} = {j}" for j in range(100)) + "\n"

    divider = BalancedCodeDivider(approximate_lines=20)
    segments = divider.divide(code)

    assert len(segments) == 1
    assert len(segments[0].code.splitlines()) > divider.max_lines
    assert segments[0].code == code


def test_an_oversized_class_is_subdivided_into_its_methods():
    long_method_body = "\n".join(f"        x{j} = {j}" for j in range(30))
    methods = "\n".join(
        f"    def m{i}(self):\n{long_method_body}\n        return x0\n"
        for i in range(4)
    )
    code = f"class Big:\n{methods}"

    divider = BalancedCodeDivider(approximate_lines=20)
    segments = divider.divide(code)

    assert len(segments) > 1
    assert "".join(segment.code for segment in segments) == code
