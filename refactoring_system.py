import time
from datetime import timedelta
from pathlib import Path

from llm.llm import LLM
from refactoring.refactoring import Refactoring
from tree_of_thoughts.refactoring_category import RefactoringCategory
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from tree_of_thoughts.refactoring_generator import RefactoringGenerator
from utility.cli import CLI
from utility.code_divider import CodeDivider
from utility.code_file import CodeFile
from utility.compiler import Compiler
from utility.config import Config
from utility.git_repository import GitRepository
from utility.pytest_tester import PytestTester
from utility.readability_analyzer import ReadabilityAnalyzer
from utility.refactoring_system_state import RefactoringSystemState


class RefactoringSystem:
    def __init__(self, config: Config, llm: LLM, count: int, code_divider_class: type[CodeDivider], approximate_segment_length: int):
        self.config = config
        self.code_divider_class = code_divider_class
        self.approximate_segment_length = approximate_segment_length

        self.git_repository = GitRepository(config.get_absolute_git_repo_path())
        self.refactoring_generator = RefactoringGenerator(llm, count)
        self.refactoring_evaluator = RefactoringEvaluator(llm)
        self.tester = PytestTester(pyenv_name=config.pyenv_name,
                                   test_file_path=config.get_absolute_test_file_path())

        statistics_directory = config.get_absolute_statistics_directory()
        self.state_path = statistics_directory + "/refactoring_state.json"

    def run(self):
        start = time.time()
        self._setup()

        filepaths = self.config.get_absolute_file_paths()
        for file_index in range(self.state.file_index, len(filepaths)):
            self.state = RefactoringSystemState(file_index=file_index).bind(self.state_path)
            self._refactor_file(filepaths[file_index])

        RefactoringSystemState.clear(self.state_path)
        print(f"Finished refactoring in {self._format_timespan(time.time() - start)}")

    def _refactor_file(self, filepath: str):
        CLI.print_banner(
            f"Starting refactoring for {Path(filepath).name}", symbol="=", empty_line_count=2)
        # Run tests before starting the refactoring process to establish a baseline
        print(f"Test results before refactoring: {self.tester.test_before()}")

        print(f"Analyzing readability metrics for {filepath}...")
        print(ReadabilityAnalyzer.analyze_file(filepath))

        code = self._read_file(filepath)
        self.code_file = CodeFile(code, self.code_divider_class(self.approximate_segment_length))
        self.code_file.print_segment_lengths()

        for iteration in range(self.state.iteration, self.config.max_iterations):
            iteration_start = time.time()
            CLI.print_banner(f"Iteration {iteration + 1}")
            self._do_iteration(filepath)
            self.state.iteration = iteration + 1
            self.state.segment_index = 0
            print(
                f"Iteration {iteration + 1} completed in {self._format_timespan(time.time() - iteration_start)}")

    def _do_iteration(self, filepath: str):
        self._print_available_categories()

        segment_ids = self.code_file.segment_ids()
        already_done_count = self.state.segment_index

        for position, segment_id in enumerate(segment_ids[already_done_count:], start=already_done_count):
            categories = self.state.categories_for_segment(segment_id)
            if len(categories) > 0:
                self._refactor_segment(
                    segment_id, filepath, categories)
            else:
                CLI.print_debug(
                    f"No more categories available for segment {segment_id + 1}. Skipping refactoring for this segment.")

            self.state.segment_index = position + 1

    def _refactor_segment(self, segment_id: int, filepath: str, categories: list[RefactoringCategory]):
        CLI.print_banner(
            f"Segment {segment_id + 1}", symbol="-")
        commit_history = self.git_repository.get_commit_history()
        refactoring_suggestions = self.refactoring_generator.generate_refactorings(
            self.code_file, segment_id, commit_history=commit_history, categories=categories)

        if refactoring_suggestions == []:
            CLI.print_debug(f"No refactoring suggestions generated for segment in {filepath}.")
            return

        self.refactoring_evaluator.batch_evaluate(refactoring_suggestions)

        self._analyze_refactorings(filepath, refactoring_suggestions)

        sorted_refactorings = self._sort_refactorings_by_evaluation(refactoring_suggestions)
        self._print_refactorings(sorted_refactorings)
        final_candidates = self._filter_refactorings(sorted_refactorings)

        if self.config.show_tree:
            self._apply_all_refactorings(sorted_refactorings, filepath, segment_id)
        elif final_candidates:
            self._apply_best_refactoring(final_candidates[0], filepath)
        else:
            CLI.print_debug(f"No valid refactoring found for segment in {filepath}.")

    def _analyze_refactorings(self, filepath, refactoring_suggestions: list[Refactoring]):
        original_code_file = self.code_file
        for refactoring in refactoring_suggestions:
            self._apply_refactoring(refactoring, filepath, remember=False)
            refactoring.set_compiles(Compiler.try_compile_file(filepath))
            refactoring.set_tests_changed(self.tester.test_changed())
            refactoring.set_metrics(ReadabilityAnalyzer.analyze_file(filepath))
            # revert refactoring to original code
            self._write_file(filepath, original_code_file.code)

    def _setup(self):
        self.state = RefactoringSystemState.load_if_exists(self.state_path)
        if self.state is not None:
            self.git_repository.checkout_branch(self.config.branch_name)
            CLI.print_debug(
                f"Resuming from checkpoint: file {self.state.file_index + 1}, "
                f"iteration {self.state.iteration + 1}, segment {self.state.segment_index + 1}")
        else:
            self.state = RefactoringSystemState().bind(self.state_path)
            if self.git_repository.branch_exists(self.config.branch_name):
                self.git_repository.checkout_branch(self.config.branch_name)
            else:
                self.git_repository.create_branch(self.config.branch_name)

    def _apply_best_refactoring(self, best_refactoring: Refactoring, filepath: str):
        self._apply_refactoring(best_refactoring, filepath, remember=True)
        self.git_repository.commit_changes(best_refactoring.get_commit_message())

    def _apply_all_refactorings(self, sorted_refactorings: list[Refactoring], filepath: str, code_segment_id: int):
        if len(sorted_refactorings) == 0:
            return

        best_refactoring = None

        for refactoring in sorted_refactorings:
            self.git_repository.create_branch(
                f"{self.state.file_index}_{self.state.iteration}_{code_segment_id}_{refactoring.category.get_name()}")
            self._apply_refactoring(refactoring, filepath, remember=False)
            self.git_repository.commit_changes(refactoring.get_commit_message())
            if best_refactoring is None and self._is_valid_refactoring(refactoring):
                best_refactoring = refactoring
                self.git_repository.move_branch(self.config.branch_name)
            self.git_repository.go_to_previous_commit()
        self.git_repository.checkout_branch(self.config.branch_name)

        # Update the code file with the best refactoring if it exists
        if best_refactoring is not None:
            self.code_file = best_refactoring.code_file

    def _sort_refactorings_by_evaluation(self, refactorings: list) -> list:
        return sorted(refactorings, key=lambda r: r.evaluation.sorting_value() if r.evaluation else -4, reverse=True)

    def _filter_refactorings(self, refactorings: list) -> list:
        filtered_refactorings = []
        for refactoring in refactorings:
            if self._is_valid_refactoring(refactoring):
                filtered_refactorings.append(refactoring)
        return filtered_refactorings

    def _is_valid_refactoring(self, refactoring: Refactoring) -> bool:
        return refactoring.evaluation and refactoring.evaluation.correct and refactoring.evaluation.grade > 0 and refactoring.compiles and not refactoring.tests_changed

    def _print_refactorings(self, sorted_refactorings):
        for i, refactoring in enumerate(sorted_refactorings):
            print(f"{i+1}. {self._refactoring_printable_string(refactoring)}")

    def _refactoring_printable_string(self, refactoring: Refactoring) -> str:
        tool_name = refactoring.tool_name()

        if not refactoring.evaluation:
            return f"no evaluation, {tool_name}"
        else:
            # Get the first line of the description
            short_description = refactoring.evaluation.description.splitlines()[
                0]
            correct_string = "Correct" if refactoring.evaluation.correct else "Incorrect"
            return f"{correct_string}, {refactoring.evaluation.grade}, {short_description}, {tool_name}"

    def _apply_refactoring(self, refactoring: Refactoring, filepath, remember: bool = True):
        new_code_file = refactoring.code_file if refactoring.code_file is not None else self.code_file
        self._write_file(filepath, new_code_file.code)
        if remember:
            self.code_file = new_code_file

    def _format_timespan(self, seconds: float) -> str:
        return str(timedelta(seconds=seconds))

    def _read_file(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()

    def _write_file(self, filepath: str, content: str):
        with open(filepath, "w") as f:
            f.write(content)

    def _print_available_categories(self):
        for segment_id in self.code_file.segment_ids():
            categories = self.state.categories_for_segment(segment_id)
            print(
                f"Segment {segment_id+1}: {', '.join([category.get_name() for category in categories])}")
