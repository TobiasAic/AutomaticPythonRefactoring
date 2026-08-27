from utility.code_divider import CodeDivider, CodeSegment
from utility.code_file import CodeFile

example_code_file_path = "tests/test_files/example.py"

def read_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()


class SingleSegmentDivider(CodeDivider):
    """Treats the whole file as one segment. Test-only divider."""

    def divide(self, code: str) -> list[CodeSegment]:
        return [CodeSegment(id=0, code=code)]


def single_segment_code_file(code: str) -> CodeFile:
    """Builds a CodeFile whose only segment (id=0) is the entire given code."""
    return CodeFile(code, SingleSegmentDivider())