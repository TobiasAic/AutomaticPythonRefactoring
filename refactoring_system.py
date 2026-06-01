from pathlib import Path
from typing import List
import logging

from git_repository import GitRepository
from llm.big_pickle import BigPickle
from tree_of_thoughts.refactoring_generator import RefactoringGenerator 
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from readability_analyzer import ReadabilityAnalyzer

class RefactoringSystem:
    def __init__(self, git_repository_path: Path, files_to_refactor: List[Path], test_files: List[Path], branch_name: str):
        self.files_to_refactor = files_to_refactor
        self.test_files = test_files
        self.branch_name = branch_name

        self.git_repository = GitRepository(git_repository_path)
        self.refactoring_generator = RefactoringGenerator(BigPickle())
        self.refactoring_evaluator = RefactoringEvaluator(BigPickle())
        self.readability_analyzer = ReadabilityAnalyzer()

    def run(self, max_iterations: int = None):
        self.git_repository.create_branch(self.branch_name)

        for filepath in self.files_to_refactor:
            self.refactor_file(filepath, max_iterations=max_iterations)

    def refactor_file(self, filepath: Path, max_iterations: int = None):
        self.readability_analyzer.record_metrics(filepath.absolute())
        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.info(f"Starting refactoring process for {filepath.name}. Initial Maintainability Index: {self.readability_analyzer.metrics[filepath.absolute()][0].maintainability_index}")

        iteration = 0

        while self.is_improving(filepath):
            refactoring_suggestions = self.refactoring_generator.generate_refactorings(filepath.read_text(), count=2)

            for i, refactoring in enumerate(refactoring_suggestions):
                evaluation = self.refactoring_evaluator.evaluate(refactoring)
                refactoring.evaluation = evaluation
                refactoring.execute(filepath.absolute())
                self.git_repository.create_branch(f"suggestion_{iteration + 1}_{i + 1}")
                refactoring.commit_hash = self.git_repository.commit_changes(refactoring.evaluation.description)
                self.git_repository.go_to_previous_commit() 

            ranked_refactorings = sorted(refactoring_suggestions, key=lambda r: r.evaluation.grade if r.evaluation else 0, reverse=True)

            for refactoring in ranked_refactorings:
                print(f"Evaluation: {refactoring.evaluation.description} (Correct: {refactoring.evaluation.correct}, Grade: {refactoring.evaluation.grade})")

            if ranked_refactorings[0].evaluation and ranked_refactorings[0].evaluation.correct:
                best_refactoring = ranked_refactorings[0]
                self.git_repository.checkout_commit(best_refactoring.commit_hash)
                self.git_repository.move_branch(self.branch_name)

            self.readability_analyzer.record_metrics(filepath.absolute())
            logger.info(f"Analyzed readability metrics for {filepath.name}: MI = {self.readability_analyzer.metrics[filepath.absolute()][-1].maintainability_index}")

            iteration += 1
            if max_iterations is not None and iteration > max_iterations:
                logger.info(f"Reached maximum iterations ({max_iterations}) for {filepath.name}. Stopping refactoring process for this file.")
                break

    def is_improving(self, filepath: Path) -> bool:
        if len(self.readability_analyzer.metrics.get(filepath.absolute(), [])) < 2:
            return True # for the first iteration

        metrics_before = self.readability_analyzer.metrics[filepath.absolute()][-2]
        metrics_after = self.readability_analyzer.metrics[filepath.absolute()][-1]

        if metrics_before.maintainability_index <= metrics_after.maintainability_index:
            return True
        else:
            return False