from __future__ import annotations

import threading
import time

import pytest

from llm.llm_types import LLMResponse
from llm.logging_llm import LoggingLLM
from llm.parallel_llm import ParallelLLM


class FakeLLM:
    def __init__(self):
        self.model_name = "fake-model"
        self.calls: list[tuple[str, list[dict]]] = []
        self.calls_by_prompt: dict[str, list[dict]] = {}
        self._lock = threading.Lock()

    def generate(self, prompt: str, tools: list[dict] | None = None):
        tool_list = tools or []
        with self._lock:
            self.calls.append((prompt, tool_list))
            self.calls_by_prompt[prompt] = tool_list

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