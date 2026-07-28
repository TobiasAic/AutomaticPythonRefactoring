from utility.code_divider import CodeDivider

def test_code_divider():
    with open("tests/test_files/example.py", "r") as f:
        code = f.read()

    divider = CodeDivider(code)
    old_segment = divider.get_segments()[3]
    new_segment = "def load_demo_tasks() -> list[Task]:\n    # This segment got replaced\n    pass"
    divider.replace_segment(old_segment, new_segment)

    with open("tests/test_files/segment_replaced.py", "r") as f:
        expected_code = f.read()

    assert divider.get_code() == expected_code