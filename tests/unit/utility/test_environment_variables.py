import pytest

from utility.environment_variables import get_env_variable


def test_get_env_variable_returns_value_when_set(monkeypatch):
    monkeypatch.setenv("SOME_TEST_VARIABLE", "value")
    monkeypatch.setattr("utility.environment_variables.load_dotenv", lambda: None)

    assert get_env_variable("SOME_TEST_VARIABLE") == "value"


def test_get_env_variable_raises_when_missing(monkeypatch):
    monkeypatch.delenv("SOME_MISSING_VARIABLE", raising=False)
    monkeypatch.setattr("utility.environment_variables.load_dotenv", lambda: None)

    with pytest.raises(ValueError, match="SOME_MISSING_VARIABLE"):
        get_env_variable("SOME_MISSING_VARIABLE")
