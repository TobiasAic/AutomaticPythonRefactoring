from git import Repo
from git.exc import InvalidGitRepositoryError

from utility.cli import CLI


class GitRepository:
    """ A wrapper class to access GitPython functionality in a more user-friendly way. """
    def __init__(self, repo_path: str):
        """Initialize the Git repository.

        Args:
            repo_path (str): The path to the Git repository.

        Raises:
            Exception: If the repository cannot be initialized.
            Exception: If the repository is bare (This means it has no working copy).
            Exception: If the repository has uncommitted changes.
        """
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError as e:
            self.repo = Repo.init(repo_path)
            self.commit_changes("Initial commit") # create an initial commit so that a branch can be created later
        except Exception as e:
            raise Exception(f"Could not initialize Git repository at {repo_path}: {str(e)}")
        
        if self.repo.bare:
            raise Exception(f"The repository at {repo_path} is bare. Please provide a valid Git repository.")

        if self.repo.is_dirty():
            raise Exception("Repository has uncommitted changes. Please commit or stash them before proceeding.")
        
    def create_branch(self, branch_name: str):
        """Create a branch with a specified name.

        Args:
            branch_name (str): The name of the branch to create.

        Raises:
            Exception: If the branch creation fails.
        """
        try:
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            CLI.print_debug(f"Successfully created and switched to branch '{branch_name}'")
        except Exception as e:
            raise Exception(f"Failed to create and switch to branch '{branch_name}': {str(e)}")

    def branch_exists(self, branch_name: str) -> bool:
        """Check whether a branch with the given name already exists.

        Args:
            branch_name (str): The name of the branch to look for.

        Returns:
            bool: True if the branch exists.
        """
        return branch_name in [head.name for head in self.repo.heads]

    def commit_changes(self, message: str) -> str:
        """Commit all changes with a specified message.

        Args:
            message (str): The commit message.

        Raises:
            Exception: If the commit fails.

        Returns:
            str: The hexadecimal SHA-1 hash of the committed changes.
        """
        try:
            self.repo.git.add(A=True)
            commit = self.repo.index.commit(message)
            return commit.hexsha
        except Exception as e:
            raise Exception(f"Failed to commit changes: {str(e)}") 
        
    def revert_changes(self):
        """Revert all changes to the last commit.

        Raises:
            Exception: If the revert fails.
        """
        try:
            self.repo.git.reset('--hard')
        except Exception as e:
            raise Exception(f"Failed to revert changes: {str(e)}")
        
    def go_to_previous_commit(self):
        """Go to the previous commit.

        Raises:
            Exception: If the operation fails.
        """
        try:
            self.repo.git.checkout('HEAD~1')
        except Exception as e:
            raise Exception(f"Failed to go to previous commit: {str(e)}")
        
    def detach_head(self):
        """Detach the head.

        Raises:
            Exception: If the operation fails.
        """
        try:
            self.repo.git.checkout('--detach')
        except Exception as e:
            raise Exception(f"Failed to detach HEAD: {str(e)}")
        
    def move_branch(self, branch_name: str):
        """Move branch to current commit.

        Args:
            branch_name (str): The name of the branch to move.

        Raises:
            Exception: If the branch moving fails.
        """
        try:
            self.repo.git.branch('-f', branch_name)
        except Exception as e:
            raise Exception(f"Failed to move branch '{branch_name}': {str(e)}")
        
    def checkout_commit(self, commit_hash: str):
        """Checkout a specific commit by its hash.

        Args:
            commit_hash (str): The hash of the commit to checkout.

        Raises:
            Exception: If the checkout fails.
        """
        try:
            self.repo.git.checkout(commit_hash)
        except Exception as e:
            raise Exception(f"Failed to checkout commit '{commit_hash}': {str(e)}")
        
    def get_current_branch(self) -> str:
        """Get the name of the currently visited branch.

        Raises:
            Exception: If the operation fails.

        Returns:
            str: The name of the currently visited branch.
        """
        try:
            return self.repo.active_branch.name
        except TypeError: # happens when HEAD is detached
            return None
        except Exception as e:
            raise Exception(f"Failed to get current branch: {str(e)}")
        
    def checkout_branch(self, branch_name: str):
        """Checkout a specific branch by its name.

        Args:
            branch_name (str): The name of the branch to checkout.

        Raises:
            Exception: If the checkout fails.
        """
        try:
            self.repo.git.checkout(branch_name)
        except Exception as e:
            raise Exception(f"Failed to checkout branch '{branch_name}': {str(e)}")
        
    def get_commit_history(self) -> list:
        """Get the commit messages of the entire commit history.

        Raises:
            Exception: If the operation fails.

        Returns:
            list: A list of commit messages.
        """
        try:
            commits = list(self.repo.iter_commits(self.get_current_branch()))
            return [commit.message for commit in commits]
        except Exception as e:
            raise Exception(f"Failed to get commit history for branch '{self.get_current_branch()}': {str(e)}")
        