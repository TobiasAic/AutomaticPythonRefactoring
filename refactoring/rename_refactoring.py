import os

from refactoring.refactoring import Refactoring
from rope.base.project import Project
from rope.base import libutils
from rope.refactor.rename import Rename

class RenameRefactoring(Refactoring):
    def __init__(self, filepath: str, offset: int, new_name: str):
        super().__init__()

        self.project = Project(os.path.dirname(filepath))
        self.resource = libutils.path_to_resource(self.project, filepath)
        self.rename = Rename(self.project, self.resource, offset)
        self.changes = self.rename.get_changes(new_name)

    def get_diff(self) -> str:
       return self.changes.get_description()

    def execute(self) -> None:
       self.project.do(self.changes) 
    
    def revert(self) -> None:
        self.project.history.undo()

    def __del__(self):
        self.project.close()