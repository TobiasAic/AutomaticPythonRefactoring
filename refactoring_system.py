import time
from datetime import timedelta
from pathlib import Path

from llm.llm import LLM
from refactoring.refactoring import Refactoring
from tree_of_thoughts.refactoring_category import RefactoringCategory
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from tree_of_thoughts.refactoring_generator import RefactoringGenerator
from utility.cli import CLI
from utility.code_divider import CodeDivider, CodeSegment
from utility.compiler import Compiler
from utility.config import Config
from utility.git_repository import GitRepository
from utility.pytest_tester import PytestTester
from utility.readability_analyzer import ReadabilityAnalyzer
from utility.refactoring_system_state import RefactoringSystemState


class RefactoringSystem:
    def __init__(self, config: Config, llm: LLM, count: int, code_divider_class: type[CodeDivider], approximate_segment_length: int):
        self.config = config
        self.count = count
        self.llm = llm
        self.code_divider_class = code_divider_class
        self.approximate_segment_length = approximate_segment_length

        self.git_repository = GitRepository(
            config.get_absolute_git_repo_path())
        self.refactoring_evaluator = RefactoringEvaluator(llm)
        self.readability_analyzer = ReadabilityAnalyzer()
        self.tester = PytestTester(
            pyenv_name=config.pyenv_name, test_file_path=config.get_absolute_test_file_path())

        statistics_directory = config.get_absolute_statistics_directory()
        self.state_path = statistics_directory + "/refactoring_state.json"
        self.metrics_path = statistics_directory + "/readability_metrics.json"

    def run(self):
        start = time.time()

        self.state = RefactoringSystemState.load_if_exists(self.state_path)
        if self.state is not None:
            self.readability_analyzer.load(self.metrics_path)
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

        filepaths = self.config.get_absolute_file_paths()
        for file_index in range(self.state.file_index, len(filepaths)):
            self.file_index = file_index
            if file_index != self.state.file_index:
                self.state = RefactoringSystemState(file_index=file_index).bind(self.state_path)
            filepath = filepaths[file_index]
            self.refactor_file(filepath)
            self.readability_analyzer.plot_percentage_change(
                filepath, output_path=self.config.get_absolute_statistics_directory() + f"/{Path(filepath).stem}_readability_plot.png")

        self.readability_analyzer.save(self.metrics_path)
        RefactoringSystemState.clear(self.state_path)
        print(
            f"Finished refactoring in {self.format_timespan(time.time() - start)}")

    def refactor_file(self, filepath: str):
        CLI.print_banner(
            f"Starting refactoring for {Path(filepath).name}", symbol="=", empty_line_count=2)
        # Run tests before starting the refactoring process to establish a baseline
        print(f"Test results before refactoring: {self.tester.test_before()}")

        if filepath not in self.readability_analyzer.metrics:
            self.readability_analyzer.record_metrics(filepath)
            self.readability_analyzer.save(self.metrics_path)

        code = self.__read_file(filepath)
        code_divider = self.code_divider_class(
            code, self.approximate_segment_length)
        code_divider.print_segment_lengths()

        self.refactoring_generators = [
            RefactoringGenerator(self.llm, self.count)
            for segment in code_divider.get_segments()
        ]

        for iteration in range(self.state.iteration, self.config.max_iterations):
            self.iteration = iteration
            iteration_start = time.time()
            CLI.print_banner(
                f"Iteration {iteration + 1}")
            self.do_iteration(filepath, code_divider)
            self.state.iteration = iteration + 1
            self.state.segment_index = 0
            print(
                f"Iteration {iteration + 1} completed in {self.format_timespan(time.time() - iteration_start)}")

    def do_iteration(self, filepath: str, code_divider: CodeDivider):
        self.print_available_categories(code_divider)

        for segment in code_divider.get_segments()[self.state.segment_index:]:
            categories = self.state.categories_for_segment(segment.id)
            if len(categories) > 0:
                self.refactor_segment(
                    segment, filepath, code_divider, self.refactoring_generators[segment.id], categories)
            else:
                CLI.print_debug(
                    f"No more categories available for segment {segment.id+1}. Skipping refactoring for this segment.")

            self.state.segment_index = segment.id + 1

    def refactor_segment(self, code_segment: CodeSegment, filepath: str, code_divider: CodeDivider, refactoring_generator: RefactoringGenerator, categories: list[RefactoringCategory]):
        CLI.print_banner(
            f"Segment {code_segment.id + 1} - Current MI: {self.readability_analyzer.metrics[filepath][-1].maintainability_index}", symbol="-")
        commit_history = self.git_repository.get_commit_history()
        refactoring_suggestions = refactoring_generator.generate_refactorings(
            code_segment.code, commit_history=commit_history, categories=categories)

        if refactoring_suggestions == []:
            CLI.print_debug(
                f"No refactoring suggestions generated for segment in {filepath}.")
            return

        self.refactoring_evaluator.batch_evaluate(refactoring_suggestions)

        for refactoring in refactoring_suggestions:
            original_code = self.__read_file(filepath)
            self.apply_refactoring(
                refactoring, filepath, code_segment.id, code_divider, remember=False)
            refactoring.set_compiles(Compiler.try_compile_file(filepath))
            refactoring.set_tests_changed(self.tester.test_changed())
            refactoring.set_metrics(
                ReadabilityAnalyzer.analyze_file(filepath))
            # revert refactoring to original code
            self.__write_file(filepath, original_code)

        sorted_refactorings = self.sort_refactorings_by_evaluation(
            refactoring_suggestions)
        self.print_refactorings(sorted_refactorings)
        final_candidates = self.filter_refactorings(sorted_refactorings)

        if self.config.show_tree:
           self.apply_all_refactorings(sorted_refactorings, filepath, code_segment.id, code_divider) 
        else:
            self.apply_best_refactoring(
                final_candidates[0], filepath, code_segment.id, code_divider)

    def apply_best_refactoring(self, best_refactoring: Refactoring, filepath: str, code_segment_id: int, code_divider: CodeDivider):
        self.apply_refactoring(
            best_refactoring, filepath, code_segment_id, code_divider, remember=True)
        self.git_repository.commit_changes(best_refactoring.get_commit_message())

    def apply_all_refactorings(self, sorted_refactorings: list[Refactoring], filepath: str, code_segment_id: int, code_divider: CodeDivider):
        if len(sorted_refactorings) == 0:
            return

        best_refactoring = None

        for refactoring in sorted_refactorings:
            self.git_repository.create_branch(f"{self.file_index}_{self.iteration}_{code_segment_id}_{refactoring.category.get_name()}")
            self.apply_refactoring(
                refactoring, filepath, code_segment_id, code_divider, remember=False)
            self.git_repository.commit_changes(refactoring.get_commit_message())
            if best_refactoring is None and self.is_valid_refactoring(refactoring):
                best_refactoring = refactoring
                self.git_repository.move_branch(self.config.branch_name)
            self.git_repository.go_to_previous_commit()
        self.git_repository.checkout_branch(self.config.branch_name)

        # Update the code segment with the best refactoring if it exists 
        if best_refactoring is not None:
            code_divider.replace_segment(
                CodeSegment(id=code_segment_id, code=best_refactoring.new_code), remember=True)

    def sort_refactorings_by_evaluation(self, refactorings: list) -> list:
        return sorted(refactorings, key=lambda r: r.evaluation.sorting_value() if r.evaluation else -4, reverse=True)

    def filter_refactorings(self, refactorings: list) -> list:
        filtered_refactorings = []
        for refactoring in refactorings:
            if self.is_valid_refactoring(refactoring):
                filtered_refactorings.append(refactoring)
        return filtered_refactorings

    def is_valid_refactoring(self, refactoring: Refactoring) -> bool:
        return refactoring.evaluation and refactoring.evaluation.correct and refactoring.evaluation.grade > 0 and refactoring.compiles and not refactoring.tests_changed

    def print_refactorings(self, sorted_refactorings):
        for i, refactoring in enumerate(sorted_refactorings):
            print(f"{i+1}. {self.refactoring_printable_string(refactoring)}")

    def refactoring_printable_string(self, refactoring: Refactoring) -> str:
        tool_name = refactoring.tool_name()

        if not refactoring.evaluation:
            return f"no evaluation, {tool_name}"
        else:
            # Get the first line of the description
            short_description = refactoring.evaluation.description.splitlines()[
                0]
            correct_string = "Correct" if refactoring.evaluation.correct else "Incorrect"
            return f"{correct_string}, {refactoring.evaluation.grade}, {short_description}, {tool_name}"

    def apply_refactoring(self, refactoring: Refactoring, filepath, segment_id: int, code_divider: CodeDivider, remember: bool = True):
        refactored_file = code_divider.replace_segment(CodeSegment(
            id=segment_id, code=refactoring.new_code), remember=remember)
        self.__write_file(filepath, refactored_file)

    def format_timespan(self, seconds: float) -> str:
        return str(timedelta(seconds=seconds))

    def __read_file(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()

    def __write_file(self, filepath: str, content: str):
        with open(filepath, "w") as f:
            f.write(content)

    def print_available_categories(self, code_divider: CodeDivider):
        for segment in code_divider.get_segments():
            categories = self.state.categories_for_segment(segment.id)
            print(
                f"Segment {segment.id+1}: {', '.join([category.get_name() for category in categories])}")
