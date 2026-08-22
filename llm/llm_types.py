""" Types and data structures used in the LLM module. """

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMConfig:
    """ Represents the configuration to access an LLM at a specific endpoint. """
    api_key: str
    base_url: str
    model_name: str
    timeout: int = 600  # Default timeout in seconds for LLM requests


@dataclass
class LLMResponse:
    """ Represents a response from the LLM, including the generated content and any tool calls. """
    text: str | None = None
    tool_call: ToolCall | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "tool_call": self.tool_call.to_dict() if self.tool_call else None,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LLMResponse":
        return LLMResponse(
            text=data.get("text"),
            tool_call=ToolCall.from_dict(data["tool_call"]) if data.get("tool_call") else None,
        )

    @staticmethod
    def from_json(data: str) -> "LLMResponse":
        return LLMResponse.from_dict(json.loads(data))

@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""
    name: str
    arguments: dict

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ToolCall":
        return ToolCall(
            name=data["name"],
            arguments=data["arguments"],
        )
