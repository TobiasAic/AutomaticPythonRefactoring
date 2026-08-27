# AI-generated

from types import SimpleNamespace

from refactoring.refactoring import Refactoring
from refactoring.refactoring_evaluation import RefactoringEvaluation
from refactoring_system import RefactoringSystem
from tree_of_thoughts.refactoring_category import CONDITIONAL_LOGIC
from utility.refactoring_system_state import RefactoringSystemState


class FakeGitRepository:
    def __init__(self):
        self.commits = []

    def get_commit_history(self):
        return []

    def commit_changes(self, message):
        self.commits.append(message)
        return "deadbeef"


class FakeTester:
    def test_changed(self):
        return False


class FakeEvaluator:
    """ Leaves each refactoring's evaluation untouched instead of calling an LLM. """
    def batch_evaluate(self, refactorings):
        pass


class FakeGenerator:
    def __init__(self, refactorings):
        self._refactorings = refactorings

    def generate_refactorings(self, code, commit_history, categories):
        return self._refactorings


def make_system() -> RefactoringSystem:
    """Build a RefactoringSystem instance without running __init__, since the
    methods under test here are pure and don't touch any instance state that
    __init__ would normally set up (git repo, LLM, config, ...)."""
    return RefactoringSystem.__new__(RefactoringSystem)


def make_refactoring(correct: bool, grade: int, compiles: bool = True, tests_changed: bool = False) -> Refactoring:
    refactoring = Refactoring("old", "new")
    refactoring.set_evaluation(RefactoringEvaluation(description="desc", correct=correct, grade=grade))
    refactoring.set_compiles(compiles)
    refactoring.set_tests_changed(tests_changed)
    return refactoring


def test_sort_refactorings_by_evaluation_orders_by_grade_descending():
    system = make_system()
    low = make_refactoring(correct=True, grade=1)
    high = make_refactoring(correct=True, grade=3)
    mid = make_refactoring(correct=True, grade=2)

    sorted_refactorings = system._sort_refactorings_by_evaluation([low, high, mid])

    assert sorted_refactorings == [high, mid, low]


def test_sort_refactorings_by_evaluation_sorts_incorrect_and_unevaluated_last():
    system = make_system()
    valid = make_refactoring(correct=True, grade=1)
    incorrect = make_refactoring(correct=False, grade=3)
    unevaluated = Refactoring("old", "new")

    sorted_refactorings = system._sort_refactorings_by_evaluation([incorrect, valid, unevaluated])

    assert sorted_refactorings[0] is valid
    assert set(sorted_refactorings[1:]) == {incorrect, unevaluated}


def test_filter_refactorings_keeps_only_valid_refactorings():
    system = make_system()
    valid = make_refactoring(correct=True, grade=1)
    invalid = make_refactoring(correct=False, grade=1)

    filtered = system._filter_refactorings([valid, invalid])

    assert filtered == [valid]


def test_categories_available_is_true_when_any_category_has_attempts_left():
    system = make_system()
    system.state = RefactoringSystemState.initial(1)

    assert system._categories_available() is True


def test_categories_available_is_false_when_all_categories_are_exhausted():
    system = make_system()
    system.state = RefactoringSystemState.initial(0)

    assert system._categories_available() is False


def test_remove_category_decrements_its_count():
    system = make_system()
    system.state = RefactoringSystemState.initial(2)

    system.remove_category(CONDITIONAL_LOGIC)

    assert system.state.categories[CONDITIONAL_LOGIC] == 1


def test_refactoring_applied_writes_new_code_then_restores_original(tmp_path):
    filepath = tmp_path / "example.py"
    filepath.write_text("a = 1\n")
    system = make_system()
    refactoring = Refactoring(old_code="a = 1\n", new_code="a = 2\n")

    with system._refactoring_applied(refactoring, str(filepath)):
        assert filepath.read_text() == "a = 2\n"

    assert filepath.read_text() == "a = 1\n"


def test_do_iteration_skips_commit_when_no_suggestion_is_valid(tmp_path):
    """ Regression test: when every generated refactoring is rejected (e.g. graded <= 0
    or marked incorrect), an iteration should leave the file and commit history untouched
    instead of committing or crashing. """
    code = "a = 1\n"
    filepath = tmp_path / "example.py"
    filepath.write_text(code)
    filepath = str(filepath)

    system = make_system()
    system.config = SimpleNamespace(show_tree=False)
    system.git_repository = FakeGitRepository()
    system.tester = FakeTester()
    system.refactoring_evaluator = FakeEvaluator()
    system.state = RefactoringSystemState.initial(1)

    invalid_refactoring = make_refactoring(correct=False, grade=3)
    system.refactoring_generator = FakeGenerator([invalid_refactoring])

    system._do_iteration(filepath)

    assert system.git_repository.commits == []
    assert open(filepath).read() == code
