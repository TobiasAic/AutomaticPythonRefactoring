import pytest

from refactoring.rope_refactoring import RopeRefactoring
from tests.unit.refactoring.shared import single_segment_code_file


def test_tool_name_is_rope():
    class NoOpRopeRefactoring(RopeRefactoring):
        def execute_rope_refactoring(self, project, filepath, code_file, segment_id, refactoring_arguments):
            pass

    code_file = single_segment_code_file("x = 1\n")

    refactoring = NoOpRopeRefactoring(code_file, 0, refactoring_arguments=None)

    assert refactoring.tool_name() == "Rope"
    assert refactoring.old_code == "x = 1\n"
    assert refactoring.new_code == "x = 1\n"


def test_execute_rope_refactoring_must_be_implemented_by_subclasses():
    code_file = single_segment_code_file("x = 1\n")

    with pytest.raises(NotImplementedError):
        RopeRefactoring(code_file, 0, refactoring_arguments=None)
