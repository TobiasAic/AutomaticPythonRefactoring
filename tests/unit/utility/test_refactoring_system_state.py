# AI-generated

from utility.refactoring_system_state import RefactoringSystemState
from tree_of_thoughts.refactoring_category import ALL_CATEGORIES, CODE_QUALITY


def test_new_state_has_default_progress_values():
    state = RefactoringSystemState()

    assert state.file_index == 0
    assert state.iteration == 0
    assert state.categories == {category: 1 for category in ALL_CATEGORIES}


def test_initial_gives_every_category_the_given_attempt_count():
    state = RefactoringSystemState.initial(category_count=3, file_index=2)

    assert state.file_index == 2
    assert state.categories == {category: 3 for category in ALL_CATEGORIES}


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "state.json"
    state = RefactoringSystemState(file_index=2, iteration=5)
    state.categories[CODE_QUALITY] = 0
    state.save(str(path))

    loaded = RefactoringSystemState.load(str(path))

    assert loaded.file_index == 2
    assert loaded.iteration == 5
    assert loaded.categories[CODE_QUALITY] == 0


def test_bind_autosaves_on_every_field_change(tmp_path):
    path = tmp_path / "state.json"
    state = RefactoringSystemState().bind(str(path))

    state.iteration = 3

    reloaded = RefactoringSystemState.load(str(path))
    assert reloaded.iteration == 3


def test_state_does_not_save_before_being_bound(tmp_path):
    path = tmp_path / "state.json"
    state = RefactoringSystemState()

    state.iteration = 1

    assert not path.exists()


def test_load_if_exists_returns_none_when_missing(tmp_path):
    path = tmp_path / "missing.json"

    assert RefactoringSystemState.load_if_exists(str(path)) is None


def test_load_if_exists_returns_state_when_present(tmp_path):
    path = tmp_path / "state.json"
    RefactoringSystemState(iteration=7).save(str(path))

    loaded = RefactoringSystemState.load_if_exists(str(path))

    assert loaded.iteration == 7


def test_clear_removes_existing_file(tmp_path):
    path = tmp_path / "state.json"
    RefactoringSystemState().save(str(path))

    RefactoringSystemState.clear(str(path))

    assert not path.exists()


def test_clear_is_a_no_op_when_file_missing(tmp_path):
    path = tmp_path / "missing.json"

    RefactoringSystemState.clear(str(path))  # should not raise
