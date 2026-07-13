import os
import json
import random

from refactoring.refactoring_storage import RefactoringStorage
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config
from tree_of_thoughts.comparison_refactoring_evaluator import ComparisonRefactoringEvaluator

refactoring_storage = RefactoringStorage(os.path.abspath("refactoring_collection/refactoring_ids.json"))
refactorings = refactoring_storage.load_refactorings()

evaluations = {}

evaluator_llm = OpenAILLM(config=big_pickle_config)
refactoring_evaluator = ComparisonRefactoringEvaluator(evaluator_llm)

completed = False

while not completed:
    sampled_refactorings = random.sample(refactorings, 5)
    refactoring_evaluator.batch_evaluate(sampled_refactorings)

    for refactoring in sampled_refactorings:
        if refactoring.commit_hash not in evaluations:
            print(f"Adding new evaluation for refactoring with commit_hash {refactoring.commit_hash}.")
            evaluations[refactoring.commit_hash] = []
        if len(evaluations[refactoring.commit_hash]) < 10 and refactoring.evaluation is not None:
            evaluations[refactoring.commit_hash].append(refactoring.evaluation.to_dict())

    print("Completed evaluation round")

    all_evaluated = True

    for refactoring in refactorings:
        if refactoring.commit_hash not in evaluations or len(evaluations[refactoring.commit_hash]) < 10:
            all_evaluated = False
            break

    if all_evaluated:
        completed = True
        print("All refactorings have been evaluated 10 times.")

with open("refactoring_collection/evaluations_comparison.json", "w") as f:
    json.dump(evaluations, f)