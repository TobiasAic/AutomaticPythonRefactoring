# AI-generated

from __future__ import annotations

import threading
import time

import pytest

from llm.llm_types import LLMResponse
from llm.logging_llm import LoggingLLM
from llm.parallel_llm import ParallelLLM
from llm.retrying_llm import RetryingLLM


class FakeLLM:
    def __init__(self):
        self.model_name = "fake-model"
        self.calls: list[tuple[str, list[dict]]] = []
        self.calls_by_prompt: dict[str, list[dict]] = {}
        self.require_tool_call_by_prompt: dict[str, bool] = {}
        self._lock = threading.Lock()

    def generate(self, prompt: str, tools: list[dict] | None = None, require_tool_call: bool = False):
        tool_list = tools or []
        with self._lock:
            self.calls.append((prompt, tool_list))
            self.calls_by_prompt[prompt] = tool_list
            self.require_tool_call_by_prompt[prompt] = require_tool_call

        if prompt == "slow":
            time.sleep(0.05)
        elif prompt == "fast":
            time.sleep(0.01)

        return LLMResponse(text=prompt.upper())


class DummyProgressBar:
    def __init__(self, *args, **kwargs):
        self.updates = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, amount: int):
        self.updates += amount


def test_logging_llm_logs_timing_and_delegates_attributes(monkeypatch):
    fake_llm = FakeLLM()
    logging_llm = LoggingLLM(fake_llm)
    messages: list[str] = []
    time_values = iter([100.0, 102.3456])

    monkeypatch.setattr("llm.logging_llm.CLI.print_debug", lambda message: messages.append(message))
    monkeypatch.setattr("llm.logging_llm.time.time", lambda: next(time_values))

    response = logging_llm.generate("prompt", tools=[{"name": "tool"}])

    assert response == LLMResponse(text="PROMPT")
    assert messages == ["Generated response in 2.35 seconds"]
    assert logging_llm.model_name == "fake-model"


def test_parallel_llm_preserves_result_order_and_tools(monkeypatch):
    fake_llm = FakeLLM()
    parallel_llm = ParallelLLM(fake_llm)
    prompts = ["slow", "fast"]
    tools = [[{"name": "slow-tool"}], [{"name": "fast-tool"}]]

    monkeypatch.setattr("llm.parallel_llm.tqdm", lambda *args, **kwargs: DummyProgressBar())

    responses = parallel_llm.batch_generate(prompts, tools=tools)

    assert responses == [LLMResponse(text="SLOW"), LLMResponse(text="FAST")]
    assert fake_llm.calls_by_prompt == {
        "slow": [{"name": "slow-tool"}],
        "fast": [{"name": "fast-tool"}],
    }


def test_parallel_llm_passes_require_tool_call_through(monkeypatch):
    fake_llm = FakeLLM()
    parallel_llm = ParallelLLM(fake_llm)

    monkeypatch.setattr("llm.parallel_llm.tqdm", lambda *args, **kwargs: DummyProgressBar())

    parallel_llm.batch_generate(["slow", "fast"], require_tool_call=True)

    assert fake_llm.require_tool_call_by_prompt == {"slow": True, "fast": True}


def test_parallel_llm_defaults_tools_to_empty_lists(monkeypatch):
    fake_llm = FakeLLM()
    parallel_llm = ParallelLLM(fake_llm)

    monkeypatch.setattr("llm.parallel_llm.tqdm", lambda *args, **kwargs: DummyProgressBar())

    responses = parallel_llm.batch_generate(["one", "two"])

    assert responses == [LLMResponse(text="ONE"), LLMResponse(text="TWO")]
    assert fake_llm.calls_by_prompt == {"one": [], "two": []}


def test_parallel_llm_rejects_mismatched_tool_counts():
    parallel_llm = ParallelLLM(FakeLLM())

    with pytest.raises(ValueError, match="Length of tools list must match length of prompts list"):
        parallel_llm.batch_generate(["only-one"], tools=[[], []])


def test_parallel_llm_limits_batch_size():
    parallel_llm = ParallelLLM(FakeLLM())

    prompts = [f"prompt-{index}" for index in range(11)]

    with pytest.raises(ValueError, match="Batch generation is limited to 10 prompts at a time"):
        parallel_llm.batch_generate(prompts)


class FlakyLLM:
    def __init__(self, failures_before_success: int):
        self.model_name = "flaky-model"
        self.failures_before_success = failures_before_success
        self.attempts = 0

    def generate(self, prompt: str, tools=None, require_tool_call: bool = False):
        self.attempts += 1
        if self.attempts <= self.failures_before_success:
            raise RuntimeError(f"attempt {self.attempts} failed")
        return LLMResponse(text=prompt.upper())


def test_retrying_llm_returns_result_once_it_succeeds(monkeypatch):
    monkeypatch.setattr("llm.retrying_llm.time.sleep", lambda seconds: None)
    flaky_llm = FlakyLLM(failures_before_success=2)
    retrying_llm = RetryingLLM(flaky_llm, max_retries=3, delay_seconds=0)

    response = retrying_llm.generate("prompt")

    assert response == LLMResponse(text="PROMPT")
    assert flaky_llm.attempts == 3


def test_retrying_llm_raises_last_exception_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr("llm.retrying_llm.time.sleep", lambda seconds: None)
    flaky_llm = FlakyLLM(failures_before_success=5)
    retrying_llm = RetryingLLM(flaky_llm, max_retries=3, delay_seconds=0)

    with pytest.raises(RuntimeError, match="attempt 3 failed"):
        retrying_llm.generate("prompt")

    assert flaky_llm.attempts == 3


def test_retrying_llm_delegates_unknown_attributes():
    retrying_llm = RetryingLLM(FakeLLM())

    assert retrying_llm.model_name == "fake-model"