from dataclasses import dataclass


@dataclass
class RenameArguments:
    """ Arguments from the LLM for the Rename and MultiRename refactoring. """
    line_number: int
    old_name: str
    new_name: str

def calculate_offset(filepath: str, line_number: int, identifier: str) -> int:
    """ Calculates the offset of an identifier in a file.

    Args:
        filepath (str): The path to the file containing the code.
        line_number (int): The line number of the identifier to rename.
        identifier (str): The identifier to rename.

    Returns:
        int: The offset of the identifier in the file.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    offset = 0
    for i in range(line_number - 1):
        offset += len(lines[i])

    offset += lines[line_number - 1].index(identifier)
    return offset