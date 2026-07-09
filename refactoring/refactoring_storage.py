import uuid
import os
import json

from refactoring.refactoring import Refactoring

class RefactoringStorage:
    def __init__(self, filepath: str):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def save_refactoring(self, refactoring: Refactoring) -> None:
        refactoring_id = str(uuid.uuid4())
        refactoring.commit_id = refactoring_id
        dir_path = os.path.dirname(self.filepath)

        os.makedirs(dir_path, exist_ok=True)

        with open(os.path.join(dir_path, f"{refactoring_id}.json"), 'w') as file:
            json.dump(refactoring.to_dict(), file, indent=4)

        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as file:
                refactoring_ids = json.load(file)
        else:
            refactoring_ids = []

        refactoring_ids.append(refactoring_id)
        with open(self.filepath, 'w') as file:
            json.dump(refactoring_ids, file, indent=4)

    def load_refactorings(self) -> list[Refactoring]:
        refactorings = []
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as file:
                refactoring_ids = json.load(file)
            for refactoring_id in refactoring_ids:
                with open(os.path.join(os.path.dirname(self.filepath), f"{refactoring_id}.json"), 'r') as file:
                    refactoring_dict = json.load(file)
                    refactoring = Refactoring.from_dict(refactoring_dict)
                    refactoring.commit_hash = refactoring_id # TODO: Remove, when I have better refactorings saved
                    refactorings.append(refactoring)
        return refactorings