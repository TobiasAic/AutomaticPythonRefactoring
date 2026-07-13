from pathlib import Path
import time
from datetime import timedelta
import os

from utility.git_repository import GitRepository
from llm.openai_llm import OpenAILLM
from llm.replay_llm import ReplayLLM, ReplayMode
from llm.llm_presets import big_pickle_config
from tree_of_thoughts.refactoring_generator import RefactoringGenerator 
from tree_of_thoughts.individual_refactoring_evaluator import IndividualRefactoringEvaluator
from utility.readability_analyzer import ReadabilityAnalyzer
from utility.config import Config
from utility.compiler import Compiler
from utility.pytest_tester import PytestTester
from utility.cli import CLI
from refactoring.refactoring_storage import RefactoringStorage

class RefactoringSystem:
    def __init__(self, config: Config):
        self.config = config

        self.git_repository = GitRepository(config.get_absolute_git_repo_path())
        generator_llm = ReplayLLM(config=big_pickle_config, filepath="replays/new_generator.json", mode=ReplayMode.REPLAY)
        evaluator_llm = ReplayLLM(config=big_pickle_config, filepath="replays/new_evaluator.json", mode=ReplayMode.REPLAY)
        self.refactoring_generator = RefactoringGenerator(generator_llm)
        self.refactoring_evaluator = IndividualRefactoringEvaluator(evaluator_llm)
        self.readability_analyzer = ReadabilityAnalyzer()
        self.tester = PytestTester(project_root=Path(config.get_absolute_test_root_path()), pyenv_name=config.pyenv_name)
        self.refactoring_storage = RefactoringStorage(os.path.abspath("refactoring_collection/refactoring_ids.json"))

    def run(self):
        start = time.time()
        self.git_repository.create_branch(self.config.branch_name)
        CLI.print_debug(f"Successfully created and switched to branch '{self.git_repository.get_current_branch()}'")

        for filepath in self.config.get_absolute_file_paths():
            self.refactor_file(filepath)
            self.readability_analyzer.plot_percentage_change(filepath, output_path=self.config.get_absolute_statistics_directory() + f"/{Path(filepath).stem}_readability_plot.png")

        self.readability_analyzer.save(self.config.get_absolute_statistics_directory() + "/readability_metrics.json")
        CLI.print_debug(f"Saved readability metrics to {self.config.get_absolute_statistics_directory() + '/readability_metrics.json'}")
        print(f"Finished refactoring in {self.format_timespan(time.time() - start)}")

    def refactor_file(self, filepath: str):
        test_results = self.tester.test_before() # Run tests before starting the refactoring process to establish a baseline
        print(f"Test results before refactoring: {test_results}")
        self.readability_analyzer.record_metrics(filepath)
        CLI.print_banner(f"Starting refactoring for {Path(filepath).name}", symbol="=", empty_line_count=2)

        for iteration in range(self.config.max_iterations):
            iteration_start = time.time()
            CLI.print_banner(f"Iteration {iteration + 1} - Current MI: {self.readability_analyzer.metrics[filepath][-1].maintainability_index}", symbol="-")

            with open(filepath, "r") as f:
                code_segment = f.read()

            commit_history = self.git_repository.get_commit_history()
            refactoring_suggestions = self.refactoring_generator.generate_refactorings(code_segment, filepath=filepath, commit_history=commit_history)

            self.refactoring_evaluator.batch_evaluate(refactoring_suggestions)

            for refactoring in refactoring_suggestions:
                self.refactoring_storage.save_refactoring(refactoring)

            sorted_refactorings = self.sort_refactorings_by_evaluation(refactoring_suggestions)

            self.print_refactorings(sorted_refactorings)

            if self.config.show_tree:
                self.apply_all_refactorings(filepath, iteration, sorted_refactorings) 
            else:
                self.apply_best_refactoring(filepath, sorted_refactorings)

            self.readability_analyzer.record_metrics(filepath)

            print(f"Iteration {iteration + 1} completed in {self.format_timespan(time.time() - iteration_start)}")

    def print_refactorings(self, sorted_refactorings):
        for i, refactoring in enumerate(sorted_refactorings):
            if not refactoring.evaluation:
                print(f"{i + 1}. Refactoring without evaluation")
            else:
                print(f"{i + 1}. {"Correct" if refactoring.evaluation.correct else "Incorrect"}, {refactoring.evaluation.grade}: {refactoring.evaluation.description}")

    def apply_all_refactorings(self, filepath, iteration, sorted_refactorings):
        found_best_refactoring = False
        for i, refactoring in enumerate(sorted_refactorings):
            if refactoring.evaluation is not None:
                refactoring.execute()
                self.git_repository.create_branch(f"{Path(filepath).name.replace('.py', '')}_{iteration + 1}_{i + 1}")
                self.git_repository.commit_changes(refactoring.evaluation.description)
                if not found_best_refactoring and self.validate_refactoring(filepath) and refactoring.evaluation.correct:
                    self.git_repository.move_branch(self.config.branch_name)
                    found_best_refactoring = True
                self.git_repository.go_to_previous_commit()
        self.git_repository.checkout_branch(self.config.branch_name)

    def apply_best_refactoring(self, filepath, sorted_refactorings):
        for refactoring in sorted_refactorings:
            if refactoring.evaluation and refactoring.evaluation.correct:
                if self.validate_refactoring(filepath):
                    refactoring.execute()
                    self.git_repository.commit_changes(refactoring.evaluation.description)
                    break
                else:
                    CLI.print_debug(f"Refactoring '{refactoring.evaluation.description}' failed validation. Trying next best refactoring.")
        else:
            print("No correct refactorings generated in this iteration")

    def sort_refactorings_by_evaluation(self, refactorings: list) -> list:
        return sorted(refactorings, key=lambda r: r.evaluation.sorting_value() if r.evaluation else 0, reverse=True)

    def validate_refactoring(self, filepath: str) -> bool:
        if not Compiler.try_compile_file(filepath):
            return False
        
        if self.tester.test_changed():
            return False
        
        return True
    
    def format_timespan(self, seconds: float) -> str:
        return str(timedelta(seconds=seconds))