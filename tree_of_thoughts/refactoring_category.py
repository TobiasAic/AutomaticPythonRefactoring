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


class RefactoringCategory:
    def __init__(
        self,
        name: str,
        description: str,
        tools: list[dict] | None = None,
        refactoring_suggestions: list[type[RefactoringSuggestion]] | None = None,
    ):
        self._name = name
        self._description = description
        self._tools = tools or []
        self._refactoring_suggestions = refactoring_suggestions or []

    def get_name(self) -> str:
        return self._name

    def get_prompt(self) -> str:
        return dedent(f"""
            Category: {self.get_name()}

            {self.get_description()}
            {self.get_refactoring_suggestions_string()}
        """).strip()

    def get_tools(self) -> list[dict]:
        return self._tools

    def get_description(self) -> str:
        return self._description

    def get_refactoring_suggestions_string(self) -> str:
        suggestions = self.get_refactoring_suggestions()
        if not suggestions:
            return "No specific refactoring suggestions provided."
        return "\n\n".join(f"- {suggestion.get_description()}" for suggestion in suggestions)

    def get_refactoring_suggestions(self) -> list[type[RefactoringSuggestion]]:
        return self._refactoring_suggestions


CONDITIONAL_LOGIC = RefactoringCategory(
    name="CONDITIONAL_LOGIC",
    description=dedent("""
        Look only for improvements to conditional logic, including the following:
    """).strip(),
    refactoring_suggestions=[
        ConsolidateConditionalExpression,
        DecomposeConditional,
        ReplaceExceptionWithPrecheck,
        ReplaceNestedConditionalWithGuardClauses,
    ],
)

CONTROL_FLOW = RefactoringCategory(
    name="CONTROL_FLOW",
    description=dedent("""
        Look only for improvements to control flow, including the following:
    """).strip(),
    refactoring_suggestions=[
        ReplaceControlFlagWithBreak,
        ReplaceLoopWithPipeline,
        SlideStatements,
        SplitLoop,
        SubstituteAlgorithm,
    ],
)

METHOD_STRUCTURE = RefactoringCategory(
    name="METHOD_STRUCTURE",
    description=dedent("""
        Look only for improvements to method structure, including the following:
    """).strip(),
    tools=[ExtractMethodTool.get_description()],
    refactoring_suggestions=[
        ExtractFunction,
        InlineFunction,
        ReplaceTempWithQuery,
    ],
)

EXPRESSION = RefactoringCategory(
    name="EXPRESSION",
    description=dedent("""
        Look only for improvements to expressions, including the following:
    """).strip(),
    refactoring_suggestions=[
        ExtractVariable,
        InlineVariable,
        ReplaceMagicLiteral,
        SplitVariable,
    ],
)

CLASS_STRUCTURE = RefactoringCategory(
    name="CLASS_STRUCTURE",
    description=dedent("""
        Look only for improvements to class structure, including the following:
    """).strip(),
    refactoring_suggestions=[
        ExtractClass,
        InlineClass,
        PreserveWholeObject,
    ],
)

CODE_QUALITY = RefactoringCategory(
    name="CODE_QUALITY",
    description=dedent("""
        Look only for improvements to code quality, including the following:
    """).strip(),
    tools=[MultiRenameTool.get_description()],
    refactoring_suggestions=[
        RemoveDeadCode,
        RenameVariable,
        AddTypeHints,
        ImproveMethodDocstring,
        AddExplanatoryComment,
    ],
)
