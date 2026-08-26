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
    segment_index: int = 0
    categories_by_segment: dict[int, list[RefactoringCategory]] = field(default_factory=dict)
    path: str | None = field(default=None, init=False, repr=False, compare=False)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name != "path" and self.path is not None:
            self.save(self.path)

    def bind(self, path: str) -> "RefactoringSystemState":
        """ Set the path this state saves itself to. Subsequent field changes save automatically. """
        self.path = path
        return self

    def categories_for_segment(self, segment_id: int) -> list[RefactoringCategory]:
        """ Categories not yet exhausted for a segment. All categories are available the first time a segment is seen. """
        return self.categories_by_segment.setdefault(segment_id, list(ALL_CATEGORIES))

    def save(self, filepath: str):
        data = {
            "file_index": self.file_index,
            "iteration": self.iteration,
            "segment_index": self.segment_index,
            "categories_by_segment": {
                segment_id: [category.get_name() for category in categories]
                for segment_id, categories in self.categories_by_segment.items()
            },
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
            segment_index=data["segment_index"],
            categories_by_segment={
                int(segment_id): [CATEGORIES_BY_NAME[name] for name in category_names]
                for segment_id, category_names in data["categories_by_segment"].items()
            },
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
