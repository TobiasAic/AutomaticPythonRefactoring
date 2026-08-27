# AI-generated

import pytest

from refactoring.rope_refactoring import RopeRefactoring


def test_tool_name_is_rope():
    class NoOpRopeRefactoring(RopeRefactoring):
        def execute_rope_refactoring(self, project, filepath, code, refactoring_arguments):
            pass

    refactoring = NoOpRopeRefactoring("x = 1\n", refactoring_arguments=None)

    assert refactoring.tool_name() == "Rope"
    assert refactoring.old_code == "x = 1\n"
    assert refactoring.new_code == "x = 1\n"


def test_execute_rope_refactoring_must_be_implemented_by_subclasses():
    with pytest.raises(TypeError):
        RopeRefactoring("x = 1\n", refactoring_arguments=None)
