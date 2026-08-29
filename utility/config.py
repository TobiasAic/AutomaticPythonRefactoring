import os
from dataclasses import dataclass
from pathlib import Path

import tomllib


@dataclass
class Config:
    """ 
    Configuration class for the Automatic Python Refactoring tool. 
    This class holds all the necessary configuration parameters required for the tool to function properly.
    """
    root_path: str
    target_file_paths: list[str]
    git_repo_path: str
    branch_name: str
    pyenv_name: str
    test_file_path: str
    refactoring_state_path: str
    max_iterations: int = None
    show_tree: bool = False
    seed: int = 42
    temperature: float = None
    refactoring_idea_count: int = 3
    category_attempt_count: int = 3

    def __str__(self):
        return (
            f"Config(\n"
            f"  root_path='{self.root_path}',\n"
            f"  target_file_paths={self.target_file_paths},\n"
            f"  git_repo_path='{self.git_repo_path}',\n"
            f"  branch_name='{self.branch_name}',\n"
            f"  pyenv_name='{self.pyenv_name}',\n"
            f"  test_file_path='{self.test_file_path}',\n"
            f"  refactoring_state_path='{self.refactoring_state_path}',\n"
            f"  max_iterations={self.max_iterations},\n"
            f"  show_tree={self.show_tree},\n"
            f"  seed={self.seed},\n"
            f"  temperature={self.temperature},\n"
            f"  refactoring_idea_count={self.refactoring_idea_count},\n"
            f"  category_attempt_count={self.category_attempt_count}\n"
            f")"
        )

    def get_absolute_file_paths(self) -> list[str]:
        return [os.path.join(self.root_path, path) for path in self.target_file_paths]

    def get_absolute_git_repo_path(self) -> str:
        return os.path.join(self.root_path, self.git_repo_path)

    def get_absolute_test_file_path(self) -> str:
        return os.path.join(self.root_path, self.test_file_path)

    def get_absolute_refactoring_state_path(self) -> str:
        return os.path.join(self.root_path, self.refactoring_state_path)


def load_from_toml(file_path: str) -> "Config":
    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    if "root_path" not in data:
        root_path = os.path.dirname(file_path)
    else:
        root_path = Path(data["root_path"]).expanduser()

    return Config(
        root_path=root_path,
        target_file_paths=data["target_file_paths"],
        git_repo_path=data["git_repo_path"],
        branch_name=data["branch_name"],
        pyenv_name=data["pyenv_name"],
        test_file_path=data["test_file_path"],
        refactoring_state_path=data["refactoring_state_path"],
        max_iterations=data["max_iterations"],
        show_tree=data["show_tree"],
        seed=data.get("seed", 42),
        temperature=data.get("temperature"),
        refactoring_idea_count=data.get("refactoring_idea_count", 3),
        category_attempt_count=data.get("category_attempt_count", 3)
    )
