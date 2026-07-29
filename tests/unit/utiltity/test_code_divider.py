from utility.code_divider import CodeDivider


def test_code_divider():
    with open("tests/test_files/example.py", "r") as f:
        code = f.read()

    divider = CodeDivider(code, max_lines=15)
    new_segment = "class TaskRepository:\n    # Replaced\n    pass"
    divider.replace_segment(2, new_segment)

    with open("tests/test_files/segment_replaced.py", "r") as f:
        expected_code = f.read()

    assert divider.get_code() == expected_code