import json
import os
from dataclasses import dataclass, field

from tree_of_thoughts.refactoring_category import (
    ALL_CATEGORIES,
    CATEGORIES_BY_NAME,
    RefactoringCategory,
)


@dataclass
class RefactoringSystemState:
    """ Holds all progress of a refactoring run. Once `path` is bound (see `load` or `bind`), the state
    saves itself to that path automatically whenever a field is set, so it can be resumed after a crash
    or manual stop without callers having to remember to save. """
    file_index: int = 0
    iteration: int = 0
    categories: dict[RefactoringCategory, int] = field(
        default_factory=lambda: {category: 1 for category in ALL_CATEGORIES})
    path: str | None = field(default=None, init=False, repr=False, compare=False)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name != "path" and self.path is not None:
            self.save(self.path)

    def bind(self, path: str) -> "RefactoringSystemState":
        """ Set the path this state saves itself to. Subsequent field changes save automatically. """
        self.path = path
        return self

    @staticmethod
    def initial(category_count: int, file_index: int = 0) -> "RefactoringSystemState":
        """ Fresh state for a new file, giving every category `category_count` chances before it's dropped. """
        return RefactoringSystemState(
            file_index=file_index,
            categories={category: category_count for category in ALL_CATEGORIES},
        )

    def save(self, filepath: str):
        data = {
            "file_index": self.file_index,
            "iteration": self.iteration,
            "categories": {category.get_name(): count for category, count in self.categories.items()},
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load(filepath: str) -> "RefactoringSystemState":
        with open(filepath, "r") as f:
            data = json.load(f)
        return RefactoringSystemState(
            file_index=data["file_index"],
            iteration=data["iteration"],
            categories={CATEGORIES_BY_NAME[name]: count for name, count in data["categories"].items()},
        ).bind(filepath)

    @staticmethod
    def load_if_exists(filepath: str) -> "RefactoringSystemState | None":
        if not os.path.exists(filepath):
            return None
        return RefactoringSystemState.load(filepath)

    @staticmethod
    def clear(filepath: str):
        if os.path.exists(filepath):
            os.remove(filepath)
