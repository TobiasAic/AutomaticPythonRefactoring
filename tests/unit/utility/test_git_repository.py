# AI-generated

import pytest
from git import Repo

from utility.git_repository import GitRepository


@pytest.fixture
def repo_path(tmp_path):
    repo = Repo.init(tmp_path)
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test")
        config.set_value("user", "email", "test@example.com")
    (tmp_path / "file.txt").write_text("initial\n")
    repo.git.add(A=True)
    repo.index.commit("Initial commit")
    return tmp_path


def test_init_creates_repo_when_directory_is_not_a_repo(tmp_path):
    git_repository = GitRepository(str(tmp_path))

    assert git_repository.get_current_branch() is not None
    assert git_repository.get_commit_history() == ["Initial commit"]


def test_init_wraps_an_existing_valid_repo(repo_path):
    git_repository = GitRepository(str(repo_path))

    assert git_repository.get_commit_history() == ["Initial commit"]


def test_init_rejects_repo_with_uncommitted_changes(repo_path):
    (repo_path / "dirty.txt").write_text("uncommitted\n")

    with pytest.raises(Exception, match="uncommitted changes"):
        GitRepository(str(repo_path))


def test_create_branch_switches_to_new_branch(repo_path):
    git_repository = GitRepository(str(repo_path))

    git_repository.create_branch("feature")

    assert git_repository.get_current_branch() == "feature"
    assert git_repository.branch_exists("feature")


def test_branch_exists_returns_false_for_unknown_branch(repo_path):
    git_repository = GitRepository(str(repo_path))

    assert git_repository.branch_exists("does-not-exist") is False


def test_commit_changes_adds_and_commits_all_changes(repo_path):
    git_repository = GitRepository(str(repo_path))
    (repo_path / "new_file.txt").write_text("content\n")

    commit_hash = git_repository.commit_changes("Add new file")

    assert commit_hash
    assert git_repository.get_commit_history()[0] == "Add new file"


def test_revert_changes_discards_uncommitted_modifications(repo_path):
    git_repository = GitRepository(str(repo_path))
    (repo_path / "file.txt").write_text("modified\n")

    git_repository.revert_changes()

    assert (repo_path / "file.txt").read_text() == "initial\n"


def test_checkout_branch_switches_branches(repo_path):
    git_repository = GitRepository(str(repo_path))
    original_branch = git_repository.get_current_branch()
    git_repository.create_branch("feature")

    git_repository.checkout_branch(original_branch)

    assert git_repository.get_current_branch() == original_branch


def test_move_branch_moves_branch_to_current_commit(repo_path):
    git_repository = GitRepository(str(repo_path))
    original_branch = git_repository.get_current_branch()
    git_repository.create_branch("feature")
    git_repository.commit_changes("Second commit")

    git_repository.move_branch(original_branch)
    git_repository.checkout_branch(original_branch)

    assert git_repository.get_commit_history()[0] == "Second commit"


def test_detach_head_leaves_no_active_branch(repo_path):
    git_repository = GitRepository(str(repo_path))

    git_repository.detach_head()

    assert git_repository.get_current_branch() is None


def test_go_to_previous_commit_moves_head_back(repo_path):
    git_repository = GitRepository(str(repo_path))
    git_repository.commit_changes("Second commit")

    git_repository.go_to_previous_commit()

    assert (repo_path / "file.txt").read_text() == "initial\n"


def test_checkout_commit_moves_to_specific_commit(repo_path):
    git_repository = GitRepository(str(repo_path))
    first_commit_hash = git_repository.repo.head.commit.hexsha
    (repo_path / "file.txt").write_text("changed\n")
    git_repository.commit_changes("Second commit")

    git_repository.checkout_commit(first_commit_hash)

    assert (repo_path / "file.txt").read_text() == "initial\n"


def test_get_commit_history_lists_messages_newest_first(repo_path):
    git_repository = GitRepository(str(repo_path))
    git_repository.commit_changes("Second commit")
    git_repository.commit_changes("Third commit")

    assert git_repository.get_commit_history() == [
        "Third commit",
        "Second commit",
        "Initial commit",
    ]
