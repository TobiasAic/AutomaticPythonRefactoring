from types import SimpleNamespace

import pytest
from pytest import ExitCode

from utility.pytest_tester import PytestTester


def fake_run(stdout: str, returncode: int = ExitCode.OK):
    def run(*args, **kwargs):
        return SimpleNamespace(stdout=stdout, stderr="", returncode=returncode)
    return run


PASSING_OUTPUT = (
    "PASSED tests/test_foo.py::test_a\n"
    "PASSED tests/test_foo.py::test_b\n"
    "2 passed in 0.10s"
)

MIXED_OUTPUT = (
    "PASSED tests/test_foo.py::test_a\n"
    "FAILED tests/test_foo.py::test_b - AssertionError\n"
    "1 passed, 1 failed in 0.10s"
)


def test_test_before_returns_summary_line_and_records_results(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(PASSING_OUTPUT))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")

    summary = tester.test_before()

    assert summary == "2 passed in 0.10s"
    assert tester.initial_test_results == {
        "tests/test_foo.py::test_a": True,
        "tests/test_foo.py::test_b": True,
    }


def test_test_changed_returns_false_when_results_are_identical(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(PASSING_OUTPUT))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")
    tester.test_before()

    assert tester.test_changed() is False


def test_test_changed_returns_true_when_a_test_starts_failing(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(PASSING_OUTPUT))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")
    tester.test_before()

    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(MIXED_OUTPUT))

    assert tester.test_changed() is True


def test_test_changed_returns_true_when_a_previously_passing_test_is_missing(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(PASSING_OUTPUT))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")
    tester.test_before()

    monkeypatch.setattr(
        "utility.pytest_tester.subprocess.run",
        fake_run("PASSED tests/test_foo.py::test_a\n1 passed in 0.10s"),
    )

    assert tester.test_changed() is True


def test_test_changed_returns_true_when_pytest_execution_raises(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run(PASSING_OUTPUT))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")
    tester.test_before()

    def raise_run(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr("utility.pytest_tester.subprocess.run", raise_run)

    assert tester.test_changed() is True


def test_run_pytest_raises_on_unexpected_return_code(monkeypatch):
    monkeypatch.setattr("utility.pytest_tester.subprocess.run", fake_run("boom", returncode=2))
    tester = PytestTester(pyenv_name="3.12", test_file_path="tests")

    with pytest.raises(Exception, match="Pytest execution failed"):
        tester.test_before()
