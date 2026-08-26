import json

import pytest

from llm.llm_types import LLMResponse, ToolCall
from tree_of_thoughts.refactoring_category import ALL_CATEGORIES, CONDITIONAL_LOGIC
from tree_of_thoughts.refactoring_generator import RefactoringGenerator


class ScriptedLLM:
    def __init__(self, responses):
        self.responses = responses
        self.batch_calls = []

    def batch_generate(self, prompts, tools):
        self.batch_calls.append((prompts, tools))
        return self.responses


def test_init_rejects_count_exceeding_available_categories():
    with pytest.raises(ValueError):
        RefactoringGenerator(ScriptedLLM([]), count=len(ALL_CATEGORIES) + 1)


def test_generate_refactorings_removes_category_when_llm_finds_nothing():
    response = LLMResponse(tool_call=ToolCall(name="no_refactoring", arguments="{}"))
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)
    categories = [CONDITIONAL_LOGIC]

    refactorings = generator.generate_refactorings("x = 1\n", commit_history=[], categories=categories)

    assert refactorings == []
    assert categories == []


def test_generate_refactorings_builds_refactoring_from_apply_edits_tool_call():
    arguments = json.dumps({"edits": [{"old_code": "x = 1", "new_code": "x = 2"}]})
    response = LLMResponse(tool_call=ToolCall(name="apply_edits", arguments=arguments))
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)
    categories = [CONDITIONAL_LOGIC]

    refactorings = generator.generate_refactorings("x = 1\n", commit_history=[], categories=categories)

    assert len(refactorings) == 1
    assert refactorings[0].new_code == "x = 2\n"
    assert refactorings[0].category is CONDITIONAL_LOGIC
    assert categories == [CONDITIONAL_LOGIC]  # category stays available for future rounds


def test_generate_refactorings_skips_response_with_no_tool_call():
    response = LLMResponse(text="I cannot comply", tool_call=None)
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)

    refactorings = generator.generate_refactorings("x = 1\n", commit_history=[], categories=[CONDITIONAL_LOGIC])

    assert refactorings == []


def test_generate_refactorings_skips_unknown_tool_name():
    response = LLMResponse(tool_call=ToolCall(name="unknown_tool", arguments="{}"))
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)

    refactorings = generator.generate_refactorings("x = 1\n", commit_history=[], categories=[CONDITIONAL_LOGIC])

    assert refactorings == []


def test_generate_refactorings_skips_apply_edits_call_that_fails_validation():
    arguments = json.dumps({"edits": [{"old_code": "does not exist", "new_code": "x"}]})
    response = LLMResponse(tool_call=ToolCall(name="apply_edits", arguments=arguments))
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)

    refactorings = generator.generate_refactorings("x = 1\n", commit_history=[], categories=[CONDITIONAL_LOGIC])

    assert refactorings == []


def test_generate_refactorings_passes_code_segment_history_and_category_prompt_to_llm():
    response = LLMResponse(tool_call=ToolCall(name="no_refactoring", arguments="{}"))
    llm = ScriptedLLM([response])
    generator = RefactoringGenerator(llm, count=1)

    generator.generate_refactorings("x = 1\n", commit_history=["prior commit"], categories=[CONDITIONAL_LOGIC])

    prompts, tools = llm.batch_calls[0]
    assert len(prompts) == 1
    assert "x = 1" in prompts[0]
    assert "prior commit" in prompts[0]
    assert "CONDITIONAL_LOGIC" in prompts[0]
    assert any(tool["function"]["name"] == "apply_edits" for tool in tools[0])
    assert any(tool["function"]["name"] == "no_refactoring" for tool in tools[0])
