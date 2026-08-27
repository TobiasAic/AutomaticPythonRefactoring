# AI-generated

import os

from utility.config import Config, load_from_toml


def make_config(**overrides) -> Config:
    defaults = dict(
        root_path="/root",
        target_file_paths=["a.py", "b.py"],
        git_repo_path="repo",
        branch_name="branch",
        pyenv_name="pyenv",
        test_file_path="tests",
    )
    defaults.update(overrides)
    return Config(**defaults)


def test_get_absolute_file_paths_joins_root_with_each_target():
    config = make_config()

    assert config.get_absolute_file_paths() == [
        os.path.join("/root", "a.py"),
        os.path.join("/root", "b.py"),
    ]


def test_get_absolute_git_repo_path_joins_root_with_git_repo_path():
    config = make_config()

    assert config.get_absolute_git_repo_path() == os.path.join("/root", "repo")


def test_get_absolute_test_file_path_joins_root_with_test_file_path():
    config = make_config()

    assert config.get_absolute_test_file_path() == os.path.join("/root", "tests")


def test_get_absolute_statistics_directory_joins_root_with_statistics_directory():
    config = make_config(statistics_directory="stats")

    assert config.get_absolute_statistics_directory() == os.path.join("/root", "stats")


def test_str_includes_all_field_values():
    config = make_config(max_iterations=5, show_tree=True)

    text = str(config)

    assert "root_path='/root'" in text
    assert "max_iterations=5" in text
    assert "show_tree=True" in text


def test_load_from_toml_with_explicit_root_path(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
        root_path = "/explicit/root"
        target_file_paths = ["main.py"]
        git_repo_path = "repo"
        branch_name = "refactor"
        pyenv_name = "3.12"
        test_file_path = "tests"
        max_iterations = 3
        statistics_directory = "stats"
        show_tree = true
        """
    )

    config = load_from_toml(str(config_file))

    assert str(config.root_path) == "/explicit/root"
    assert config.target_file_paths == ["main.py"]
    assert config.branch_name == "refactor"
    assert config.max_iterations == 3
    assert config.show_tree is True


def test_load_from_toml_defaults_root_path_to_config_file_directory(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
        target_file_paths = ["main.py"]
        git_repo_path = "repo"
        branch_name = "refactor"
        pyenv_name = "3.12"
        test_file_path = "tests"
        max_iterations = 1
        statistics_directory = "stats"
        show_tree = false
        """
    )

    config = load_from_toml(str(config_file))

    assert config.root_path == os.path.dirname(str(config_file))
