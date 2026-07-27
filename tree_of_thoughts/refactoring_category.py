from abc import ABC, abstractmethod
from textwrap import dedent

from refactoring.extract_method_refactoring import ExtractMethodTool
from refactoring.multi_rename_refactoring import MultiRenameTool

class RefactoringCategory(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        pass

    def get_tools(self) -> list[dict]:
        pass

class ControlFlowCategory(RefactoringCategory):
    def get_name(self):
        return "CONTROL_FLOW"

    def get_prompt(self):
        return dedent("""
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
        """).strip()

    def get_tools(self):
        return []

class MethodStructureCategory(RefactoringCategory):
    def get_name(self):
        return "METHOD_STRUCTURE"

    def get_prompt(self):
        return dedent("""
            Category: Method structure

            Look only for improvements to method structure.

            Consider:
            - Extracting a coherent block of logic into a new private helper method.
            - Splitting methods that are too long or contain multiple distinct responsibilities.
            - Removing duplicated logic by introducing a shared helper.

            Do not:
            - Change function names, parameters, or public APIs.
            """).strip() 

    def get_tools(self):
        return [ExtractMethodTool.get_description()]

class ExpressionCategory(RefactoringCategory):
    def get_name(self):
        return "EXPRESSION"

    def get_prompt(self):
        return dedent("""
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
        """).strip() 

    def get_tools(self):
        return []

class TypeDocumentationCategory(RefactoringCategory):
    def get_name(self):
        return "TYPE_DOCUMENTATION"

    def get_prompt(self):
        return dedent("""
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
        """).strip()

    def get_tools(self):
        return []

class NamingCategory(RefactoringCategory):
    def get_name(self):
        return "NAMING"

    def get_prompt(self):
        return dedent("""
            Category: Local variable naming

            Look only for bad local variable names.
            Variable names should snake_case, be descriptive, and avoid abbreviations.

            If several local variables in the same nearby block, function, or scope have weak names, prefer renaming them together in one MultiRename change instead of producing a single isolated rename.
            Only batch names when the renames are clearly related and improve readability as a group.

            Do not:
            - Rename function parameters.
            - Rename functions or classes.
            - Rename attributes.
            - Rename variables where the existing name is already clear.
            - Perform cosmetic renaming with little readability benefit.
                """).strip() 

    def get_tools(self):
        return [MultiRenameTool.get_description()]