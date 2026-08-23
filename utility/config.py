import os
from dataclasses import dataclass

import tomllib


@dataclass
class Config():
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
    max_iterations: int = None
    statistics_directory: str = None
    show_tree: bool = False

    def __str__(self):
        return (
            f"Config(\n"
            f"  root_path='{self.root_path}',\n"
            f"  target_file_paths={self.target_file_paths},\n"
            f"  git_repo_path='{self.git_repo_path}',\n"
            f"  branch_name='{self.branch_name}',\n"
            f"  pyenv_name='{self.pyenv_name}',\n"
            f"  test_file_path='{self.test_file_path}',\n"
            f"  max_iterations={self.max_iterations},\n"
            f"  statistics_directory='{self.statistics_directory}',\n"
            f"  show_tree={self.show_tree}\n"
            f")"
        )
    
    def get_absolute_file_paths(self) -> list[str]:
        return [os.path.join(self.root_path, path) for path in self.target_file_paths]
    
    def get_absolute_git_repo_path(self) -> str:
        return os.path.join(self.root_path, self.git_repo_path)
    
    def get_absolute_test_file_path(self) -> str:
        return os.path.join(self.root_path, self.test_file_path)

    def get_absolute_statistics_directory(self) -> str:
        return os.path.join(self.root_path, self.statistics_directory)

def load_from_toml(file_path: str) -> "Config":
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    
    return Config(
        root_path=os.path.dirname(file_path),
        target_file_paths=data["target_file_paths"],
        git_repo_path=data["git_repo_path"],
        branch_name=data["branch_name"],
        pyenv_name=data["pyenv_name"],
        test_file_path=data["test_file_path"],
        max_iterations=data["max_iterations"],
        statistics_directory=data["statistics_directory"],
        show_tree=data["show_tree"]
    )