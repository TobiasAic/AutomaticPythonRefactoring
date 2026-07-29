example_code_file_path = "tests/test_files/example.py" 

def read_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()