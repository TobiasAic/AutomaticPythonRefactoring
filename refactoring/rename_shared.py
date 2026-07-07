from dataclasses import dataclass

@dataclass
class RenameArguments:
    line_number: int
    old_name: str
    new_name: str

def calculate_offset(filepath: str, line_number: int, identifier: str) -> int:
        with open(filepath, "r") as f:
            lines = f.readlines()

        offset = 0
        for i in range(line_number - 1):
            offset += len(lines[i])

        offset += lines[line_number - 1].index(identifier)
        return offset