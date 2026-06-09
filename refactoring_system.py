from pathlib import Path
import logging

from git_repository import GitRepository
from llm.big_pickle import BigPickle
from tree_of_thoughts.refactoring_generator import RefactoringGenerator 
from tree_of_thoughts.refactoring_evaluator import RefactoringEvaluator
from readability_analyzer import ReadabilityAnalyzer
from config import Config

class RefactoringSystem:
    def __init__(self, config: Config):
        self.config = config

        self.git_repository = GitRepository(config.get_absolute_git_repo_path())
        self.refactoring_generator = RefactoringGenerator(BigPickle())
        self.refactoring_evaluator = RefactoringEvaluator(BigPickle())
        self.readability_analyzer = ReadabilityAnalyzer()

    def run(self):
        self.git_repository.create_branch(self.config.branch_name)
        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.debug(f"Created and switched to branch '{self.git_repository.get_current_branch()}' for refactoring process")

        for filepath in self.config.get_absolute_file_paths():
            self.refactor_file(filepath)

    def refactor_file(self, filepath: str):
        self.readability_analyzer.record_metrics(filepath)
        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.info(f"Starting refactoring process for {Path(filepath).name}. Initial Maintainability Index: {self.readability_analyzer.metrics[filepath][0].maintainability_index}")

        iteration = 0

        while self.is_improving(filepath):
            with open(filepath, "r") as f:
                code_segment = f.read()

            refactoring_suggestions = self.refactoring_generator.generate_refactorings(code_segment, count=2)

            for i, refactoring in enumerate(refactoring_suggestions):
                evaluation = self.refactoring_evaluator.evaluate(refactoring)
                refactoring.evaluation = evaluation
                refactoring.execute(filepath)
                self.git_repository.create_branch(f"suggestion_{iteration + 1}_{i + 1}")
                refactoring.commit_hash = self.git_repository.commit_changes(refactoring.evaluation.description)
                self.git_repository.go_to_previous_commit() 

            ranked_refactorings = sorted(refactoring_suggestions, key=lambda r: r.evaluation.grade if r.evaluation else 0, reverse=True)

            for refactoring in ranked_refactorings:
                print(f"Evaluation: {refactoring.evaluation.description} (Correct: {refactoring.evaluation.correct}, Grade: {refactoring.evaluation.grade})")

            if ranked_refactorings[0].evaluation and ranked_refactorings[0].evaluation.correct:
                best_refactoring = ranked_refactorings[0]
                self.git_repository.checkout_commit(best_refactoring.commit_hash)
                self.git_repository.move_branch(self.config.branch_name)

            self.readability_analyzer.record_metrics(filepath)
            logger.info(f"Analyzed readability metrics for {Path(filepath).name}: MI = {self.readability_analyzer.metrics[filepath][0].maintainability_index}")

            iteration += 1
            if self.config.max_iterations is not None and iteration > self.config.max_iterations:
                logger.info(f"Reached maximum iterations ({self.config.max_iterations}) for {Path(filepath).name}. Stopping refactoring process for this file.")
                break

    def is_improving(self, filepath: Path) -> bool:
        if len(self.readability_analyzer.metrics.get(filepath, [])) < 2:
            return True # for the first iteration

        metrics_before = self.readability_analyzer.metrics[filepath][-2]
        metrics_after = self.readability_analyzer.metrics[filepath][-1]

        minimum_improvement = -0.05
        improvement_percentage = (metrics_after.maintainability_index - metrics_before.maintainability_index) / metrics_before.maintainability_index
        if improvement_percentage >= minimum_improvement:
            return True
        else:
            return False