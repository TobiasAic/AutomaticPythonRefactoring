import json

from refactoring.refactoring_evaluation import RefactoringEvaluation

with open("refactoring_collection/evaluations.json", 'r') as file:
    evaluation_dicts = json.load(file)

evaluations = {}
for (uuid, evaluation_dict_list) in evaluation_dicts.items():
    evaluations[uuid] = []
    for evaluation_dict in evaluation_dict_list:
        evaluation = RefactoringEvaluation.from_dict(evaluation_dict)
        evaluations[uuid].append(evaluation) 

correctness = {}
for (uuid, evaluation_list) in evaluations.items():
    correctness[uuid] = [0,0] 
    for evaluation in evaluation_list:
        if evaluation.correct:
            correctness[uuid][1] += 1
        else:
            correctness[uuid][0] += 1

for i, (uuid, correctness_list) in enumerate(correctness.items()):
    print(f"{i+1} - {uuid}: Incorrect={correctness_list[0]}, Correct={correctness_list[1]}")

print("="*40)

grades = {}
grades_spans = []
for (uuid, evaluation_list) in evaluations.items():
    grades[uuid] = [0] * 11 
    for evaluation in evaluation_list:
        grades[uuid][evaluation.grade] += 1

for i, (uuid, grades_list) in enumerate(grades.items()):
    output = f"{i+1} - {uuid}:"
    given_grades = []
    for grade, grade_count in enumerate(grades_list):
        output += f" {grade}:{grade_count},"
        if grade_count > 0:
            given_grades.append(grade)
    print(output)
    grades_span = max(given_grades) - min(given_grades)
    grades_spans.append(grades_span)
    print(f"Grades span={grades_span}")

print()
print(f"Average grade span={sum(grades_spans)/len(grades_spans)}")
