import json
import os
from dataclasses import asdict, dataclass, field


@dataclass
class Checkpoint:
    """ Tracks progress through a refactoring run so it can be resumed after a crash or manual stop. """
    file_index: int = 0
    iteration: int = 0
    segment_index: int = 0
    categories_by_segment: dict[int, list[str]] = field(default_factory=dict)

    def save(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(asdict(self), f)

    @staticmethod
    def load(filepath: str) -> "Checkpoint":
        with open(filepath, "r") as f:
            data = json.load(f)
        return Checkpoint(
            file_index=data["file_index"],
            iteration=data["iteration"],
            segment_index=data["segment_index"],
            categories_by_segment={
                int(segment_id): category_names
                for segment_id, category_names in data["categories_by_segment"].items()
            },
        )

    @staticmethod
    def load_if_exists(filepath: str) -> "Checkpoint | None":
        if not os.path.exists(filepath):
            return None
        return Checkpoint.load(filepath)

    @staticmethod
    def clear(filepath: str):
        if os.path.exists(filepath):
            os.remove(filepath)
