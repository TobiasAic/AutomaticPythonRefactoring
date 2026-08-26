from utility.refactoring_system_state import RefactoringSystemState
from tree_of_thoughts.refactoring_category import ALL_CATEGORIES, CODE_QUALITY


def test_new_state_has_default_progress_values():
    state = RefactoringSystemState()

    assert state.file_index == 0
    assert state.iteration == 0
    assert state.segment_index == 0
    assert state.categories_by_segment == {}


def test_categories_for_segment_returns_all_categories_on_first_access():
    state = RefactoringSystemState()

    categories = state.categories_for_segment(0)

    assert categories == list(ALL_CATEGORIES)


def test_categories_for_segment_reflects_previous_mutation():
    state = RefactoringSystemState()
    categories = state.categories_for_segment(0)
    categories.remove(CODE_QUALITY)

    assert state.categories_for_segment(0) == categories
    assert CODE_QUALITY not in state.categories_for_segment(0)


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "state.json"
    state = RefactoringSystemState(file_index=2, iteration=5, segment_index=1)
    state.categories_for_segment(0).remove(CODE_QUALITY)
    state.save(str(path))

    loaded = RefactoringSystemState.load(str(path))

    assert loaded.file_index == 2
    assert loaded.iteration == 5
    assert loaded.segment_index == 1
    assert loaded.categories_by_segment.keys() == {0}
    assert CODE_QUALITY not in loaded.categories_by_segment[0]


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
