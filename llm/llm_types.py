from dataclasses import dataclass

@dataclass
class OpenAILLMConfig:
    api_key: str
    base_url: str
    model_name: str

@dataclass
class LLMResponse:
    """Represents a response from the LLM, including the generated content and any tool calls."""
    text: str | None = None
    tool_call: ToolCall | None = None

@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""
    name: str
    arguments: dict