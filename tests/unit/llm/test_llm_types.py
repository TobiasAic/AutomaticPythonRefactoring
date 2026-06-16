import json

from llm.llm_types import LLMResponse, ToolCall


def test_llm_response_json_with_text():
    response = LLMResponse(text="hello", tool_call=None)

    restored = LLMResponse.from_json(response.to_json())

    assert restored == response


def test_llm_response_json_with_tool_call():
    response = LLMResponse(
        text=None,
        tool_call=ToolCall(name="rename", arguments={"line_number": "5", "old_name": "x", "new_name": "y"}),
    )

    restored = LLMResponse.from_json(response.to_json())

    assert restored == response
