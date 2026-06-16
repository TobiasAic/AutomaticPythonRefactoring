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
        return f1.read() == f2.read()