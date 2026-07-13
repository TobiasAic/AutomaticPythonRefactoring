import os
import json

from refactoring.refactoring_storage import RefactoringStorage
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config
from tree_of_thoughts.individual_refactoring_evaluator import IndividualRefactoringEvaluator

refactoring_storage = RefactoringStorage(os.path.abspath("refactoring_collection/refactoring_ids.json"))
refactorings = refactoring_storage.load_refactorings()

evaluations = {}

evaluator_llm = OpenAILLM(config=big_pickle_config)
refactoring_evaluator = IndividualRefactoringEvaluator(evaluator_llm)

for i in range(10):
    refactoring_evaluator.batch_evaluate(refactorings)
    for refactoring in refactorings:
        if refactoring.commit_hash not in evaluations:
            print(f"Adding new evaluation for refactoring with commit_hash {refactoring.commit_hash}.")
            evaluations[refactoring.commit_hash] = []
        evaluations[refactoring.commit_hash].append(refactoring.evaluation.to_dict())
    print(f"Completed evaluation round {i + 1}")

with open("refactoring_collection/evaluations.json", "w") as f:
    json.dump(evaluations, f)