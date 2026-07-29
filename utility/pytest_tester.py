import os
import subprocess
from pathlib import Path

from pytest import ExitCode

from utility.cli import CLI
from utility.tester import Tester


class PytestTester(Tester):
    def __init__(self, pyenv_name: str, test_file_path: str):
        self.pyenv_name = pyenv_name
        self.test_file_path = test_file_path

    def test_before(self) -> str:
        """Run tests and record which passed and which failed.

        Returns:
            str: The summary line of the pytest output.
        """
        pytest_output = self.__run_pytest()
        self.initial_test_results = self.__extract_test_results(pytest_output)
        return pytest_output.splitlines()[-1] # return the summary line of the pytest output

    def test_changed(self) -> bool:
        """Run tests and check if the same tests pass and fail as recorded.

        Returns:
            bool: True if the test results have changed, False otherwise.
        """
        pytest_output = self.__run_pytest()
        changed_test_results = self.__extract_test_results(pytest_output)

        results_changed = not self.__compare_to_initial_results(changed_test_results)

        if results_changed:
            CLI.print_debug(f"Current pytest results: {pytest_output.splitlines()[-1]}")

        return results_changed

    def __run_pytest(self) -> str:
        env = os.environ.copy()
        env["PYENV_VERSION"] = self.pyenv_name
        result = subprocess.run(["pyenv", "exec", "pytest",  "-q", "-rpf", self.test_file_path], env=env, capture_output=True, text=True)
        if not result.returncode in [ExitCode.OK, ExitCode.TESTS_FAILED]:
            raise Exception(f"Pytest execution failed with return code {result.returncode}. Stderr: {result.stderr}")
        return result.stdout
    
    def __extract_test_results(self, pytest_output: str) -> dict[str, bool]:
        test_results = {}
        for line in pytest_output.splitlines():
            if line.startswith("PASSED"):
                test_name = line.replace("PASSED", "", 1).strip()
                test_results[test_name] = True
            elif line.startswith("FAILED"):
                test_name = line.replace("FAILED", "", 1).strip().split(" - ", 1)[0].strip()
                test_results[test_name] = False
        return test_results
    
    def __compare_to_initial_results(self, changed_test_results: dict[str, bool]) -> bool:
        for test_name, initial_status in self.initial_test_results.items():
            changed_status = changed_test_results.get(test_name)
            if changed_status is None or changed_status != initial_status:
                return False
        return True