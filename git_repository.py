from git import Repo

class GitRepository:
    def __init__(self, repo_path: str):
        try:
            self.repo = Repo.init(repo_path)
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

    def commit_changes(self, message: str):
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(message)
        except Exception as e:
            raise Exception(f"Failed to commit changes: {str(e)}") 
        
    def revert_changes(self):
        try:
            self.repo.git.reset('--hard')
        except Exception as e:
            raise Exception(f"Failed to revert changes: {str(e)}")
