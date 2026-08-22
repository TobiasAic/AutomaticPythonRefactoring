import time
from datetime import timedelta
from pathlib import Path

from llm.llm import LLM
from refactoring.refactoring import Refactoring
from refactoring.rope_refactoring import RopeRefactoring
from tree_of_thoughts.individual_refactoring_evaluator import (
    IndividualRefactoringEvaluator,
)
from tree_of_thoughts.refactoring_generator import RefactoringGenerator
from utility.cli import CLI
from utility.code_divider import CodeDivider
from utility.compiler import Compiler
from utility.config import Config
from utility.git_repository import GitRepository
from utility.pytest_tester import PytestTester
from utility.readability_analyzer import ReadabilityAnalyzer


class RefactoringSystem:
    def __init__(self, config: Config, llm: LLM, count: int):
        self.config = config
        self.count = count
        self.llm = llm

        self.git_repository = GitRepository(
            config.get_absolute_git_repo_path())
        self.refactoring_evaluator = IndividualRefactoringEvaluator(llm)
        self.readability_analyzer = ReadabilityAnalyzer()
        self.tester = PytestTester(
            pyenv_name=config.pyenv_name, test_file_path=config.get_absolute_test_file_path())

    def run(self):
        start = time.time()
        self.git_repository.create_branch(self.config.branch_name)

        for filepath in self.config.get_absolute_file_paths():
            self.refactor_file(filepath)
            self.readability_analyzer.plot_percentage_change(
                filepath, output_path=self.config.get_absolute_statistics_directory() + f"/{Path(filepath).stem}_readability_plot.png")

        self.readability_analyzer.save(
            self.config.get_absolute_statistics_directory() + "/readability_metrics.json")
        print(
            f"Finished refactoring in {self.format_timespan(time.time() - start)}")

    def refactor_file(self, filepath: str):
        CLI.print_banner(
            f"Starting refactoring for {Path(filepath).name}", symbol="=", empty_line_count=2)
        # Run tests before starting the refactoring process to establish a baseline
        print(f"Test results before refactoring: {self.tester.test_before()}")
        self.readability_analyzer.record_metrics(filepath)

        code = self.__read_file(filepath)
        code_divider = CodeDivider(code)
        if code_divider.get_code() != code:
            CLI.print_error(
                f"Code was incorrectly divided into {code_divider.get_number_of_segments()} segments for {filepath}.")

        self.refactoring_generators = [RefactoringGenerator(self.llm, self.count) for _ in range(code_divider.get_number_of_segments())]

        for iteration in range(self.config.max_iterations):
            iteration_start = time.time()
            CLI.print_banner(
                f"Iteration {iteration + 1}")
            self.do_iteration(filepath, code_divider)
            print(
                f"Iteration {iteration + 1} completed in {self.format_timespan(time.time() - iteration_start)}")

    def do_iteration(self, filepath: str, code_divider: CodeDivider):
        self.print_available_categories()

        for segment_id, segment in code_divider.get_segments_with_id().items():
            if len(self.refactoring_generators[segment_id].categories) > 0:
                self.refactor_segment(segment, filepath, segment_id, code_divider, self.refactoring_generators[segment_id])
            else:
                CLI.print_debug(f"No more categories available for segment {segment_id+1}. Skipping refactoring for this segment.")

    def refactor_segment(self, code_segment: str, filepath: str, segment_id: int, code_divider: CodeDivider, refactoring_generator: RefactoringGenerator):
        CLI.print_banner(
                f"Segment {segment_id + 1} - Current MI: {self.readability_analyzer.metrics[filepath][-1].maintainability_index}", symbol="-")
        commit_history = self.git_repository.get_commit_history()
        refactoring_suggestions = refactoring_generator.generate_refactorings(
            code_segment, commit_history=commit_history)

        if refactoring_suggestions == []:
            CLI.print_debug(
                f"No refactoring suggestions generated for segment in {filepath}.")
            return

        self.refactoring_evaluator.batch_evaluate(refactoring_suggestions)

        sorted_refactorings = self.sort_refactorings_by_evaluation(
            refactoring_suggestions)
        self.print_refactorings(sorted_refactorings)
        final_candidates = self.filter_refactorings(sorted_refactorings)

        self.apply_best_refactoring(filepath, segment_id, final_candidates, code_divider)

        self.readability_analyzer.record_metrics(filepath)

    def sort_refactorings_by_evaluation(self, refactorings: list) -> list:
        return sorted(refactorings, key=lambda r: r.evaluation.sorting_value() if r.evaluation else 0, reverse=True)

    def filter_refactorings(self, refactorings: list) -> list:
        filtered_refactorings = []
        for refactoring in refactorings:
            if refactoring.evaluation and refactoring.evaluation.correct:
                filtered_refactorings.append(refactoring)
        return filtered_refactorings

    def print_refactorings(self, sorted_refactorings):
        for i, refactoring in enumerate(sorted_refactorings):
            print(f"{i+1}. {self.refactoring_printable_string(refactoring)}")

    def refactoring_printable_string(self, refactoring: Refactoring) -> str:
        if isinstance(refactoring, RopeRefactoring):
            tool_name = refactoring.tool_name()
        else:
            tool_name = "no tool" 

        if not refactoring.evaluation:
            return f"no evaluation, {tool_name}"
        else:
            short_description = refactoring.evaluation.description.splitlines()[0]  # Get the first line of the description
            correct_string = "Correct" if refactoring.evaluation.correct else "Incorrect"
            return f"{correct_string}, {refactoring.evaluation.grade}, {short_description}, {tool_name}"

    def apply_best_refactoring(self, filepath, segment_id: int, sorted_refactorings: list, code_divider: CodeDivider):
        for refactoring in sorted_refactorings:
            if self.validate_refactoring(refactoring, segment_id, filepath, code_divider):
                self.apply_refactoring(refactoring, filepath, segment_id, code_divider, remember=True)
                self.git_repository.commit_changes(refactoring.evaluation.description)
                break

    def apply_refactoring(self, refactoring: Refactoring, filepath, segment_id: int, code_divider: CodeDivider, remember: bool = True):
        refactored_file = code_divider.replace_segment(segment_id, refactoring.new_code)
        self.__write_file(filepath, refactored_file)

    def validate_refactoring(self, refactoring: Refactoring, segment_id: int, filepath: str, code_divider: CodeDivider) -> bool:
        original_code = self.__read_file(filepath)
        self.apply_refactoring(refactoring, filepath, segment_id, code_divider, remember=False)

        if not Compiler.try_compile_file(filepath):
            input("Press Enter to continue...")
            self.__write_file(filepath, original_code) # Restore the original code
            CLI.print_debug(f"Refactoring '{refactoring.evaluation.description}' failed compilation.")
            return False

        tests_changed = self.tester.test_changed()
        if tests_changed:
            CLI.print_debug(f"Refactoring '{refactoring.evaluation.description}' failed tests.")
        self.__write_file(filepath, original_code) # Restore the original code
        return not tests_changed

    def format_timespan(self, seconds: float) -> str:
        return str(timedelta(seconds=seconds))

    def __read_file(self, filepath: str) -> str:
        with open(filepath, "r") as f:
            return f.read()

    def __write_file(self, filepath: str, content: str):
        with open(filepath, "w") as f:
            f.write(content)

    def print_available_categories(self):
        for i, refactoring_generator in enumerate(self.refactoring_generators):
            print(f"Segment {i+1}: {', '.join([category.get_name() for category in refactoring_generator.categories])}")