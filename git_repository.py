from git import Repo
from git.exc import InvalidGitRepositoryError

class GitRepository:
    def __init__(self, repo_path: str):
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
        try:
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
        except Exception as e:
            raise Exception(f"Failed to create and switch to branch '{branch_name}': {str(e)}")

    def commit_changes(self, message: str) -> str:
        try:
            self.repo.git.add(A=True)
            commit = self.repo.index.commit(message)
            return commit.hexsha
        except Exception as e:
            raise Exception(f"Failed to commit changes: {str(e)}") 
        
    def revert_changes(self):
        try:
            self.repo.git.reset('--hard')
        except Exception as e:
            raise Exception(f"Failed to revert changes: {str(e)}")
        
    def go_to_previous_commit(self):
        try:
            self.repo.git.checkout('HEAD~1')
        except Exception as e:
            raise Exception(f"Failed to go to previous commit: {str(e)}")
        
    def detach_head(self):
        try:
            self.repo.git.checkout('--detach')
        except Exception as e:
            raise Exception(f"Failed to detach HEAD: {str(e)}")
        
    def switch_branch(self, branch_name: str):
        try:
            self.repo.git.checkout(branch_name)
        except Exception as e:
            raise Exception(f"Failed to switch to branch '{branch_name}': {str(e)}")
        
    def move_branch(self, branch_name: str):
        try:
            self.repo.git.branch('-f', branch_name)
        except Exception as e:
            raise Exception(f"Failed to move branch '{branch_name}': {str(e)}")
        
    def checkout_commit(self, commit_hash: str):
        try:
            self.repo.git.checkout(commit_hash)
        except Exception as e:
            raise Exception(f"Failed to checkout commit '{commit_hash}': {str(e)}")
        
    def get_current_branch(self) -> str:
        try:
            return self.repo.active_branch.name
        except TypeError: # happens when HEAD is detached
            return None
        except Exception as e:
            raise Exception(f"Failed to get current branch: {str(e)}")
        
    def checkout_branch(self, branch_name: str):
        try:
            self.repo.git.checkout(branch_name)
        except Exception as e:
            raise Exception(f"Failed to checkout branch '{branch_name}': {str(e)}")
