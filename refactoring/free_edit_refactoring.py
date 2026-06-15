import difflib

from refactoring.refactoring import Refactoring

class FreeEditRefactoring(Refactoring):
    def __init__(self, filepath: str, old_code: str, new_code: str):
        super().__init__(filepath)
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

    def execute(self) -> None:
        with open(self.filepath, 'w') as file:
            file.write(self.new_code)