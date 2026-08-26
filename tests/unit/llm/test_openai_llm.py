from types import SimpleNamespace

import pytest

from llm.llm_types import LLMConfig, LLMResponse, ToolCall
from llm.openai_llm import OpenAILLM


class FakeCompletions:
    def __init__(self, response):
        self._response = response
        self.last_call_kwargs = None

    def create(self, **kwargs):
        self.last_call_kwargs = kwargs
        return self._response


def make_llm(monkeypatch, response) -> OpenAILLM:
    monkeypatch.setattr("llm.openai_llm.OpenAI", lambda **kwargs: SimpleNamespace())
    llm = OpenAILLM(LLMConfig(api_key="key", base_url="https://example.com", model_name="test-model"))
    llm.client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(response)))
    return llm


def text_response(text: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content=text, tool_calls=None))]
    )


def tool_call_response(name: str, arguments: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[SimpleNamespace(function=SimpleNamespace(name=name, arguments=arguments))],
                ),
            )
        ]
    )


def test_generate_returns_text_response(monkeypatch):
    llm = make_llm(monkeypatch, text_response("hello"))

    response = llm.generate("prompt")

    assert response == LLMResponse(text="hello", tool_call=None)


def test_generate_returns_tool_call_response(monkeypatch):
    llm = make_llm(monkeypatch, tool_call_response("rename", '{"old_name": "x"}'))

    response = llm.generate("prompt")

    assert response == LLMResponse(text=None, tool_call=ToolCall(name="rename", arguments='{"old_name": "x"}'))


def test_generate_passes_prompt_and_tools_to_the_client(monkeypatch):
    llm = make_llm(monkeypatch, text_response("hello"))
    tools = [{"name": "some_tool"}]

    llm.generate("prompt", tools=tools)

    assert llm.client.chat.completions.last_call_kwargs["messages"] == [{"role": "user", "content": "prompt"}]
    assert llm.client.chat.completions.last_call_kwargs["tools"] == tools


def test_batch_generate_returns_one_response_per_prompt(monkeypatch):
    llm = make_llm(monkeypatch, text_response("hello"))
    monkeypatch.setattr("llm.openai_llm.tqdm", lambda iterable, **kwargs: iterable)

    responses = llm.batch_generate(["a", "b"])

    assert responses == [LLMResponse(text="hello"), LLMResponse(text="hello")]


def test_batch_generate_rejects_mismatched_tool_counts(monkeypatch):
    llm = make_llm(monkeypatch, text_response("hello"))

    with pytest.raises(ValueError, match="Length of tools list must match length of prompts list"):
        llm.batch_generate(["a", "b"], tools=[[]])
