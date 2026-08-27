from dataclasses import asdict, dataclass

from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit
from radon.raw import analyze as raw_analyze


@dataclass
class ReadabilityMetrics:
    """ Represents the readability metrics for a piece of code. """
    cyclomatic_complexity: int
    loc: int
    lloc: int
    sloc: int
    comments: int
    comment_blocks: int
    blank_lines: int
    single_comments: int
    halstead_h1: int
    halstead_h2: int
    halstead_n1: int
    halstead_n2: int
    halstead_vocabulary: int
    halstead_length: int
    halstead_calculated_length: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    halstead_time: float
    halstead_bugs: float
    maintainability_index: float

    def print_metrics(self):
        print(f"Cyclomatic Complexity: {self.cyclomatic_complexity}")
        print(f"Lines of Code (LOC): {self.loc}")
        print(f"Logical Lines of Code (LLOC): {self.lloc}")
        print(f"Source Lines of Code (SLOC): {self.sloc}")
        print(f"Comments: {self.comments}")
        print(f"Comment Blocks: {self.comment_blocks}")
        print(f"Blank Lines: {self.blank_lines}")
        print(f"Single Comments: {self.single_comments}")
        print(f"Distinct Operators (H1): {self.halstead_h1}")
        print(f"Distinct Operands (H2): {self.halstead_h2}")
        print(f"Total Number of Operators (N1): {self.halstead_n1}")
        print(f"Total Number of Operands (N2): {self.halstead_n2}")
        print(f"Vocabulary: {self.halstead_vocabulary}")
        print(f"Length: {self.halstead_length}")
        print(f"Calculated Length: {self.halstead_calculated_length}")
        print(f"Volume: {self.halstead_volume}")
        print(f"Difficulty: {self.halstead_difficulty}")
        print(f"Effort: {self.halstead_effort}")
        print(f"Time: {self.halstead_time} seconds")
        print(f"Bugs: {self.halstead_bugs}")
        print(f"Maintainability Index (MI): {self.maintainability_index}")

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'ReadabilityMetrics':
        return ReadabilityMetrics(**data)

class ReadabilityAnalyzer:
    def analyze_file(filepath: str) -> ReadabilityMetrics:
        """Analyze the metrics for a file

        Args:
            filepath (str): The path to the file to analyze.

        Returns:
            ReadabilityMetrics: The readability metrics for the file.
        """
        code = ""
        with open(filepath, 'r') as file:
            code = file.read()
        return ReadabilityAnalyzer.analyze_code(code)

    def analyze_code(code: str) -> ReadabilityMetrics:
        """Analyze the metrics for a piece of code
        Args:
            code (str): The code to analyze.

        Returns:
            ReadabilityMetrics: The readability metrics for the code.
        """
        # Get Cyclomatic Complexity results
        cc_results = cc_visit(code)
        # Get raw metrics (including LOC)
        raw_results = raw_analyze(code)
        # Get Maintainability Index results
        mi_results = mi_visit(code, multi=True)
        # Halstead metrics
        halstead_results = h_visit(code)

        return ReadabilityMetrics(
            cyclomatic_complexity=cc_results[0].complexity if cc_results else 1,
            loc=raw_results.loc,
            lloc=raw_results.lloc,
            sloc=raw_results.sloc,
            comments=raw_results.comments,
            comment_blocks=raw_results.multi,
            blank_lines=raw_results.blank,
            single_comments=raw_results.single_comments,
            halstead_h1=halstead_results.total.h1,
            halstead_h2=halstead_results.total.h2,
            halstead_n1=halstead_results.total.N1,
            halstead_n2=halstead_results.total.N2,
            halstead_vocabulary=halstead_results.total.vocabulary,
            halstead_length=halstead_results.total.length,
            halstead_calculated_length=round(halstead_results.total.calculated_length, 2),
            halstead_volume=round(halstead_results.total.volume, 2),
            halstead_difficulty=round(halstead_results.total.difficulty, 2),
            halstead_effort=round(halstead_results.total.effort, 2),
            halstead_time=round(halstead_results.total.time, 2),
            halstead_bugs=round(halstead_results.total.bugs, 2),
            maintainability_index=round(mi_results, 2)
        )