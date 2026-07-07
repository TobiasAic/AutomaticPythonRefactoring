header = """
You are generating a refactoring candidate for a Python file to improve readability.

Find exactly one small refactoring from the category specified below.

The refactoring must:
- Improve readability.
- Preserve behavior exactly.
- Avoid changing public APIs.
- Avoid adding imports.
- Avoid renaming functions, parameters, or classes.
- Not repeat a refactoring already performed in the commit history.

{return_instruction}
If no meaningful refactoring exists in this category, return "NO_REFACTORING".

Prefer a real readability improvement over a cosmetic change.
"""

with_tools_return_instruction = """
Some refactorings can be done by calling a tool. If the refactoring can be done by a tool, you MUST use the tool.
If the refactoring can't be done by a tool, return the refactored in a Markdown Python code block (without line numbers):
```python
    ...some python code...
```
"""

without_tools_return_instruction = """
Return the refactored code in a Markdown Python code block (without line numbers):
```python
    ...some python code...
```
"""

control_flow = """
Category: Control flow simplification

Look only for improvements to control flow.

Consider:
- Reducing deeply nested if/else structures.
- Replacing nested conditions with early returns or guard clauses.
- Simplifying boolean expressions.
- Removing unnecessary else blocks after return/raise/continue/break.
- Combining duplicated conditional branches where behavior remains identical.

Do not:
- Change evaluation order of expressions with possible side effects.
- Change exception behavior.
"""

method_structure = """
Category: Method structure

Look only for improvements to method structure.

Consider:
- Extracting a coherent block of logic into a new private helper method.
- Splitting methods that are too long or contain multiple distinct responsibilities.
- Removing duplicated logic by introducing a shared helper.

Do not:
- Change function names, parameters, or public APIs.
"""

expression = """
Category: Expression simplification

Look only for improvements to expressions and local data flow.

Consider:
- Removing redundant temporary assignments.
- Replacing unnecessary intermediate variables with direct expressions.
- Introducing well-named local variables for complex expressions.

Do not:
- Create unreadable one-liners.
- Change evaluation order.
- Replace clear code with clever Python tricks.
"""

type_documentation = """
Category: Type/documentation improvements

Look only for missing or insufficient documentation.

Consider:
- Adding missing type hints to function signatures.
- Improving incomplete or missing method docstrings.
- Adding comments for genuinely non-obvious logic.

Do not:
- Add comments that merely repeat the code.
- Add inaccurate types.
- Add documentation where the code is already self-explanatory.

Do not add imports. Only use types already available in the file.
"""

naming = """
Category: Local variable naming

Look only for bad local variable names. 
Variable names should snake_case, be descriptive, and avoid abbreviations.

Do not:
- Rename function parameters.
- Rename functions or classes.
- Rename attributes.
- Rename variables where the existing name is already clear.
- Perform cosmetic renaming with little readability benefit.
"""

footer = """
Commit history:
{commit_history}

Python file to refactor:
{code_segment}
"""