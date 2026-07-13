import os
import json

from refactoring.refactoring_storage import RefactoringStorage
from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config
from tree_of_thoughts.comparison_refactoring_evaluator import ComparisonRefactoringEvaluator

refactoring_storage = RefactoringStorage(os.path.abspath("refactoring_collection/refactoring_ids.json"))
refactorings = refactoring_storage.load_refactorings()

evaluations = {}

evaluator_llm = OpenAILLM(config=big_pickle_config)
refactoring_evaluator = ComparisonRefactoringEvaluator(evaluator_llm)

batches = [refactorings[i:i + 5] for i in range(0, len(refactorings), 5)]

for batch in batches:
    for i in range(10):
        refactoring_evaluator.batch_evaluate(batch)

        for refactoring in batch:
            if refactoring.commit_hash not in evaluations:
                print(f"Adding new evaluation for refactoring with commit_hash {refactoring.commit_hash}.")
                evaluations[refactoring.commit_hash] = []
            if refactoring.evaluation is not None:
                evaluations[refactoring.commit_hash].append(refactoring.evaluation.to_dict())

with open("refactoring_collection/evaluations_comparison_same.json", "w") as f:
    json.dump(evaluations, f)