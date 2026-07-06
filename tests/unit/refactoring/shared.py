import difflib
import os
import shutil
from pathlib import Path
import pytest

@pytest.fixture
def example_code_file(tmp_path):
    src = Path(__file__).resolve().parents[2] / "test_files" / "example.py"
    dst = tmp_path / "example.py"
    shutil.copyfile(src, dst)

    yield dst

    os.remove(dst)

def compare_files(file1: str, file2: str) -> bool:
    with open(file1, "r") as f1, open(file2, "r") as f2:
        content1 = f1.read()
        content2 = f2.read()

        if content1 != content2:
            print(f"Files {file1} and {file2} differ:")
            diff = difflib.unified_diff(
                content1.splitlines(),
                content2.splitlines(),
                lineterm=''
            )
            print('\n'.join(diff))
            return False
        return True