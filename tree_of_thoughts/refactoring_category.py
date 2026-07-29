from abc import ABC, abstractmethod
from textwrap import dedent

from refactoring.extract_method_refactoring import ExtractMethodTool
from refactoring.multi_rename_refactoring import MultiRenameTool
from tree_of_thoughts.refactoring_suggestion import (
    AddExplanatoryComment,
    AddTypeHints,
    ConsolidateConditionalExpression,
    DecomposeConditional,
    ExtractClass,
    ExtractFunction,
    ExtractVariable,
    ImproveMethodDocstring,
    InlineClass,
    InlineFunction,
    InlineVariable,
    PreserveWholeObject,
    RefactoringSuggestion,
    RemoveDeadCode,
    RenameVariable,
    ReplaceControlFlagWithBreak,
    ReplaceExceptionWithPrecheck,
    ReplaceLoopWithPipeline,
    ReplaceMagicLiteral,
    ReplaceNestedConditionalWithGuardClauses,
    ReplaceTempWithQuery,
    SlideStatements,
    SplitLoop,
    SplitVariable,
    SubstituteAlgorithm,
)


class RefactoringCategory(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    def get_prompt(self) -> str:
        return dedent(f"""
            Category: {self.get_name()}

            {self.get_description()}
            {self.get_refactoring_suggestions()}
        """).strip()

    @abstractmethod
    def get_tools(self) -> list[dict]:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    def get_refactoring_suggestions_string(self) -> str:
        suggestions = self.get_refactoring_suggestions()
        if not suggestions:
            return "No specific refactoring suggestions provided."
        return "\n\n".join(f"- {suggestion.get_description()}" for suggestion in suggestions)

    @abstractmethod
    def get_refactoring_suggestions(self) -> list[RefactoringSuggestion]:
        pass


class ConditionalLogicCategory(RefactoringCategory):
    def get_name(self):
        return "CONDITIONAL_LOGIC"

    def get_description(self):
        return dedent("""
            Look only for improvements to conditional logic, including the following:
        """).strip()

    def get_tools(self):
        return []

    def get_refactoring_suggestions(self):
        return [
            ConsolidateConditionalExpression,
            DecomposeConditional,
            ReplaceExceptionWithPrecheck,
            ReplaceNestedConditionalWithGuardClauses,
        ]


class ControlFlowCategory(RefactoringCategory):
    def get_name(self):
        return "CONTROL_FLOW"

    def get_description(self):
        return dedent("""
            Look only for improvements to control flow, including the following:
        """).strip()

    def get_tools(self):
        return []

    def get_refactoring_suggestions(self):
        return [
            ReplaceControlFlagWithBreak,
            ReplaceLoopWithPipeline,
            SlideStatements,
            SplitLoop,
            SubstituteAlgorithm 
        ]


class MethodStructureCategory(RefactoringCategory):
    def get_name(self):
        return "METHOD_STRUCTURE"

    def get_description(self):
        return dedent("""
            Look only for improvements to method structure, including the following:
        """).strip()

    def get_tools(self):
        return [ExtractMethodTool.get_description()]

    def get_refactoring_suggestions(self):
        return [
            ExtractFunction,
            InlineFunction,
            ReplaceTempWithQuery
        ]


class ExpressionCategory(RefactoringCategory):
    def get_name(self):
        return "EXPRESSION"

    def get_description(self):
        return dedent("""
            Look only for improvements to expressions, including the following:
        """).strip()

    def get_tools(self):
        return []

    def get_refactoring_suggestions(self):
        return [
            ExtractVariable,
            InlineVariable,
            ReplaceMagicLiteral,
            SplitVariable
        ]


class ClassStructureCategory(RefactoringCategory):
    def get_name(self):
        return "CLASS_STRUCTURE"

    def get_description(self):
        return dedent("""
            Look only for improvements to class structure, including the following:
        """).strip()

    def get_tools(self):
        return []

    def get_refactoring_suggestions(self):
        return [
            ExtractClass,
            InlineClass,
            PreserveWholeObject
        ]


class CodeQualityCategory(RefactoringCategory):
    def get_name(self):
        return "CODE_QUALITY"

    def get_description(self):
        return dedent("""
            Look only for improvements to code quality, including the following:
        """).strip()

    def get_tools(self):
        return [MultiRenameTool.get_description()]

    def get_refactoring_suggestions(self):
        return [
            RemoveDeadCode,
            RenameVariable,
            AddTypeHints,
            ImproveMethodDocstring,
            AddExplanatoryComment
        ]
