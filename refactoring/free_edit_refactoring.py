import difflib

from refactoring import Refactoring

class FreeEditRefactoring(Refactoring):
    def __init__(self, old_code: str, new_code: str):
        super().__init__()
        self.old_code = old_code
        self.new_code = new_code

    def get_diff(self) -> str:
        diff = difflib.unified_diff(
            self.old_code.splitlines(),
            self.new_code.splitlines(),
            fromfile='before refactoring',
            tofile='after refactoring',
            lineterm=''
        )
        return '\n'.join(diff)

    def execute(self, filepath: str) -> None:
        with open(filepath, 'w') as file:
            file.write(self.new_code)