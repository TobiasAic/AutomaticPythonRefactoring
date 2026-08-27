from pathlib import Path

from llm.llm import LLM
from refactoring.refactoring import Refactoring
from tree_of_thoughts.refactoring_category import RefactoringCategory
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from tree_of_thoughts.refactoring_generator import RefactoringGenerator
from utility.cli import CLI
from utility.compiler import Compiler
from utility.config import Config
from utility.git_repository import GitRepository
from utility.pytest_tester import PytestTester
from utility.readability_analyzer import ReadabilityAnalyzer
from utility.refactoring_system_state import RefactoringSystemState


class RefactoringSystem:
    def __init__(self, config: Config, llm: LLM, count: int, category_attempt_count: int = 1):
        self.config = config
        self.category_attempt_count = category_attempt_count

        self.git_repository = GitRepository(config.get_absolute_git_repo_path())
        self.refactoring_generator = RefactoringGenerator(llm, count, self.remove_category)
        self.refactoring_evaluator = RefactoringEvaluator(llm)
        self.tester = PytestTester(pyenv_name=config.pyenv_name,
                                   test_file_path=config.get_absolute_test_file_path())

        statistics_directory = config.get_absolute_statistics_directory()
        self.state_path = statistics_directory + "/refactoring_state.json"

    def run(self):
        with CLI.print_with_duration("Finished refactoring."):
            self._setup()

            filepaths = self.config.get_absolute_file_paths()
            for file_index in range(self.state.file_index, len(filepaths)):
                if file_index != self.state.file_index:
                    self.state = RefactoringSystemState.initial(
                        self.category_attempt_count, file_index=file_index).bind(self.state_path)
                self._refactor_file(filepaths[file_index])

            RefactoringSystemState.clear(self.state_path)

    def _setup(self):
        self.state = RefactoringSystemState.load_if_exists(self.state_path)
        if self.state is not None:
            self.git_repository.checkout_branch(self.config.branch_name)
            CLI.print_debug(
                f"Resuming from checkpoint: file {self.state.file_index + 1}, "
                f"iteration {self.state.iteration + 1}, segment {self.state.segment_index + 1}")
        else:
            self.state = RefactoringSystemState.initial(self.category_attempt_count).bind(self.state_path)
            if self.git_repository.branch_exists(self.config.branch_name):
                self.git_repository.checkout_branch(self.config.branch_name)
            else:
                self.git_repository.create_branch(self.config.branch_name)

    def _refactor_file(self, filepath: str):
        CLI.print_banner(
            f"Starting refactoring for {Path(filepath).name}", symbol="=", empty_line_count=2)
        # Run tests before starting the refactoring process to establish a baseline
        print(f"Test results before refactoring: {self.tester.test_before()}")

        print(f"Analyzing readability metrics for {filepath}...")
        print(ReadabilityAnalyzer.analyze_file(filepath))

        for iteration in range(self.state.iteration, self.config.max_iterations):
            with CLI.print_with_duration(f"Iteration {iteration + 1} completed"):
                CLI.print_banner(f"Iteration {iteration + 1}")
                if self._categories_available():
                    self._print_available_categories()
                    self._do_iteration(filepath)
                else:
                    print("No more categories, dont")
                    break
                self.state.iteration = iteration + 1

    def _categories_available(self) -> bool:
        for category_count in self.state.categories.values():
            if category_count > 0:
                return True
        return False

    def _do_iteration(self, filepath: str):
        refactoring_suggestions = self._generate_refactorings(filepath)

        if refactoring_suggestions == []:
            CLI.print_debug(f"No refactoring suggestions generated for segment in {filepath}.")
            return

        sorted_refactorings, final_candidates = self._evaluate_refactorings(
            filepath, refactoring_suggestions)
        self._apply_generated_refactoring(filepath, sorted_refactorings, final_candidates)

    def _generate_refactorings(self, filepath):
        code = self._read_file(filepath)
        commit_history = self.git_repository.get_commit_history()
        categories = [category for category, count in self.state.categories.items() if count > 0]
        refactoring_suggestions = self.refactoring_generator.generate_refactorings(
            code=code, commit_history=commit_history, categories=categories)
        return refactoring_suggestions

    def remove_category(self, category: RefactoringCategory):
        self.state.categories[category] -= 1

    def _evaluate_refactorings(self, filepath, refactoring_suggestions):
        self.refactoring_evaluator.batch_evaluate(refactoring_suggestions)

        for refactoring in refactoring_suggestions:
            with self._refactoring_applied():
                refactoring.set_compiles(Compiler.try_compile_file(filepath))
                refactoring.set_tests_changed(self.tester.test_changed())
                refactoring.set_metrics(ReadabilityAnalyzer.analyze_file(filepath))

        sorted_refactorings = self._sort_refactorings_by_evaluation(refactoring_suggestions)
        self._print_refactorings(sorted_refactorings)
        final_candidates = self._filter_refactorings(sorted_refactorings)
        return sorted_refactorings, final_candidates

    def _apply_generated_refactoring(self, filepath, sorted_refactorings, final_candidates):
        if self.config.show_tree:
            self._apply_all_refactorings(sorted_refactorings, filepath)
        elif final_candidates:
            self._apply_best_refactoring(final_candidates[0], filepath)
        else:
            CLI.print_debug(f"No valid refactoring found for segment in {filepath}.")

    def _apply_best_refactoring(self, best_refactoring: Refactoring, filepath: str):
        self._apply_refactoring(best_refactoring, filepath, remember=True)
        self.git_repository.commit_changes(best_refactoring.get_commit_message())

    def _apply_all_refactorings(self, sorted_refactorings: list[Refactoring], filepath: str, code_segment_id: int):
        if len(sorted_refactorings) == 0:
            return

        best_refactoring_found = False 

        for refactoring in sorted_refactorings:
            self.git_repository.create_branch(
                f"{self.state.file_index}_{self.state.iteration}_{code_segment_id}_{refactoring.category.get_name()}")
            self._apply_refactoring(refactoring, filepath, remember=False)
            self.git_repository.commit_changes(refactoring.get_commit_message())
            if not best_refactoring_found and refactoring.is_valid():
                best_refactoring_found = True
                self.git_repository.move_branch(self.config.branch_name)
            self.git_repository.go_to_previous_commit()
        self.git_repository.checkout_branch(self.config.branch_name)

    def _sort_refactorings_by_evaluation(self, refactorings: list) -> list:
        return sorted(refactorings, key=lambda r: r.evaluation.sorting_value() if r.evaluation else -4, reverse=True)

    def _filter_refactorings(self, refactorings: list[Refactoring]) -> list:
        filtered_refactorings = []
        for refactoring in refactorings:
            if refactoring.is_valid():
                filtered_refactorings.append(refactoring)
        return filtered_refactorings

    def _print_refactorings(self, sorted_refactorings: list[Refactoring]):
        for i, refactoring in enumerate(sorted_refactorings):
            print(f"{i+1}. {refactoring.to_string()}")

    def _apply_refactoring(self, refactoring: Refactoring, filepath):
        self._write_file(filepath, refactoring.new_code)

    def _refactoring_applied(self, refactoring: Refactoring, filepath):
        original_code = self._read_file(filepath)
        self._apply_refactoring(refactoring, filepath)
        yield
        self._write_file(filepath, original_code)

    def _read_file(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()

    def _write_file(self, filepath: str, content: str):
        with open(filepath, "w") as f:
            f.write(content)

    def _print_available_categories(self):
        for category, count in self.state.categories.items():
            print(f"{category}: {count}")
